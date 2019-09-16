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

from vnpy.gateway.tushare import TushareGateway
from vnpy.app.cta_strategy import CtaStrategyApp
from vnpy.app.cta_strategy.base import EVENT_CTA_LOG
from vnpy.trader.event import EVENT_TIMER
from vnpy.trader.object import (
    BarData,
    TickData,
    OrderData,
    TradeData,
    OrderRequest,
    CancelRequest,
)
from vnpy.trader.constant import (
    Exchange,
    OrderType,
    Offset,
    Direction,
    Status
)


SETTINGS["log.active"] = True
SETTINGS["log.level"] = INFO
SETTINGS["log.console"] = True
SETTINGS["log.file"] = True

if sys.platform == 'win32':
    SETTINGS["database.database"] = "D:\\database-0.sqlite"


def main():
    event_engine = EventEngine()
    main_engine = MainEngine(event_engine)
    main_engine.add_gateway(TushareGateway)
    cta_engine = main_engine.add_app(CtaStrategyApp)
    main_engine.write_log("主引擎创建成功")

    log_engine = main_engine.get_engine("log")
    event_engine.register(EVENT_CTA_LOG, log_engine.process_log_event)
    main_engine.write_log("注册日志事件监听")

    with open(os.path.abspath('./.vntrader/connect_tushare.json'), 'r', encoding='utf-8') as f:
        connect_setting = json.load(f)

    main_engine.connect(connect_setting, "TUSHARE")
    main_engine.write_log("连接 TUSHARE 接口")

    cta_engine.init_engine()
    main_engine.write_log("CTA策略初始化完成")

    cta_engine.init_all_strategies()
    # Leave enough time to complete strategy initialization
    sleep(60)
    main_engine.write_log("CTA策略全部初始化")

    cta_engine.start_all_strategies()
    main_engine.write_log("CTA策略全部启动")

    while True:
        sleep(1)


if __name__ == "__main__":
    main()
