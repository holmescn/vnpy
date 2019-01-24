""""""

import importlib
import os
import shelve
import traceback
from collections import defaultdict
from pathlib import Path
from typing import Any, Callable

from vnpy.event import Event, EventEngine
from vnpy.trader.constant import Direction, Interval, PriceType
from vnpy.trader.engine import BaseEngine, MainEngine
from vnpy.trader.event import EVENT_ORDER, EVENT_TICK, EVENT_TRADE
from vnpy.trader.object import LogData, OrderRequest, TickData
from vnpy.trader.utility import get_temp_path
from .base import (
    CtaOrderType,
    EVENT_CTA_LOG,
    EVENT_CTA_STOPORDER,
    EVENT_CTA_STRATEGY,
    EngineType,
    ORDER_CTA2VT,
    STOPORDER_PREFIX,
    StopOrder,
    StopOrderStatus,
)
from .template import CtaTemplate


class CtaEngine(BaseEngine):
    """"""

    engine_type = EngineType.LIVE  # live trading engine

    filename = "CtaStrategy.vt"

    def __init__(self, main_engine: MainEngine, event_engine: EventEngine):
        """"""
        super(CtaEngine, self).__init__(
            main_engine, event_engine, "CtaStrategy"
        )

        self.setting_file = None  # setting file object

        self.classes = {}  # class_name: stategy_class
        self.strategies = {}  # strategy_name: strategy

        self.symbol_strategy_map = defaultdict(
            list
        )  # vt_symbol: strategy list
        self.orderid_strategy_map = {}  # vt_orderid: strategy
        self.strategy_orderid_map = defaultdict(
            set
        )  # strategy_name: orderid list

        self.stop_order_count = 0  # for generating stop_orderid
        self.stop_orders = {}  # stop_orderid: stop_order

    def init_engine(self):
        """
        """
        self.load_strategy_class()
        self.load_strategy_setting()
        self.register_event()
        self.write_log("CTA策略引擎初始化成功")

    def close(self):
        """"""
        self.save_strategy_setting()

    def register_event(self):
        """"""
        self.event_engine.register(EVENT_TICK, self.process_tick_event)
        self.event_engine.register(EVENT_ORDER, self.process_order_event)
        self.event_engine.register(EVENT_TRADE, self.process_trade_event)

    def process_tick_event(self, event: Event):
        """"""
        tick = event.data

        strategies = self.symbol_strategy_map[tick.vt_symbol]
        if not strategies:
            return

        self.check_stop_order(tick)

        for strategy in strategies:
            if strategy.inited:
                self.call_strategy_func(strategy, strategy.on_tick, tick)

    def process_order_event(self, event: Event):
        """"""
        order = event.data

        strategy = self.orderid_strategy_map.get(order.vt_orderid, None)
        if not strategy:
            return

        # Remove vt_orderid if order is no longer active.
        vt_orderids = self.strategy_orderid_map[strategy.name]
        if order.vt_orderid in vt_orderids and not order.is_active():
            vt_orderids.remove(order.vt_orderid)

        self.call_strategy_func(strategy, strategy.on_order, order)

    def process_trade_event(self, event: Event):
        """"""
        trade = event.data

        strategy = self.orderid_strategy_map.get(trade.vt_orderid, None)
        if not strategy:
            return

        if trade.direction == Direction.LONG:
            strategy.pos += trade.volume
        else:
            strategy.pos -= trade.volume

        self.call_strategy_func(strategy, strategy.on_trade, trade)

    def check_stop_order(self, tick: TickData):
        """"""
        for stop_order in self.stop_orders.values():
            if stop_order.vt_symbol != tick.vt_symbol:
                continue

            long_triggered = (
                so.direction == Direction.LONG
                and tick.last_price >= stop_order.price
            )
            short_triggered = (
                so.direction == Direction.SHORT
                and tick.last_price <= stop_order.price
            )

            if long_triggered or short_triggered:
                strategy = self.strategies[stop_order.strategy_name]

                # To get excuted immediately after stop order is
                # triggered, use limit price if available, otherwise
                # use ask_price_5 or bid_price_5
                if so.direction == Direction.LONG:
                    if tick.limit_up:
                        price = tick.limit_up
                    else:
                        price = tick.ask_price_5
                else:
                    if tick.limit_down:
                        price = tick.limit_down
                    else:
                        price = tick.bid_price_5

                vt_orderid = self.send_limit_order(
                    strategy, stop_order.order_type, price, stop_order.volume
                )

                # Update stop order status if placed successfully
                if vt_orderid:
                    # Remove from relation map.
                    self.stop_orders.pop(stop_order.stop_orderid)

                    vt_orderids = self.strategy_orderid_map[strategy.name]
                    if stop_orderid in vt_orderids:
                        vt_orderids.remove(stop_orderid)

                    # Change stop order status to cancelled and update to strategy.
                    stop_order.status = StopOrderStatus.TRIGGERED
                    stop_order.vt_orderid = vt_orderid

                    self.call_strategy_func(
                        strategy, strategy.on_stop_order, stop_order
                    )

    def send_limit_order(
        self,
        strategy: CtaTemplate,
        order_type: CtaOrderType,
        price: float,
        volume: float,
    ):
        """
        Send a new order.
        """
        contract = self.main_engine.get_contract(strategy.vt_symbol)
        if not contract:
            self.write_log(f"委托失败，找不到合约：{strategy.vt_symbol}", strategy)
            return ""

        direction, offset = ORDER_CTA2VT[order_type]

        # Create request and send order.
        req = OrderRequest(
            symbol=contract.symbol,
            exchange=contract.exchange,
            dierction=direction,
            offset=offset,
            price_type=PriceType.LIMIT,
            price=price,
            volume=volume,
        )
        vt_orderid = self.main_engine.send_limit_order(
            req, contract.gateway_name
        )

        # Save relationship between orderid and strategy.
        self.orderid_strategy_map[vt_orderid] = strategy

        vt_orderids = self.strategy_orderid_map[strategy.name]
        vt_orderids.add(vt_orderid)

        return vt_orderid

    def send_stop_order(
        self,
        strategy: CtaTemplate,
        order_type: CtaOrderType,
        price: float,
        volume: float,
    ):
        """
        Send a new order.
        """
        self.stop_order_count += 1
        direction, offset = ORDER_CTA2VT[order_type]
        stop_orderid = f"{STOPORDER_PREFIX}.{self.stop_order_count}"

        stop_order = StopOrder(
            vt_symbol=strategy.vt_symbol,
            direction=direction,
            offset=offset,
            price=price,
            volume=volume,
            stop_orderid=stop_orderid,
            strategy_name=strategy.strategy_name,
        )

        self.stop_orders[stop_orderid] = stop_order

        vt_orderids = self.strategy_orderid_map[strategy.name]
        vt_orderids.add(stop_orderid)

        self.call_strategy_func(strategy, strategy.on_stop_order, stop_order)

        return stop_orderid

    def cancel_limit_order(self, vt_orderid: str):
        """
        Cancel existing order by vt_orderid.
        """
        order = self.main_engine.get_order(vt_orderid)
        if not order:
            self.write_log(f"撤单失败，找不到委托{vt_orderid}", strategy)
            return

        req = order.create_cancel_request()
        self.main_engine.cancel_limit_order(req, order.gateway_name)

    def cancel_stop_order(self, stop_orderid: str):
        """
        Cancel a local stop order.
        """
        stop_order = self.stop_orders.get(stop_orderid, None)
        if not stop_order:
            return
        strategy = self.strategies[stop_order.strategy_name]

        # Remove from relation map.
        self.stop_orders.pop(stop_orderid)

        vt_orderids = self.strategy_orderid_map[strategy.name]
        if stop_orderid in vt_orderids:
            vt_orderids.remove(stop_orderid)

        # Change stop order status to cancelled and update to strategy.
        stop_order.status = StopOrderStatus.CANCELLED

        self.call_strategy_func(strategy, strategy.on_stop_order, stop_order)

    def send_order(
        self,
        strategy: CtaTemplate,
        order_type: CtaOrderType,
        price: float,
        volume: float,
        stop: bool,
    ):
        """
        """
        if stop:
            return self.send_stop_order(strategy, order_type, price, volume)
        else:
            return self.send_limit_order(strategy, order_type, price, volume)

    def cancel_order(self, vt_orderid: str):
        """
        """
        if vt_orderid.startswith(STOPORDER_PREFIX):
            self.cancel_stop_order(vt_orderid)
        else:
            self.cancel_limit_order(vt_orderid)

    def cancel_all(self, strategy: CtaTemplate):
        """
        Cancel all active orders of a strategy.
        """
        vt_orderids = self.strategy_orderid_map[strategy.name]
        if not vt_orderids:
            return

        for vt_orderid in vt_orderids:
            self.cancel_limit_order(vt_orderid)

    def get_engine_type(self):
        """"""
        return self.engine_type

    def load_bar(
        self, vt_symbol: str, days: int, interval: Interval, callback: Callable
    ):
        """"""
        pass

    def load_tick(self, vt_symbol: str, days: int, callback: Callable):
        """"""
        pass

    def call_strategy_func(
        self, strategy: CtaTemplate, func: Callable, params: Any = None
    ):
        """
        Call function of a strategy and catch any exception raised.
        """
        try:
            if params:
                func(params)
            else:
                func()
        except Exception:
            strategy.trading = False
            strategy.inited = False

            msg = f"触发异常已停止\n{traceback.format_exc()}"
            self.write_log(msg, strategy)

    def add_strategy(
        self,
        class_name: str,
        strategy_name: str,
        vt_symbol: str,
        setting: dict,
    ):
        """
        Add a new strategy.
        """
        if strategy_name in self.strategies:
            self.write_log(f"创建策略失败，存在重名{strategy_name}")
            return

        strategy_class = self.classes[class_name]

        strategy = strategy_class(self, strategy_name, vt_symbol, setting)
        self.strategies[strategy_name] = strategy

        # Add vt_symbol to strategy map.
        strategies = self.symbol_strategy_map[vt_symbol]
        strategies.append(strategy)

        # Update to setting file.
        self.update_strategy_setting(strategy_name, setting)

        self.put_strategy_event(strategy)

    def init_strategy(self, strategy_name: str):
        """
        Init a strategy.
        """
        strategy = self.strategies[strategy_name]
        self.call_strategy_func(strategy, strategy.on_init)
        strategy.inited = True

        # Subscribe market data
        contract = self.main_engine.get_contract(strategy.vt_symbol)
        if not contract:
            self.write_log(f"行情订阅失败，找不到合约{strategy.vt_symbol}", strategy)

        self.put_strategy_event(strategy)

    def start_strategy(self, strategy_name: str):
        """
        Start a strategy.
        """
        strategy = self.strategies[strategy_name]
        self.call_strategy_func(strategy, strategy.on_start)
        strategy.trading = True

        self.put_strategy_event(strategy)

    def stop_strategy(self, strategy_name: str):
        """
        Stop a strategy.
        """
        strategy = self.strategies[strategy_name]
        self.call_strategy_func(strategy, strategy.on_start)
        strategy.trading = False

        self.put_strategy_event(strategy)

    def edit_strategy(self, strategy_name: str, setting: dict):
        """
        Edit parameters of a strategy.
        """
        strategy = self.strategies[strategy_name]
        strategy.update_setting(setting)

        self.update_strategy_setting(strategy_name, setting)
        self.put_strategy_event(strategy)

    def remove_strategy(self, strategy_name: str):
        """
        Remove a strategy.
        """
        # Remove setting
        self.remove_strategy_setting(strategy_name)

        # Remove from symbol strategy map
        strategy = self.strategies[strategy_name]
        strategies = self.symbol_strategy_map[strategy.vt_symbol]
        strategies.remove(strategy)

        # Remove from active orderid map
        if strategy_name in self.strategy_orderid_map:
            vt_orderids = self.strategy_orderid_map.pop(strategy_name)

            # Remove vt_orderid strategy map
            for vt_orderid in vt_orderids:
                self.orderid_strategy_map.pop(vt_orderid)

        # Remove from strategies
        self.strategies.pop(strategy_name)

    def load_strategy_class(self):
        """
        Load strategy class from source code.
        """
        path1 = Path(__file__).parent.joinpath("strategies")
        self.load_strategy_class_from_folder(
            path1, "vnpy.app.cta_strategy.strategies"
        )

        path2 = Path.cwd().joinpath("strategies")
        self.load_strategy_class_from_folder(path2, "strategies")

    def load_strategy_class_from_folder(
        self, path: Path, module_name: str = ""
    ):
        """
        Load strategy class from certain folder.
        """
        for dirpath, dirnames, filenames in os.walk(path):
            for filename in filenames:
                module_name = ".".join(
                    [module_name, filename.replace(".py", "")]
                )
                self.load_strategy_class_from_module(module_name)

    def load_strategy_class_from_module(self, module_name: str):
        """
        Load strategy class from module file.
        """
        try:
            module = importlib.import_module(module_name)

            for name in dir(module):
                value = getattr(module, name)
                if issubclass(value, CtaTemplate) and value is not CtaTemplate:
                    self.classes[value.__name__] = value
        except:  # noqa
            msg = f"策略文件{module_name}加载失败，触发异常：\n{traceback.format_exc()}"
            self.write_log(msg)

    def get_all_strategy_class_names(self):
        """
        Return names of strategy classes loaded.
        """
        return list(self.classes.keys())

    def get_strategy_class_parameters(self, class_name: str):
        """
        Get default parameters of a strategy class.
        """
        strategy_class = self.classes[class_name]

        parameters = {}
        for name in strategy_class.parameters:
            parameters[name] = getattr(strategy_class, name)

        return parameters

    def get_strategy_parameters(self, strategy_name):
        """
        Get parameters of a strategy.
        """
        strategy = self.strategies[strategy_name]
        return strategy.get_parameters()

    def init_all_strategies(self):
        """
        """
        for strategy_name in self.strategies.keys():
            self.init_strategy(strategy_name)

    def start_all_strategies(self):
        """
        """
        for strategy_name in self.strategies.keys():
            self.start_strategy(strategy_name)

    def stop_all_strategies(self):
        """
        """
        for strategy_name in self.strategies.keys():
            self.stop_strategy(strategy_name)

    def load_strategy_setting(self):
        """
        Load setting file.
        """
        filepath = str(get_temp_path(self.filename))
        self.setting_file = shelve.open(filepath)

        for tp in list(self.setting_file.values()):
            class_name, strategy_name, vt_symbol, setting = tp
            self.add_strategy(class_name, strategy_name, vt_symbol, setting)

    def update_strategy_setting(self, strategy_name: str, setting: dict):
        """
        Update setting file.
        """
        strategy = self.strategies[strategy_name]

        self.setting_file[strategy_name] = (
            strategy.__class__.__name__,
            strategy_name,
            strategy.vt_symbol,
            setting,
        )
        self.setting_file.sync()

    def remove_strategy_setting(self, strategy_name: str):
        """
        Update setting file.
        """
        if strategy_name not in self.setting_file:
            return

        self.setting_file.pop(strategy_name)
        self.setting_file.sync()

    def save_strategy_setting(self):
        """
        Save and close setting file.
        """
        if self.setting_file:
            self.setting_file.close()

    def put_stop_order_event(self, stop_order: StopOrder):
        """
        Put an event to update stop order status.
        """
        event = Event(EVENT_CTA_STOPORDER, stop_order)
        self.event_engine.put(event)

    def put_strategy_event(self, strategy: CtaTemplate):
        """
        Put an event to update strategy status.
        """
        data = strategy.get_data()
        event = Event(EVENT_CTA_STRATEGY, data)
        self.event_engine.put(event)

    def write_log(self, msg: str, strategy: CtaTemplate = None):
        """
        Create cta engine log event.
        """
        if strategy:
            msg = f"{strategy.strategy_name}: {msg}"

        log = LogData(msg=msg, gateway_name="CtaStrategy")
        event = Event(type=EVENT_CTA_LOG, data=log)
        self.event_engine.put(event)
