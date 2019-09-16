"""TuShare Gateway"""

import sys
import time
import tushare as ts
from copy import copy
from datetime import datetime, timedelta
from threading import Lock

from vnpy.event import Event
from vnpy.api.rest import Request, RestClient
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


class TushareGateway(BaseGateway):
    """
    VN Trader Gateway for Tushare.
    """
    datetime: datetime = None
    orderid_counter = 0

    default_setting = {
        "Token": ""
    }

    exchanges = [Exchange.BITMEX, Exchange.OKEX, Exchange.BITFINEX, Exchange.BINANCE]

    def __init__(self, event_engine):
        """Constructor"""
        super(TushareGateway, self).__init__(event_engine, "TUSHARE")
        event_engine.register(EVENT_TIMER, self.process_timer_event)
        self.ts_api = None
        self._subscribed = set()
        self._orders = dict()
        self.orderid_counter_lock = Lock()

    def _new_order_id(self, vt_symbol):
        with self.orderid_counter_lock:
            self.orderid_counter += 1
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            return '%s_%s_%d' % (vt_symbol, timestamp, self.orderid_counter)

    def connect(self, setting: dict):
        if self.ts_api is None:
            token = setting["Token"]
            self.ts_api = ts.pro_api(token)

    def subscribe(self, req: SubscribeRequest):
        """"""
        if req.vt_symbol not in self._subscribed:
            self._subscribed.add(req.vt_symbol)

    def send_order(self, req: OrderRequest):
        orderid = self._new_order_id(req.vt_symbol)
        order: OrderData = req.create_order_data(orderid, self.gateway_name)
        if self.datetime:
            order.time = self.datetime.strftime("%T")
        self.on_order(copy(order))
        self._orders[orderid] = order
        return order.vt_orderid

    def cancel_order(self, req: CancelRequest):
        if req.orderid in self._orders:
            order: OrderData = self._orders[req.orderid]
            if self.datetime:
                order.time = self.datetime.strftime("%T")
            order.status = Status.CANCELLED
            self.on_order(copy(order))
            self._orders.pop(req.orderid)

    def on_bar(self, bar: BarData):
        self.datetime = bar.datetime

        time_str = bar.datetime.strftime('%F %T.000')
        print("{} 1MIN {} {:.2f} {}".format(time_str, bar.symbol, bar.close_price, bar.volume))

        limit_long_cross_price = bar.low_price
        limit_short_cross_price = bar.high_price
        stop_long_cross_price = bar.high_price
        stop_short_cross_price = bar.low_price

        closed_orders = []
        for orderid, o in self._orders.items():
            if o.vt_symbol != bar.vt_symbol:
                continue

            if o.status == Status.SUBMITTING:
                o.status = Status.NOTTRADED
                o.time = self.datetime.strftime('%T')
                self.on_order(copy(o))

            if not o.is_active():
                closed_orders.append(orderid)
                continue

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
                    closed_orders.append(orderid)
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
                    closed_orders.append(orderid)

        for orderid in closed_orders:
            self._orders.pop(orderid)

    def on_deal(self, orderid, o: OrderData, bar: BarData, volume):
        o.time = bar.datetime.strftime("%T")
        o.status = Status.ALLTRADED
        o.traded = o.volume
        self.on_order(copy(o))

        tradeid = 'TRADE_{}'.format(o.vt_orderid)
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

    def process_timer_event(self, event: Event):
        with self.orderid_counter_lock:
            self.orderid_counter = 0

        for instrument in self._subscribed:
            exchange, symbol = instrument.lower().split('.')

    def query_history(self, req: HistoryRequest):
        self.write_log("QUERY HISTORY")

    def query_account(self):
        self.write_log("QUERY ACCOUNT")

    def query_position(self):
        self.write_log("QUERY POSITION")

    def close(self):
        self.write_log("CLOSE")
