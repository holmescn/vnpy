import os
import json
from uuid import uuid1
from time import sleep
from datetime import datetime, time
from logging import INFO
from copy import copy

from vnpy.event import EventEngine
from vnpy.trader.setting import SETTINGS
from vnpy.trader.engine import MainEngine

from vnpy.gateway.bitmex import BitmexGateway
from vnpy.app.cta_strategy import CtaStrategyApp
from vnpy.app.cta_strategy.base import EVENT_CTA_LOG
from vnpy.app.cta_strategy.base import Offset, Direction, OrderType
from vnpy.trader.object import (
    Status,
    OrderType,
    TickData,
    OrderData,
    TradeData,
    OrderRequest,
    CancelRequest,
)


SETTINGS["log.active"] = True
SETTINGS["log.level"] = INFO
SETTINGS["log.console"] = True
SETTINGS["database.database"] = "D:\\database-0.sqlite"

class SimBitMEXGateway(BitmexGateway):

    def __init__(self, event_engine):
        super(SimBitMEXGateway, self).__init__(event_engine)
        self._orders = dict()
        self.datetime = None

    def send_order(self, req: OrderRequest):
        orderid = str(uuid1())
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

    def on_tick(self, tick: TickData):
        """"""
        super(SimBitMEXGateway, self).on_tick(tick)
        self.datetime = tick.datetime

        print("{} TICK {} {:.2f} {:.2f} {:.2f} {}".format(tick.datetime.strftime('%F %T.%f'), tick.symbol, tick.bid_price_1, tick.last_price, tick.ask_price_1, tick.volume))

        limit_long_cross_price = tick.ask_price_1
        limit_short_cross_price = tick.bid_price_1

        closed_orders = []
        for orderid, o in self._orders.items():
            if o.exchange != tick.exchange or o.symbol != tick.symbol:
                continue

            if o.status == Status.SUBMITTING:
                o.status = Status.NOTTRADED
                o.tick = self.datetime.strftime('%T')
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
            self._orders.pop(orderid)

    def sim_deal(self, orderid, o, tick, volume):
        o.time = tick.datetime.strftime("%T")
        o.status = Status.ALLTRADED
        o.traded = o.volume
        self.on_order(copy(o))

        tradeid = str(uuid1())
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


def main():
    SETTINGS["log.file"] = True

    event_engine = EventEngine()
    main_engine = MainEngine(event_engine)
    main_engine.add_gateway(SimBitMEXGateway)
    cta_engine = main_engine.add_app(CtaStrategyApp)
    main_engine.write_log("主引擎创建成功")

    log_engine = main_engine.get_engine("log")
    event_engine.register(EVENT_CTA_LOG, log_engine.process_log_event)
    main_engine.write_log("注册日志事件监听")

    with open('./.vntrader/connect_bitmex_real.json', 'r', encoding='utf-8') as f:
        connect_setting = json.load(f)

    main_engine.connect(connect_setting, "BITMEX")
    main_engine.write_log("连接 BITMEX 接口")

    sleep(3)

    cta_engine.init_engine()
    main_engine.write_log("CTA策略初始化完成")

    cta_engine.init_all_strategies()
    sleep(60)   # Leave enough time to complete strategy initialization
    main_engine.write_log("CTA策略全部初始化")

    cta_engine.start_all_strategies()
    main_engine.write_log("CTA策略全部启动")

    while True:
        sleep(1)


if __name__ == "__main__":
    main()
