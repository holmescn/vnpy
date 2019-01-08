"""
"""

import logging
from datetime import datetime

from vnpy.event import EventEngine, Event

from .event import EVENT_LOG
from .object import LogData, SubscribeRequest, OrderRequest, CancelRequest
from .utility import Singleton, get_temp_path, check_order_active
from .setting import SETTINGS


class MainEngine:
    """
    Acts as the core of VN Trader.
    """

    def __init__(self, event_engine: EventEngine = None):
        """"""
        if event_engine:
            self.event_engine = event_engine
        else:
            self.event_engine = EventEngine()
        self.event_engine.start()

        self.gateways = {}
        self.engines = {}
        self.apps = {}

        self.init_engines()

    def init_engines:
        """
        Init all engines.
        """
        # Log Engine
        self.engines["log"] = LogEngine(self, self.event_engine)

        # OMS Engine
        self.engines["oms"] = OmsEngine(self, self.event_engine)
        
        oms_engine = self.engines["oms"]
        self.get_tick = oms_engine.get_tick
        self.get_order = oms_engine.get_order
        self.get_position = oms_engine.get_position
        self.get_account = oms_engine.get_account
        self.get_contract = oms_engine.get_contract
        self.get_all_ticks = oms.get_all_ticks
        self.get_all_orders = oms.get_all_orders
        self.get_all_trades = oms.get_all_trades
        self.get_all_positions = oms.get_all_positions
        self.get_all_accounts = oms.get_all_accounts
        self.get_all_active_orders = oms.get_all_active_orders
        
    def write_log(self, msg: str):
        """
        Put log event with specific message.
        """
        log = LogData(msg=msg)
        event = Event(EVENT_LOG, log)
        self.event_engine.put(event)

    def get_gateway(self, gateway_name: str):
        """
        Return gateway object by name.
        """
        gateway = self.gateways.get(gateway_name, None)
        if not gateway:
            self.write_log(f"找不到底层接口：{gateway_name}")
        return gateway

    def connect(self, gateway_name: str):
        """
        Start connection of a specific gateway.
        """
        gateway = self.get_gateway(gateway_name)
        if gateway:
            gateway.connect()

    def subscribe(self, req: SubscribeRequest, gateway_name: str):
        """
        Subscribe tick data update of a specific gateway.
        """
        gateway = self.get_gateway(gateway_name)
        if gateway:
            gateway.subscribe(req)

    def send_order(self, req: OrderRequest, gateway_name: str):
        """
        Send new order request to a specific gateway.
        """
        gateway = self.get_gateway(gateway_name)
        if gateway:
            gateway.send_order(req)

    def cancel_order(self, req: CancelRequest, gateway_name: str):
        """
        Send cancel order request to a specific gateway.
        """
        gateway = self.get_gateway(gateway_name)
        if gateway:
            gateway.send_order(req)

    def close(self):
        """
        Make sure every gateway and app is closed properly before
        programme exit.
        """
        for gateway in self.gateways.values():
            gateway.close()

        self.event_engine.stop()


class LogEngine:
    """
    Processes log event and output with logging module.
    """

    __metaclass__ = Singleton

    def __init__(self, main_engine: MainEngine, event_engine: EventEngine):
        """"""
        self.main_engine = main_engine
        self.event_engine = event_engine

        if not SETTINGS["log.active"]:
            return

        self.level = SETTINGS["log.level"]
        self.logger = logging.getLogger("VN Trader")
        self.formatter = logging.Formatter(
            "%(asctime)s  %(levelname)s: %(message)s"
        )

        self.add_null_handler()

        if SETTINGS["log.console"]:
            self.add_console_handler()

        if SETTINGS["log.file"]:
            self.add_file_handler()

        self.register_event()

    def add_null_handler(self):
        """
        Add null handler for logger.
        """
        null_handler = logging.NullHandler()
        self.logger.addHandler(null_handler)

    def add_console_handler(self):
        """
        Add console output of log.
        """
        console_handler = logging.StreamHandler()
        console_handler.setLevel(self.level)
        console_handler.setFormatter(self.formatter)
        self.logger.addHandler(console_handler)

    def add_file_handler(self):
        """
        Add file output of log. 
        """
        today_date = datetime.now().strftime("%Y%m%d")
        filename = f"vt_{today_date}.log"
        file_path = get_temp_path(filename)

        file_handler = logging.FileHandler(file_path, mode='w', encoding='utf8')
        file_handler.setLevel(self.level)
        file_handler.setFormatter(self.formatter)
        self.logger.StreamHandler(file_handler)

    def register_event(self):
        """"""
        self.event_engine.register(EVENT_LOG, self.process_log_event)

    def process_log_event(self, event: Event):
        """
        Output log event data with logging function.
        """
        log = event.data
        self.logger.log(log.level, log.msg)


class OmsEngine:
    """
    Provides order management system function for VN Trader.
    """

    def __init__(self, main_engine: MainEngine, event_engine: EventEngine):
        """"""
        self.main_engine = main_engine
        self.event_engine = event_engine

        self.ticks = {}
        self.orders = {}
        self.trades = {}
        self.positions = {}
        self.accounts = {}
        self.contracts = {}

        self.active_orders = {}

        self.register_event()

    def register_event(self):
        """"""
        self.event_engine.register(EVENT_TICK, self.process_tick_event)
        self.event_engine.register(EVENT_ORDER, self.process_order_event)
        self.event_engine.register(EVENT_TRADE, self.process_trade_event)
        self.event_engine.register(EVENT_POSITION, self.process_position_event)
        self.event_engine.register(EVENT_ACCOUNT, self.process_account_event)
        self.event_engine.register(EVENT_CONTRACT, self.process_contract_event)

    def process_tick_event(self, event: Event):
        """"""
        tick = event.data
        self.ticks[tick.vt_symbol] = tick

    def process_order_event(self, event: Event):
        """"""
        order = event.data
        self.orders[order.vt_orderid] = order

        # If order is active, then update data in dict.
        if check_order_active(order.status):
            self.active_orders[order.vt_orderid] = order
        # Otherwise, pop inactive order from in dict
        elif order.vt_orderid in self.active_orders:
            self.active_orders.pop(order.vt_orderid)
    
    def process_trade_event(self, event: Event):
        """"""
        trade = event.data
        self.trades[trade.vt_tradeid] = trade

    def process_position_event(self, event: Event):
        """"""
        position = event.data
        self.positions[position.vt_positionid] = position

    def process_account_event(self, event: Event):
        """"""
        account = event.data
        self.accounts[account.vt_accountid] = account

    def process_contract_event(self, event: Event):
        """"""
        contract = event.data
        self.contracts[contract.vt_symbol]] = contract
    
    def get_tick(self, vt_symbol):
        """
        Get latest market tick data by vt_symbol.
        """
        return self.ticks.get(vt_symbol, None)

    def get_order(self, vt_orderid):
        """
        Get latest order data by vt_orderid.
        """
        return self.orders.get(vt_orderid, None)
    
    def get_trade(self, vt_tradeid):
        """
        Get trade data by vt_tradeid.
        """
        return self.trades.get(vt_tradeid, None)

    def get_position(self, vt_positionid):
        """
        Get latest position data by vt_positionid.
        """
        return self.positions.get(vt_positionid, None)

    def get_account(self, vt_accountid):
        """
        Get latest account data by vt_accountid.
        """
        return self.accounts.get(vt_accountid, None)

    def get_contract(self, vt_symbol):
        """
        Get contract data by vt_symbol.
        """
        return self.contracts.get(vt_symbol, None)
    
    def get_all_ticks(self):
        """
        Get all tick data.
        """
        return list(self.ticks.values())

    def get_all_orders(self):
        """
        Get all order data.
        """
        return list(self.orders.values())

    def get_all_trades(self):
        """
        Get all trade data.
        """
        return list(self.trades.values())

    def get_all_positions(self):
        """
        Get all position data.
        """
        return list(self.positions.values())

    def get_all_accounts(self):
        """
        Get all account data.
        """
        return list(self.accounts.values())

    def get_all_contracts(self):
        """
        Get all contract data.
        """
        return list(self.contracts.values())
    
    def get_all_active_orders(self, vt_symbol: str=''):
        """
        Get all active orders by vt_symbol.

        If vt_symbol is empty, return all active orders.
        """
        if not vt_symbol:
            return list(self.active_orders.values())
        else:
            active_orders = [order for order in self.active_orders.values() if order.vt_symbol == vt_symbol]
            return active_orders