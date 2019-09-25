import multiprocessing
import random
import importlib
import os
import traceback
import numpy as np
import pandas as pd
import tushare as ts
import requests.exceptions as requests_exceptions
from vnpy.app.cta_strategy import strategies
from time import sleep

from collections import defaultdict
from datetime import date, datetime, timedelta
from typing import Callable
from itertools import product
from time import time
from pandas import DataFrame
from pathlib import Path
from typing import Any, Callable
from datetime import datetime, timedelta
from threading import Thread
from queue import Queue, Empty
from copy import copy

from vnpy.trader.object import OrderData, TradeData, BarData, TickData
from vnpy.trader.utility import round_to
from vnpy.app.cta_strategy.base import (
    APP_NAME,
    EVENT_CTA_LOG,

    BacktestingMode,
    EngineType,
    STOPORDER_PREFIX,
    StopOrder,
    StopOrderStatus,
)
from vnpy.event import Event, EventEngine
from vnpy.trader.engine import BaseEngine, MainEngine
from vnpy.trader.object import (
    OrderRequest,
    SubscribeRequest,
    HistoryRequest,
    LogData,
    TickData,
    BarData,
    ContractData
)
from vnpy.trader.constant import (
    Direction, 
    OrderType, 
    Interval, 
    Exchange, 
    Offset, 
    Status
)
from vnpy.trader.utility import load_json, save_json, extract_vt_symbol, round_to
from vnpy.trader.database import database_manager
from vnpy.trader.rqdata import rqdata_client
from vnpy.app.cta_strategy.converter import OffsetConverter
from vnpy.app.cta_strategy.template import CtaTemplate


STOP_STATUS_MAP = {
    Status.SUBMITTING: StopOrderStatus.WAITING,
    Status.NOTTRADED: StopOrderStatus.WAITING,
    Status.PARTTRADED: StopOrderStatus.TRIGGERED,
    Status.ALLTRADED: StopOrderStatus.TRIGGERED,
    Status.CANCELLED: StopOrderStatus.CANCELLED,
    Status.REJECTED: StopOrderStatus.CANCELLED
}

class TushareEngine(BaseEngine):
    engine_type = EngineType.BACKTESTING
    gateway_name = "TUSHARE"

    setting_filename = "tushare_strategy_setting.json"

    def __init__(self, main_engine: MainEngine, event_engine: EventEngine):
        super(TushareEngine, self).__init__(
            main_engine, event_engine, APP_NAME
        )

        self.strategy_setting = {}  # strategy_name: dict

        self.classes = {}           # class_name: stategy_class
        self.strategies = {}        # strategy_name: strategy

        self.symbol_strategy_map = defaultdict(list)  # vt_symbol: strategy list
        self.orderid_strategy_map = {}  # vt_orderid: strategy
        self.strategy_orderid_map = defaultdict(set)  # strategy_name: orderid list

        self.vt_tradeids = set()    # for filtering duplicate trade

        self.offset_converter = OffsetConverter(self.main_engine)

        self.start = None
        self.mode = BacktestingMode.BAR

        self.bar: BarData = None
        self.datetime = None
        self.callback = None
        self.strategy = None
        self.symbol = None
        self.exchange = Exchange.OKEX
        self.pricetick = 0.01
        self.vt_symbol = None

        self.stop_order_count = 0
        self.active_stop_orders = {}

        self.limit_order_count = 0
        self.active_limit_orders = {}

        setting = load_json('connect_tushare.json')
        self.token = setting['Token']
        self.ts_api = ts.pro_api(self.token)

    def init_engine(self):
        self.load_strategy_class()
        self.load_strategy_setting()
        self.write_log("CTA策略引擎初始化成功")

    def load_strategy_class(self):
        """
        Load strategy class from source code.
        """
        path1 = Path(strategies.__file__).parent
        self.load_strategy_class_from_folder(
            path1, "vnpy.app.cta_strategy.strategies")

        path2 = Path.cwd().joinpath("strategies")
        self.load_strategy_class_from_folder(path2, "strategies")

    def load_strategy_class_from_folder(self, path: Path, module_name: str = ""):
        """
        Load strategy class from certain folder.
        """
        for _, _, filenames in os.walk(str(path)):
            for filename in filenames:
                if filename.endswith(".py"):
                    strategy_module_name = ".".join(
                        [module_name, filename.replace(".py", "")])
                    self.load_strategy_class_from_module(strategy_module_name)

    def load_strategy_class_from_module(self, module_name: str):
        """
        Load strategy class from module file.
        """
        try:
            module = importlib.import_module(module_name)

            for name in dir(module):
                value = getattr(module, name)
                if (isinstance(value, type) and issubclass(value, CtaTemplate) and value is not CtaTemplate):
                    self.classes[value.__name__] = value
        except:  # noqa
            msg = f"策略文件{module_name}加载失败，触发异常：\n{traceback.format_exc()}"
            self.write_log(msg)

    def load_strategy_setting(self):
        """
        Load setting file.
        """
        self.strategy_setting = load_json(self.setting_filename)

        for strategy_name, strategy_config in self.strategy_setting.items():
            self.add_strategy(
                strategy_config["class_name"], 
                strategy_name,
                strategy_config["vt_symbol"], 
                strategy_config["setting"]
            )

    def add_strategy(
        self, class_name: str, strategy_name: str, vt_symbol: str, setting: dict
    ):
        """
        Add a new strategy.
        """
        if strategy_name in self.strategies:
            self.write_log(f"创建策略失败，存在重名{strategy_name}")
            return

        strategy_class = self.classes.get(class_name, None)
        if not strategy_class:
            self.write_log(f"创建策略失败，找不到策略类{class_name}")
            return

        strategy: CtaTemplate = strategy_class(self, strategy_name, vt_symbol, setting)
        self.strategies[strategy_name] = strategy

        # Add vt_symbol to strategy map.
        strategies = self.symbol_strategy_map[vt_symbol]
        strategies.append(strategy)

        # Update to setting file.
        self.update_strategy_setting(strategy_name, setting)

    def update_strategy_setting(self, strategy_name: str, setting: dict):
        """
        Update setting file.
        """
        strategy = self.strategies[strategy_name]

        self.strategy_setting[strategy_name] = {
            "class_name": strategy.__class__.__name__,
            "vt_symbol": strategy.vt_symbol,
            "setting": setting,
        }
        save_json(self.setting_filename, self.strategy_setting)

    def init_all_strategies(self):
        """
        """
        for strategy_name in self.strategies.keys():
            self.init_strategy(strategy_name)

    def init_strategy(self, strategy_name: str):
        """
        Init a strategy.
        """ 
        strategy = self.strategies[strategy_name]

        if strategy.inited:
            self.write_log(f"{strategy_name}已经完成初始化，禁止重复操作")
            return

        self.write_log(f"{strategy_name}开始执行初始化")

        # Call on_init function of strategy
        strategy.on_init()

        # Put event to update init completed status.
        strategy.inited = True
        self.put_strategy_event(strategy)
        self.write_log(f"{strategy_name}初始化完成")

    def run(self):
        while True:
            empty_counter = 0
            for vt_symbol in self.symbol_strategy_map.keys():
                symbol, exchange = extract_vt_symbol(vt_symbol)
                try:
                    df = self.ts_api.coin_mins(
                        exchange='future_%s' % exchange.value.lower(),
                        symbol=symbol.lower(),
                        trade_date=self.start.strftime('%Y%m%d'),
                        freq='1min',
                        fields='date,open,high,low,close,vol,contract_type'
                    )
                except requests_exceptions.ConnectTimeout:
                    self.ts_api = ts.pro_api(self.token)
                    self.write_log("Connection Timeout, 重启 tushare API")
                    continue
                except requests_exceptions.ReadTimeout:
                    self.ts_api = ts.pro_api(self.token)
                    self.write_log("Read Timeout, 重启 tushare API")
                    continue

                if len(df) == 0:
                    empty_counter += 1
                    sleep(1.0)
                    continue

                df['datetime'] = pd.to_datetime(df.date)
                df.set_index('datetime', inplace=True)
                df = df[df.contract_type == 'this_week']

                self.symbol = symbol
                self.vt_symbol = vt_symbol
                self.exchange = exchange
                if symbol.startswith('BTC') or symbol.startswith('BCH'):
                    self.pricetick = 0.01
                else:
                    self.pricetick = 0.001

                for strategy in self.symbol_strategy_map[vt_symbol]:
                    self.strategy = strategy

                    if not strategy.trading:
                        strategy.on_start()
                        strategy.trading = True

                    for t, row in df.iterrows():
                        self.datetime = t
                        bar = BarData(
                            symbol=symbol,
                            exchange=exchange,
                            datetime=t,
                            interval=Interval.MINUTE,
                            volume=row["vol"],
                            open_price=row["open"],
                            high_price=row["high"],
                            low_price=row["low"],
                            close_price=row["close"],
                            gateway_name=self.gateway_name
                        )
                        self.new_bar(bar)

            if empty_counter < len(self.symbol_strategy_map.keys()):
                self.start += timedelta(days=1)
            else:
                sleep(30.0)

    def new_bar(self, bar: BarData):
        """"""
        self.bar = bar
        if hasattr(self.strategy, 'datetime'):
            self.strategy.datetime = bar.datetime

        self.cross_limit_order()
        self.cross_stop_order()
        self.strategy.on_bar(bar)

    def cross_limit_order(self):
        """
        Cross limit order with last bar/tick data.
        """
        long_cross_price = self.bar.low_price
        short_cross_price = self.bar.high_price
        long_best_price = self.bar.open_price
        short_best_price = self.bar.open_price

        for order, model_id in list(self.active_limit_orders.values()):
            if model_id != self.strategy.model_id:
                continue

            # Push order update with status "not traded" (pending).
            if order.status == Status.SUBMITTING:
                order.status = Status.NOTTRADED
                self.strategy.on_order(order)

            # Check whether limit orders can be filled.
            long_cross = (
                order.direction == Direction.LONG 
                and order.price >= long_cross_price 
                and long_cross_price > 0
            )

            short_cross = (
                order.direction == Direction.SHORT 
                and order.price <= short_cross_price 
                and short_cross_price > 0
            )

            if not long_cross and not short_cross:
                continue

            # Push order udpate with status "all traded" (filled).
            order.traded = order.volume
            order.status = Status.ALLTRADED
            self.strategy.on_order(order)

            self.active_limit_orders.pop(order.vt_orderid)

            if long_cross:
                trade_price = min(order.price, long_best_price)
                pos_change = order.volume
            else:
                trade_price = max(order.price, short_best_price)
                pos_change = -order.volume

            trade = TradeData(
                symbol=order.symbol,
                exchange=order.exchange,
                orderid=order.orderid,
                tradeid=f'DIGIT_{order.orderid}',
                direction=order.direction,
                offset=order.offset,
                price=trade_price,
                volume=order.volume,
                time=self.datetime.strftime("%H:%M:%S"),
                gateway_name=self.gateway_name,
            )
            trade.datetime = self.datetime

            self.strategy.pos += pos_change
            self.strategy.on_trade(trade)

    def cross_stop_order(self):
        """
        Cross stop order with last bar/tick data.
        """
        long_cross_price = self.bar.high_price
        short_cross_price = self.bar.low_price
        long_best_price = self.bar.open_price
        short_best_price = self.bar.open_price

        for stop_order, model_id in list(self.active_stop_orders.values()):
            if model_id != self.strategy.model_id:
                continue

            # Check whether stop order can be triggered.
            long_cross = (
                stop_order.direction == Direction.LONG 
                and stop_order.price <= long_cross_price
            )

            short_cross = (
                stop_order.direction == Direction.SHORT 
                and stop_order.price >= short_cross_price
            )

            if not long_cross and not short_cross:
                continue

            # Create order data.
            self.limit_order_count += 1

            order = OrderData(
                symbol=self.symbol,
                exchange=self.exchange,
                orderid='{}_{}_{}'.format(self.vt_symbol, self.datetime.strftime("%Y%m%d_%H%M"), self.limit_order_count),
                direction=stop_order.direction,
                offset=stop_order.offset,
                price=stop_order.price,
                volume=stop_order.volume,
                status=Status.ALLTRADED,
                gateway_name=self.gateway_name,
            )
            order.datetime = self.datetime

            # Create trade data.
            if long_cross:
                trade_price = max(stop_order.price, long_best_price)
                pos_change = order.volume
            else:
                trade_price = min(stop_order.price, short_best_price)
                pos_change = -order.volume

            trade = TradeData(
                symbol=order.symbol,
                exchange=order.exchange,
                orderid=order.orderid,
                tradeid=f'DIGIT_{order.orderid}',
                direction=order.direction,
                offset=order.offset,
                price=trade_price,
                volume=order.volume,
                time=self.datetime.strftime("%H:%M:%S"),
                gateway_name=self.gateway_name,
            )
            trade.datetime = self.datetime

            # Update stop order.
            stop_order.vt_orderid = order.vt_orderid
            stop_order.status = StopOrderStatus.TRIGGERED

            self.active_stop_orders.pop(stop_order.stop_orderid)

            # Push update to strategy.
            self.strategy.on_stop_order(stop_order)
            self.strategy.on_order(order)

            self.strategy.pos += pos_change
            self.strategy.on_trade(trade)

    def load_bar(
        self, vt_symbol: str, days: int, interval: Interval, callback: Callable
    ):
        """"""
        self.days = days
        self.callback = callback

    def send_order(
        self,
        strategy: CtaTemplate,
        direction: Direction,
        offset: Offset,
        price: float,
        volume: float,
        stop: bool,
        lock: bool
    ):
        """"""
        price = round_to(price, self.pricetick)
        if stop:
            vt_orderid = self.send_stop_order(direction, offset, price, volume)
        else:
            vt_orderid = self.send_limit_order(direction, offset, price, volume)
        return [vt_orderid]

    def send_stop_order(
        self, 
        direction: Direction, 
        offset: Offset, 
        price: float, 
        volume: float
    ):
        """"""
        self.stop_order_count += 1

        ts = self.datetime.strftime("%Y%m%d_%H%M")
        stop_order = StopOrder(
            vt_symbol=self.vt_symbol,
            direction=direction,
            offset=offset,
            price=price,
            volume=volume,
            stop_orderid=f"{STOPORDER_PREFIX}.{self.vt_symbol}_{ts}_{self.stop_order_count}",
            strategy_name=self.strategy.strategy_name,
        )

        self.active_stop_orders[stop_order.stop_orderid] = (stop_order, self.strategy.model_id)

        return stop_order.stop_orderid

    def send_limit_order(
        self, 
        direction: Direction,
        offset: Offset,
        price: float, 
        volume: float
    ):
        """"""
        self.limit_order_count += 1
        
        ts = self.datetime.strftime("%Y%m%d_%H%M")
        order = OrderData(
            symbol=self.symbol,
            exchange=self.exchange,
            orderid=f'{self.vt_symbol}_{ts}_{self.limit_order_count}',
            direction=direction,
            offset=offset,
            price=price,
            volume=volume,
            status=Status.SUBMITTING,
            gateway_name=self.gateway_name,
        )
        order.datetime = self.datetime

        self.active_limit_orders[order.vt_orderid] = (order, self.strategy.model_id)

        return order.vt_orderid

    def cancel_order(self, strategy: CtaTemplate, vt_orderid: str):
        """
        Cancel order by vt_orderid.
        """
        if vt_orderid.startswith(STOPORDER_PREFIX):
            self.cancel_stop_order(strategy, vt_orderid)
        else:
            self.cancel_limit_order(strategy, vt_orderid)

    def cancel_stop_order(self, strategy: CtaTemplate, vt_orderid: str):
        """"""
        if vt_orderid not in self.active_stop_orders:
            return
        stop_order, _ = self.active_stop_orders.pop(vt_orderid)

        stop_order.status = StopOrderStatus.CANCELLED
        self.strategy.on_stop_order(stop_order)

    def cancel_limit_order(self, strategy: CtaTemplate, vt_orderid: str):
        """"""
        if vt_orderid not in self.active_limit_orders:
            return
        order, _ = self.active_limit_orders.pop(vt_orderid)

        order.status = Status.CANCELLED
        self.strategy.on_order(order)

    def cancel_all(self, strategy: CtaTemplate):
        """
        Cancel all orders, both limit and stop.
        """
        vt_orderids = list(self.active_limit_orders.keys())
        for vt_orderid in vt_orderids:
            self.cancel_limit_order(strategy, vt_orderid)

        stop_orderids = list(self.active_stop_orders.keys())
        for vt_orderid in stop_orderids:
            self.cancel_stop_order(strategy, vt_orderid)

    def write_log(self, msg: str, strategy: CtaTemplate = None):
        """
        Create cta engine log event.
        """
        if strategy:
            msg = f"{strategy.strategy_name}: {msg}"

        log = LogData(msg=msg, gateway_name="CtaStrategy")
        event = Event(type=EVENT_CTA_LOG, data=log)
        self.event_engine.put(event)
    
    def send_email(self, msg: str, strategy: CtaTemplate = None):
        """
        Send email to default receiver.
        """
        pass
    
    def sync_strategy_data(self, strategy: CtaTemplate):
        """
        Sync strategy data into json file.
        """
        pass

    def get_engine_type(self):
        """
        Return engine type.
        """
        return self.engine_type

    def put_strategy_event(self, strategy: CtaTemplate):
        """
        Put an event to update strategy status.
        """
        pass

    def output(self, msg):
        """
        Output message of backtesting engine.
        """
        print(f"{datetime.now()}\t{msg}")
