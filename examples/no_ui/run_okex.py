import os
import json
import traceback
from random import randint
from time import sleep
from datetime import datetime, time, timedelta
from logging import INFO
from copy import copy
from dateutil.relativedelta import relativedelta

from vnpy.event import EventEngine
from vnpy.trader.setting import SETTINGS
from vnpy.trader.engine import MainEngine

from vnpy.trader.utility import load_json
from vnpy.gateway.okex import OkexGateway
from vnpy.gateway.okex.okex_gateway import OkexWebsocketApi
from vnpy.app.cta_strategy import CtaStrategyApp
from vnpy.app.cta_strategy.base import EVENT_CTA_LOG
from vnpy.trader.object import (
    Offset,
    Direction,
    OrderType,
    Status,
    OrderType,
    TickData,
    OrderData,
    TradeData,
    SubscribeRequest,
    OrderRequest,
    CancelRequest,
    HistoryRequest,
)


SETTINGS["log.active"] = True
SETTINGS["log.level"] = INFO
SETTINGS["log.console"] = True


class CustomOkexWebsocketApi(OkexWebsocketApi):

    def __init__(self, gateway):
        super(CustomOkexWebsocketApi, self).__init__(gateway)
        self.subscribe_reqs = set()
        self.re_subscribe = False

    def subscribe(self, req: SubscribeRequest):
        super(CustomOkexWebsocketApi, self).subscribe(req)
        self.subscribe_reqs.add((req.symbol, req.exchange))

    def on_login(self, data: dict):
        super(CustomOkexWebsocketApi, self).on_login(data)
        if self.re_subscribe:
            for (sym, ex) in self.subscribe_reqs:
                self.subscribe(SubscribeRequest(symbol=sym, exchange=ex))

        self.re_subscribe = False

    def on_disconnected(self):
        """"""
        super(CustomOkexWebsocketApi, self).on_disconnected()
        self.re_subscribe = True


class FakeOkexGateway(OkexGateway):

    def __init__(self, event_engine):
        super(FakeOkexGateway, self).__init__(event_engine)
        self.ws_api = CustomOkexWebsocketApi(self)

        self._orders = dict()
        self.datetime = datetime.now()
        self.queried_histories = dict()

    def send_order(self, req: OrderRequest):
        orderid = "{}_{}_{:06d}".format(req.symbol, self.datetime.strftime("%Y%m%d%H%M"), randint(1, 999999))
        order: OrderData = req.create_order_data(orderid, self.gateway_name)
        order.time = self.datetime.strftime("%T")
        self.on_order(copy(order))
        self._orders[orderid] = order
        return order.vt_orderid

    def cancel_order(self, req: CancelRequest):
        if req.orderid in self._orders:
            order: OrderData = self._orders[req.orderid]
            order.time = self.datetime.strftime("%T")
            order.status = Status.CANCELLED
            self.on_order(copy(order))
            self._orders.pop(req.orderid)

    def on_tick(self, tick: TickData):
        """"""
        super(FakeOkexGateway, self).on_tick(tick)
        self.datetime = tick.datetime

        if not (isinstance(tick.last_price, float)
                and isinstance(tick.bid_price_1, float)
                and isinstance(tick.ask_price_1, float)):
            return

        limit_long_cross_price = tick.ask_price_1
        limit_short_cross_price = tick.bid_price_1

        closed_orders = []
        for orderid, o in self._orders.items():
            if o.exchange != tick.exchange or o.symbol != tick.symbol:
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
                    self.sim_deal(orderid, o, tick, o.volume)
                    closed_orders.append(orderid)
            elif o.type == OrderType.STOP:
                long_cross = (
                    tick.last_price > 0
                    and o.direction == Direction.LONG
                    and o.price <= tick.last_price
                )
                short_cross = (
                    tick.last_price > 0
                    and o.direction == Direction.SHORT
                    and o.price >= tick.last_price
                )
                if long_cross or short_cross:
                    self.sim_deal(orderid, o, tick, o.volume)
                    closed_orders.append(orderid)

        for orderid in closed_orders:
            if orderid in self._orders:
                self._orders.pop(orderid)

    def sim_deal(self, orderid, o, tick, volume):
        o.time = tick.datetime.strftime("%T")
        o.status = Status.ALLTRADED
        o.traded = o.volume
        self.on_order(copy(o))

        tradeid = f'DIGIT_{o.orderid}'
        trade = TradeData(
            symbol=tick.symbol,
            exchange=tick.exchange,
            orderid=orderid,
            tradeid=tradeid,
            direction=o.direction,
            offset=o.offset,
            price=tick.last_price if tick.last_price > 0 else (tick.bid_price_1 + tick.ask_price_1) / 2,
            volume=volume,
            time=tick.datetime.strftime("%T"),
            gateway_name=self.gateway_name,
        )
        self.on_trade(trade)

    def query_history(self, req: HistoryRequest):
        if req.vt_symbol not in self.queried_histories:
            history_data = super(FakeOkexGateway, self).query_history(req)
            self.queried_histories[req.vt_symbol] = history_data
        return self.queried_histories[req.vt_symbol]


def main():
    SETTINGS["log.file"] = True

    event_engine = EventEngine()
    main_engine = MainEngine(event_engine)
    main_engine.add_gateway(FakeOkexGateway)
    cta_engine = main_engine.add_app(CtaStrategyApp)
    main_engine.write_log("主引擎创建成功")

    log_engine = main_engine.get_engine("log")
    event_engine.register(EVENT_CTA_LOG, log_engine.process_log_event)
    main_engine.write_log("注册日志事件监听")

    connect_setting = load_json('connect_okex.json')
    main_engine.connect(connect_setting, "OKEX")
    main_engine.write_log("连接 OKEx 接口")

    sleep(5)

    cta_engine.init_engine()
    main_engine.write_log("CTA策略初始化完成")

    cta_engine.init_all_strategies()
    n_initialized = 0
    while n_initialized < len(cta_engine.strategies):
        sleep(10.0)
        n_initialized = cta_engine.n_inited.value
        main_engine.write_log("{}/{} initialized".format(
            n_initialized,
            len(cta_engine.strategies)
        ))
    main_engine.write_log("CTA策略全部初始化")

    cta_engine.start_all_strategies()
    main_engine.write_log("CTA策略全部启动")

    while True:
        sleep(1)


if __name__ == "__main__":
    main()
