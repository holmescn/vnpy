import os
import sys
import json
import argparse
from time import sleep
from datetime import datetime, time
from logging import INFO


from vnpy.event import EventEngine
from vnpy.trader.setting import SETTINGS
from vnpy.trader.engine import MainEngine

from vnpy.gateway.tushare import TushareGateway
from vnpy.app.cta_strategy import CtaStrategyApp
from vnpy.app.cta_strategy.base import EVENT_CTA_LOG
from vnpy.trader.event import EVENT_TIMER
from vnpy.trader.utility import get_file_path


SETTINGS["log.active"] = True
SETTINGS["log.level"] = INFO
SETTINGS["log.console"] = True
SETTINGS["log.file"] = True

if sys.platform == 'win32':
    SETTINGS["database.database"] = "D:\\tushare_realtime.sqlite"


def main(args):
    event_engine = EventEngine()
    main_engine = MainEngine(event_engine)
    gateway: TushareGateway = main_engine.add_gateway(TushareGateway)    
    cta_engine = main_engine.add_app(CtaStrategyApp)
    main_engine.write_log("主引擎创建成功")

    # 设置开始时间
    gateway.rt_datetime = datetime.strptime(args.start_date, '%Y-%m-%d')

    log_engine = main_engine.get_engine("log")
    event_engine.register(EVENT_CTA_LOG, log_engine.process_log_event)
    main_engine.write_log("注册日志事件监听")

    file_path = get_file_path('connect_tushare.json')
    with open(file_path, 'r', encoding='utf-8') as f:
        connect_setting = json.load(f)

    main_engine.connect(connect_setting, "TUSHARE")
    main_engine.write_log("连接 TUSHARE 接口")

    cta_engine.init_engine()
    main_engine.write_log("CTA策略初始化完成")

    cta_engine.init_all_strategies()
    all_strategies_init = False
    while not all_strategies_init:
        all_strategies_init = True
        for s in cta_engine.strategies.values():
            if not s.inited:
                all_strategies_init = False
                sleep(1)
                break

    main_engine.write_log("CTA策略全部初始化")

    cta_engine.start_all_strategies()
    main_engine.write_log("CTA策略全部启动")
    gateway.initialized = True

    while True:
        sleep(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--start_date', default='2019-09-15')
    main(parser.parse_args())
