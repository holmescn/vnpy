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

from tushare_engine import TushareEngine
from vnpy.app.cta_strategy import CtaStrategyApp
from vnpy.app.cta_strategy.base import EVENT_CTA_LOG
from vnpy.trader.event import EVENT_TIMER


SETTINGS["log.active"] = True
SETTINGS["log.level"] = INFO
SETTINGS["log.console"] = True
SETTINGS["log.file"] = True

if sys.platform == 'win32':
    SETTINGS["database.database"] = "D:\\tushare_realtime.sqlite"


CtaStrategyApp.engine_class = TushareEngine


def main(args):
    event_engine = EventEngine()
    main_engine = MainEngine(event_engine)
    # gateway: TushareGateway = main_engine.add_gateway(TushareGateway)    
    ts_engine: TushareEngine = main_engine.add_app(CtaStrategyApp)
    main_engine.write_log("主引擎创建成功")

    log_engine = main_engine.get_engine("log")
    event_engine.register(EVENT_CTA_LOG, log_engine.process_log_event)
    main_engine.write_log("注册日志事件监听")

    ts_engine.init_engine()
    main_engine.write_log("CTA策略初始化完成")

    ts_engine.init_all_strategies()
    main_engine.write_log("CTA策略全部初始化")

    start_date = datetime.strptime(args.start_date, '%Y-%m-%d')
    end_date = datetime.strptime(args.end_date, '%Y-%m-%d')
    ts_engine.run(start_date, end_date)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--start_date', required=True)
    parser.add_argument('--end_date', default=datetime.now().strftime("%Y-%m-%d"))
    main(parser.parse_args())
