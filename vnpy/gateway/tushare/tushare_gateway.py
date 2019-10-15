"""TuShare Gateway"""

import sys
import time
import pandas as pd
import tushare as ts
from copy import copy
from datetime import datetime, timedelta
from threading import Lock, Thread
from time import sleep

from vnpy.event import Event
from vnpy.trader.event import EVENT_TIMER
from vnpy.trader.constant import (
    Direction,
    Exchange,
    OrderType,
    Product,
    Status,
    Offset,
    Interval
)
from vnpy.trader.gateway import BaseGateway
from vnpy.trader.object import (
    TickData,
    OrderData,
    TradeData,
    PositionData,
    AccountData,
    ContractData,
    BarData,
    OrderRequest,
    CancelRequest,
    SubscribeRequest,
    HistoryRequest
)
from vnpy.app.cta_strategy.backtesting import BacktestingEngine
from requests import exceptions as requests_exceptions


EXCHANGE_NAME2VT = {
    'okex': Exchange.OKEX,
}

INTERVAL_VT2TS = {
    Interval.MINUTE: "1min",
    Interval.DAILY: "daily",
}

CONTRACT_INFO = {
    'future_okex/btc_usdt': {
        'tickSize': 0.01,
        "lotSize": 1,
    },
    'future_okex/bch_usdt': {
        'tickSize': 0.01,
        "lotSize": 1,
    },
    'future_okex/ltc_usdt': {
        'tickSize': 0.001,
        "lotSize": 1,
    },
    'future_okex/eth_usdt': {
        'tickSize': 0.001,
        "lotSize": 1,
    },
    'future_okex/eos_usdt': {
        'tickSize': 0.001,
        "lotSize": 1,
    },
}


class TushareGateway(BaseGateway):
    """
    VN Trader Gateway for Tushare.
    """
    default_setting = {
        "Token": ""
    }

    exchanges = [Exchange.OKEX]

    token = ''
    rt_datetime: datetime = None
    orderid_counter = 0
    initialized = False

    def __init__(self, event_engine):
        """Constructor"""
        super(TushareGateway, self).__init__(event_engine, "TUSHARE")
        self.ts_api = None
        self._subscribed = dict()
        self._orders = dict()
        self.orderid_counter_lock = Lock()
        self.orders_lock = Lock()
        self.thread = Thread(target=self.data_thread)

    def data_thread(self):
        while True:
            if not self.initialized:
                sleep(1.0)
                continue
            
            for it in self._subscribed.values():
                self.write_log(f"下载 {it['symbol']} {it['datetime'].date()} 的数据")
                try:
                    df = self.ts_api.coin_mins(
                        exchange='future_%s' % it['exchange'].value.lower(),
                        symbol=it['symbol'].lower(),
                        trade_date=it['datetime'].strftime('%Y%m%d'),
                        freq='1min',
                        fields='date,open,high,low,close,vol,contract_type'
                    )
                    if len(df) == 0:
                        sleep(1.0)
                    df['datetime'] = pd.to_datetime(df.date)
                    df.set_index('datetime', inplace=True)
                    df = df[df.contract_type == 'this_week']
                    it['data'] = df
                    it['iter'] = df.iterrows()
                except requests_exceptions.ConnectionError:
                    self.ts_api = ts.pro_api(self.token)
                    self.write_log("Connection Error, 重启 tushare API")
                    continue
                except requests_exceptions.ConnectTimeout:
                    self.ts_api = ts.pro_api(self.token)
                    self.write_log("Connection Timeout, 重启 tushare API")
                    continue
                except requests_exceptions.ReadTimeout:
                    self.ts_api = ts.pro_api(self.token)
                    self.write_log("Read Timeout, 重启 tushare API")
                    continue

            n_iter = len(self._subscribed)
            while n_iter > 0:
                n_iter = len(self._subscribed)
                for it in self._subscribed.values():
                    if 'iter' not in it:
                        n_iter -= 1
                        continue

                    try:
                        t, row = next(it['iter'])
                    except StopIteration:
                        n_iter -= 1
                        del it['iter']
                        continue

                    if t > self.rt_datetime:
                        self.rt_datetime = t

                    self.emit_tick(it, t, row)
                    self.emit_bar(it, t, row)
                    it['datetime'] = t + timedelta(minutes=1)

                sleep(0.25)

            sleep(30.0)

    def emit_tick(self, it, dt, row):
        tick = TickData(
            symbol=it['symbol'],
            exchange=it['exchange'],
            name=it['symbol'],
            datetime=dt - timedelta(seconds=50),
            gateway_name=self.gateway_name,
            last_price=row.open,
        )
        self.on_tick(copy(tick))

        tick.last_price = row.high
        tick.datetime = dt - timedelta(seconds=35)
        self.on_tick(copy(tick))

        tick.last_price = row.low
        tick.datetime = dt - timedelta(seconds=10)
        self.on_tick(copy(tick))

        tick.last_price = row.close
        tick.datetime = dt
        self.on_tick(copy(tick))

    def emit_bar(self, it, dt, row):
        bar = BarData(
            symbol=it['symbol'],
            exchange=it['exchange'],
            datetime=dt,
            interval=Interval.MINUTE,
            volume=row["vol"],
            open_price=row["open"],
            high_price=row["high"],
            low_price=row["low"],
            close_price=row["close"],
            gateway_name=self.gateway_name
        )
        self.on_bar(bar)

    def _new_order_id(self, vt_symbol):
        with self.orderid_counter_lock:
            self.orderid_counter += 1
            timestamp = self.rt_datetime.strftime('%Y%m%d_%H%M')
            return '%s_%s_%d' % (vt_symbol, timestamp, self.orderid_counter)

    def connect(self, setting: dict):
        if self.ts_api is None:
            self.token = setting["Token"]
            self.ts_api = ts.pro_api(self.token)
            self.write_log("Tushare API 启动成功")

            for ex in self.exchanges:
                df = self.ts_api.coinpair(exchange=f'future_{ex.value.lower()}')
                for _, row in df.iterrows():
                    contract_key = f"{row['exchange']}/{row['exchange_pair']}"
                    if contract_key not in CONTRACT_INFO:
                        continue

                    info = CONTRACT_INFO[contract_key]

                    contract = ContractData(
                        symbol=row["ts_pair"].upper(),
                        exchange=ex,
                        name=row['exchange_pair'].upper(),
                        product=Product.FUTURES,
                        pricetick=info["tickSize"],
                        size=info["lotSize"],
                        stop_supported=True,
                        net_position=True,
                        history_data=True,
                        gateway_name=self.gateway_name,
                    )
                    self.on_contract(contract)

            self.thread.start()

    def subscribe(self, req: SubscribeRequest):
        if req.vt_symbol not in self._subscribed:
            self._subscribed[req.vt_symbol] = {
                'exchange': req.exchange,
                'symbol': req.symbol,
                'datetime': self.rt_datetime,
                'data': pd.DataFrame(),
            }

    def send_order(self, req: OrderRequest):        
        orderid = self._new_order_id(req.vt_symbol)
        order: OrderData = req.create_order_data(orderid, self.gateway_name)
        order.time = self.rt_datetime.strftime("%T")
        order.status = Status.SUBMITTING
        self.on_order(copy(order))
        with self.orders_lock:
            self._orders[orderid] = order
        return order.vt_orderid

    def cancel_order(self, req: CancelRequest):
        if req.orderid in self._orders:
            order: OrderData = self._orders[req.orderid]
            order.time = self.rt_datetime.strftime("%T")
            order.status = Status.CANCELLED
            self.on_order(copy(order))

        with self.orders_lock:
            self._orders = {orderid: o for orderid, o in self._orders.items() if o.is_active()}

    def on_bar(self, bar: BarData):
        limit_long_cross_price = bar.low_price
        limit_short_cross_price = bar.high_price
        stop_long_cross_price = bar.high_price
        stop_short_cross_price = bar.low_price

        with self.orders_lock:
            for orderid, o in self._orders.items():
                if o.vt_symbol != bar.vt_symbol:
                    continue

                if not o.is_active():
                    continue

                if o.status == Status.SUBMITTING:
                    o.status = Status.NOTTRADED
                    o.time = bar.datetime.strftime('%T')
                    self.on_order(copy(o))

                if o.type == OrderType.LIMIT:
                    long_cross = (
                        limit_long_cross_price > 0
                        and o.direction == Direction.LONG 
                        and o.price >= limit_long_cross_price 
                    )
                    short_cross = (
                        limit_short_cross_price > 0
                        and o.price <= limit_short_cross_price 
                        and o.direction == Direction.SHORT 
                    )
                    if long_cross or short_cross:
                        self.on_deal(orderid, o, bar, o.volume)
                elif o.type == OrderType.STOP:
                    long_cross = (
                        o.direction == Direction.LONG 
                        and o.price <= stop_long_cross_price
                    )
                    short_cross = (
                        o.direction == Direction.SHORT 
                        and o.price >= stop_short_cross_price
                    )
                    if long_cross or short_cross:
                        self.on_deal(orderid, o, bar, o.volume)

    def on_deal(self, orderid, o: OrderData, bar: BarData, volume):
        o.time = bar.datetime.strftime("%T")
        o.status = Status.ALLTRADED
        o.traded = o.volume
        self.on_order(copy(o))

        tradeid = 'DIGIT_{}'.format(o.orderid)
        trade = TradeData(
            symbol=bar.symbol,
            exchange=bar.exchange,
            orderid=orderid,
            tradeid=tradeid,
            direction=o.direction,
            offset=o.offset,
            price=bar.close_price,
            volume=volume,
            time=o.time,
            gateway_name=self.gateway_name,
        )
        self.on_trade(trade)

    def query_history(self, req: HistoryRequest):
        self.write_log(f"准备下载 {req.symbol} - {req.interval.value} 从 {req.start} 到 {req.end} 的历史数据")
        trade_date = req.start

        history = []
        while True:
            df = self.ts_api.coin_mins(
                # exchange='future_%s' % req.exchange.value.lower(),
                exchange=req.exchange.value.lower(),
                symbol=req.symbol.lower(),
                trade_date=trade_date.strftime('%Y%m%d'),
                freq=INTERVAL_VT2TS[req.interval],
                # fields='date,open,high,low,close,vol,contract_type')
                fields='date,open,high,low,close,vol')

            # Break if total data count less than 750 (latest date collected)
            if len(df) == 0:
                break

            # if req.exchange == Exchange.OKEX:
            #     df = df[df.contract_type == 'this_week']
            # elif req.exchange == Exchange.BITMEX:
            #     df = df[df.contract_type == 'monthly']

            begin, end = None, None
            for _, row in df.iterrows():
                dt = datetime.strptime(row["date"], "%Y-%m-%d %H:%M:%S")
                if begin is None:
                    begin = dt
                end = dt
                bar = BarData(
                    symbol=req.symbol,
                    exchange=req.exchange,
                    datetime=dt,
                    interval=req.interval,
                    volume=row['vol'],
                    open_price=row["open"],
                    high_price=row["high"],
                    low_price=row["low"],
                    close_price=row["close"],
                    gateway_name=self.gateway_name
                )
                history.append(bar)

            msg = f"获取历史数据成功，{req.symbol} - {req.interval.value}，{begin} - {end}"
            self.write_log(msg)

            # Update start time
            trade_date += timedelta(hours=24)

            if req.end and trade_date > req.end:
                break

        return history

    def query_account(self):
        self.write_log("QUERY ACCOUNT")

    def query_position(self):
        self.write_log("QUERY POSITION")

    def close(self):
        self.write_log("CLOSE")
