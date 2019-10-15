import os
import sys
import json
from time import sleep
from datetime import datetime, time
from logging import INFO
from copy import copy

from vnpy.event import EventEngine
from vnpy.trader.setting import SETTINGS
from vnpy.trader.engine import MainEngine

from vnpy.app.cta_backtester import CtaBacktesterApp, BacktesterEngine
from vnpy.app.cta_strategy.base import EVENT_CTA_LOG
from vnpy.gateway.tushare import TushareGateway
from vnpy.trader.event import EVENT_TIMER
from vnpy.trader.utility import load_json


SETTINGS["log.active"] = True
SETTINGS["log.level"] = INFO
SETTINGS["log.console"] = True
SETTINGS["log.file"] = True

if sys.platform == 'win32':
    SETTINGS["database.database"] = "D:\\coin-database.sqlite"


def main():
    event_engine = EventEngine()
    main_engine = MainEngine(event_engine)
    main_engine.add_gateway(TushareGateway)
    bt_engine: BacktesterEngine = main_engine.add_app(CtaBacktesterApp)
    main_engine.write_log("主引擎创建成功")

    log_engine = main_engine.get_engine("log")
    event_engine.register(EVENT_CTA_LOG, log_engine.process_log_event)
    main_engine.write_log("注册日志事件监听")

    connect_setting = load_json('connect_tushare.json')
    main_engine.connect(connect_setting, "TUSHARE")
    main_engine.write_log("连接 TUSHARE 接口")

    bt_engine.init_engine()
    main_engine.write_log("CTA回测引擎初始化完成")

    vt_symbols = [
        'BTCUSDT.OKEX',
        'BCHUSDT.OKEX',
        'BSVUSDT.OKEX',
        'LTCUSDT.OKEX',
        'ETHUSDT.OKEX',
        'ETCUSDT.OKEX',
        'EOSUSDT.OKEX',
        'XRPUSDT.OKEX',
        'OKBUSDT.OKEX',
        'TRXUSDT.OKEX',
        'DASHUSDT.OKEX',
        'NEOUSDT.OKEX',
    ]
    for vt_symbol in vt_symbols:
        bt_engine.run_downloading(vt_symbol, '1m', datetime(2019, 9, 1, 0, 0), datetime.now())


if __name__ == "__main__":
    main()
