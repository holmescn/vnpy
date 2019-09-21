import datetime
import json
import logging
import logging.handlers
import os
import threading
import time

import requests as req
from vnpy.trader.utility import get_folder_path


# 提交成交记录，这是主要调用的方法
def submit_trade_data(trade_list, after_submit_event=None, ip_port_str=None, isDebug=False):
    '''
    主要功能：提交成交数据到统计系统
    实现逻辑：使用多线程的方式提交，不影响主流程，可以设置回调方法处理，添加日志功能，方便跟踪，主要以日期格式为文件名，即每天会产生一个新的日志文件
    :param trade_list:成交记录，类型：list，例子如下：
            [{"broker_id":"9999","direction":"buy","instrument_id":"IF1905","investor_id":"000000"
                ,"model_id":"IF_m1_a_99_v1.0","price":3689,"trade_id":"1236","trade_time":"2019-05-16 13:10:34","volume":1}
            ,{"broker_id":"9999","direction":"sell","instrument_id":"IF1905","investor_id":"000000"
                ,"model_id":"IF_m1_a_99_v1.0","price":3680,"trade_id":"1237","trade_time":"2019-05-16 13:13:34","volume":1
                ,"close_trade_id":"1236"}]
    :param after_submit_event:成功请求后才会调用的方法事件，提供两个参数:原成交记录数组和报错信息，报错json信息格式如下：
                        None
                        or
                        [{"model_id": "IF_m1_a_99_v1.0", "trade_id": "1236", "msg":"记录已存在，不能重复提交"}
                        , {"model_id": "IF_m1_a_99_v1.0", "trade_id": "1237", "msg: "没有与close_trade_id：1236匹配的开仓记录"}]

    :param ip_port_str:
    '''
    if len(trade_list) == 0:
        return

    ip_port_str = get_ip_str(ip_port_str)

    # 调用分线程
    t1 = threading.Thread(target=submit_trade_data_thread_func, args=(trade_list, ip_port_str, after_submit_event,))
    t1.start()

    if isDebug:
        t1.join()    # 测试用，以后会去掉


# 提交账号金额，这是主要调用的方法
def submit_account_data(date, broker_id, account, original_money=None, lastest_money=None, ip_port_str=None):
    '''
    主要功能：提交账号的金额信息到统计系统，方便统计回撤情况
    :param date: 金额日期
    :param account: 账号
    :param original_money: 当天的起始金额（若给None则不再更新；若在数据库中此项为None，但lastest_money有值，则将lastest_money定为起始值）
    :param lastest_money: 当天的最新金额
    :param ip_port_str: 接口的url和端口，不给则使用默认的，若有变动请传值
    '''
    if date is None or account is None:
        return

    ip_port_str = get_ip_str(ip_port_str)

    # 调用分线程
    t1 = threading.Thread(target=submit_account_data_thread_func, args=(date, broker_id, account, original_money, lastest_money, ip_port_str,))
    t1.start()


# 提交心跳记录，这是主要调用的方法
def submit_heart_beat_data(model_id, file_name, is_enable=None, ip_port_str=None):
    '''
    主要功能，提交运行程序的心跳数据，方便监控程序是否正常运行
    :param model_id: model_id
    :param file_name: 运行文件名称
    :param is_enable: 启用/停用，为空则是正常的心跳记录
    :param ip_port_str: 接口的url和端口，不给则使用默认的，若有变动请传值
    '''
    if model_id is None or file_name is None:
        return

    ip_port_str = get_ip_str(ip_port_str)

    # 调用分线程
    t1 = threading.Thread(target=submit_heart_beat_data_func, args=(model_id, file_name, is_enable, ip_port_str,))
    t1.start()



# ----------------- 以上是主要调用的方法 ，这是分割线 -----------------




def submit_trade_data_thread_func(trade_list, ip_port_str, after_submit_event=None):
    data_str = json.dumps(trade_list)
    # print(after_submit_event)
    try:
        write_request_log('info', '-------- 提交【成交】数据，执行开始 time:%s --------' % datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S %f'))

        ip_port_str_old = get_ip_str(None)
        link_str_old = 'http://%s/daily/model/reciveTradeData?data_str=%s' % (ip_port_str_old, data_str)
        response_old = req.get(link_str_old)

        ip_port_str = "nicemoney.nicemind.com:8006"
        link_str = 'http://%s/api/reciveTradeData?data_str=%s' % (ip_port_str, data_str)
        # print('link_str', link_str)
        write_request_log('info', link_str)
        response = req.get(link_str)
        # print('status_code', response.status_code)
        # print('status_code_type', type(response.status_code))
        # print('response_text', response.text)
        status_code = response.status_code
        text = response.text

        if status_code >= 400:
            write_request_log('warning', '请求失败，数据：%s' % data_str)
        else:
            res_errMsg = None
            res_errMsg_str = 'None'
            if text.count('model_id') > 0:# 只要出现model_id，肯定是有错误信息
                temp = json.loads(text, encoding='utf-8')

                if 'errorMsg' in temp and len(temp['errorMsg']) > 0:
                    res_errMsg = json.loads(temp['errorMsg'], encoding='utf-8')
                    res_errMsg_str = str(res_errMsg)


            if after_submit_event is not None:
                after_submit_event(trade_list, res_errMsg)

            write_request_log('info', '请求成功，返回信息：%s' % res_errMsg_str)


    except Exception as e:
        print('submit_trade_data', e)
        # 记录报错
        write_request_log('error', 'submit_trade_data:' + str(e))

    write_request_log('info', '-------- 提交【成交】数据，执行完毕 time:%s --------' % datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S %f'))


def submit_account_data_thread_func(date, broker_id, account, original_money, lastest_money, ip_port_str):

    try:
        write_request_log('info', '-------- 提交【账号】数据，执行开始 time:%s --------' % datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S %f'))
        link_str = 'http://%s/daily/model/reciveAccountData?date=%s&account=%s&original_money=%s&lastest_money=%s&broker_id=%s' \
                   % (ip_port_str, date, account, original_money, lastest_money, broker_id)

        write_request_log('info', link_str)
        response = req.get(link_str)
        status_code = response.status_code
        text = response.text

        if status_code >= 400:
            write_request_log('warning', '请求失败，数据： date: %s , account: %s' % (date, account))
        else:
            # res_errMsg = None
            res_errMsg_str = 'None'
            if text.count('account') > 0:# 只要出现account，肯定是有错误信息
                temp = json.loads(text, encoding='utf-8')

                if 'errorMsg' in temp and len(temp['errorMsg']) > 0:
                    res_errMsg = json.loads(temp['errorMsg'], encoding='utf-8')
                    res_errMsg_str = str(res_errMsg)


            write_request_log('info', '请求成功，返回信息：%s' % res_errMsg_str)

    except Exception as e:
        print('submit_trade_data', e)
        # 记录报错
        write_request_log('error', 'submit_trade_data：' + str(e))

    write_request_log('info', '-------- 提交【账号】数据，执行结束 time:%s --------' % datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S %f'))


def submit_heart_beat_data_func(model_id, file_name, is_enable, ip_port_str):
    try:
        write_request_log('info', '-------- 提交成交【心跳】数据，执行开始 time:%s --------' % datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S %f'))

        is_enable_param_str = '&is_enable=%s' % str(is_enable) if is_enable is not None else ''
        link_str = 'http://%s/daily/model/reciveHeartBeat?model_id=%s&file_name=%s%s' \
                   % (ip_port_str, model_id, file_name, is_enable_param_str)

        write_request_log('info', link_str)
        response = req.get(link_str)
        status_code = response.status_code
        text = response.text

        if status_code >= 400:
            write_request_log('warning', '请求失败，数据： model_id: %s , file_name: %s' % (model_id, file_name))
        else:
            # res_errMsg = None
            res_errMsg_str = 'None'
            temp = json.loads(text, encoding='utf-8')

            if 'errorMsg' in temp:
                res_errMsg_str = temp['errorMsg']


            write_request_log('info', '请求成功，返回信息：%s' % res_errMsg_str)

    except Exception as e:
        print('submit_trade_data', e)
        # 记录报错
        write_request_log('error', 'submit_trade_data：' + str(e))

    write_request_log('info', '-------- 提交成交【心跳】数据，执行结束 time:%s --------' % datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S %f'))


def get_ip_str(ip_port_str=None):
    if ip_port_str is None:
        ip_port_str = 'nicemoney.nicemind.com:8003'

    return ip_port_str


def write_request_log_old(level, msg):
    '''
    记录日志
    :param level: 目前只需要info，error，warning三种级别
    :param msg: 需要记录的信息
    :return:
    '''
    LOG_FORMAT = "[%(levelname)s] - %(asctime)s - %(message)s"
    dir_name = get_folder_path('submit_logs')

    if not os.path.exists(dir_name):
        os.mkdir(dir_name)


    filename = '%s/submit_trade_data_%s.log' % (dir_name, datetime.datetime.now().strftime('%Y-%m-%d'))
    logging.basicConfig(filename=filename, level=logging.DEBUG, format=LOG_FORMAT)
    # logging.debug("This is a debug log.")
    # logging.info("This is a info log.")
    # logging.warning("This is a warning log.")
    # logging.error("This is a error log.")
    # logging.critical("This is a critical log.")

    # 基本上这三种够用了
    if level == 'info':
        logging.info(msg)
    elif level == 'error':
        logging.error(msg)
    elif level == 'warning':
        logging.warning(msg)


def write_request_log(level, msg):
    global logMgr

    # 基本上这三种够用了
    if level == 'info':
        logMgr.info(msg)
    elif level == 'error':
        logMgr.error(msg)
    elif level == 'warning':
        logMgr.warning(msg)


class LogMgr:
    def __init__(self):
        LOG_FORMAT = "[%(levelname)s] - %(asctime)s - %(message)s"
        dir_name = get_folder_path('submit_logs')

        if not os.path.exists(dir_name):
            os.mkdir(dir_name)

        filename = '%s/submit_trade_data_%s.log' % (dir_name, datetime.datetime.now().strftime('%Y-%m-%d'))

        self.LOG = logging.getLogger('submit_logs')
        loghdlr1 = logging.handlers.RotatingFileHandler(filename, "a", 0, 1, encoding='utf-8')
        fmt1 = logging.Formatter(LOG_FORMAT, "%Y-%m-%d %H:%M:%S")
        loghdlr1.setFormatter(fmt1)
        self.LOG.addHandler(loghdlr1)
        self.LOG.setLevel(logging.DEBUG)

    def error(self, msg):
        if self.LOG is not None:
            self.LOG.error(msg)

    def info(self, msg):
        if self.LOG is not None:
            self.LOG.info(msg)

    def warning(self, msg):
        if self.LOG is not None:
            self.LOG.warning(msg)


# 日志类
logMgr = LogMgr()


if __name__ == '__main__':
    # trade_list = [{"broker_id":"9999","direction":"buy","instrument_id":"IF1905","investor_id":"000000"
    #                   ,"model_id":"IF_m1_a_99_v1.0","price":3689,"trade_id":"1236","trade_time":"2019-05-16 13:10:34"
    #                   ,"volume":3}
    #     ,{"broker_id":"9999","direction":"sell","instrument_id":"IF1905"
    #                     ,"investor_id":"000000","model_id":"IF_m1_a_99_v1.0","price":3680,"trade_id":"1237"
    #                     ,"trade_time":"2019-05-16 13:13:34","volume":1,"close_trade_id":"1236"}
    #     , {"broker_id": "9999", "direction": "sell", "instrument_id": "IF1905"
    #                   , "investor_id": "000000", "model_id": "IF_m1_a_99_v1.0", "price": 3680, "trade_id": "1238"
    #                   , "trade_time": "2019-05-16 13:13:34", "volume": 1, "close_trade_id": "1236"}
    #     , {"broker_id": "9999", "direction": "sell", "instrument_id": "IF1905"
    #                   , "investor_id": "000000", "model_id": "IF_m1_a_99_v1.0", "price": 3680, "trade_id": "1239"
    #                   , "trade_time": "2019-05-16 13:13:34", "volume": 1, "close_trade_id": "1236"}
    #     , {"broker_id": "9999", "direction": "sell", "instrument_id": "IF1905"
    #                   , "investor_id": "000000", "model_id": "IF_m1_a_99_v1.0", "price": 3680, "trade_id": "1240"
    #                   , "trade_time": "2019-05-16 13:13:34", "volume": 10}
    #     , {"broker_id": "9999", "direction": "buy", "instrument_id": "IF1905"
    #                   , "investor_id": "000000", "model_id": "IF_m1_a_99_v1.0", "price": 3670, "trade_id": "1241"
    #                   , "trade_time": "2019-05-16 13:13:34", "volume": 5, "close_trade_id": "1240"}
    #     , {"broker_id": "9999", "direction": "buy", "instrument_id": "IF1905"
    #                   , "investor_id": "000000", "model_id": "IF_m1_a_99_v1.0", "price": 3670, "trade_id": "1242"
    #                   , "trade_time": "2019-05-16 13:13:34", "volume": 5, "close_trade_id": "1240"}
    #               ]

    # 新添加的字段：instrument_name（合约名称，支持股票、比特币等）、category（分类：stock、future、exchange、digital）、
    # trade_list = [{"direction": "buy", "instrument_id": "IF1909", "instrument_name": "IF1909"
    #             , "model_id": "IF_m1_a_99_v1.0", "price": 3647, "trade_id": "1236", "trade_time": "2019-08-15 13:10:34"
    #             , "volume": 1, "category": "future"}]

    trade_list = [{"direction": "buy", "instrument_id": "IF1909", "instrument_name": "IF1909"
                      , "model_id": "IF_m1_a_99_v1.0", "price": 3647, "trade_id": "1237",
                   "trade_time": "2019-08-15 13:15:34"
                      , "volume": 1, "category": "future"}]

    def test_event(trade_list_back, res_errMsg):
        if res_errMsg is None:
            return

        success_list = []
        for err in res_errMsg:
            for trade in trade_list_back:
                if trade["model_id"] == err["model_id"] and trade["trade_id"] == err["trade_id"]:
                    continue

                success_list.append(trade)



        print('back_list', trade_list_back)
        print('back_msg', res_errMsg)
        print('back_msg_type', type(res_errMsg))

    # 交易记录的示范例子
    # submit_trade_data(trade_list, test_event)
    submit_trade_data(trade_list, ip_port_str="nicemoney.nicemind.com:8006")


    # 账号信息的示范例子    模拟盘必须是9999
    # submit_account_data(date='2019-07-10', broker_id='9999', account='069775', original_money=1684164.00, lastest_money=1688164.00, ip_port_str="114.67.95.193:8003")


    # 提交心跳记录的例子，有三步：
    # 第一步：启用（关键是is_enable给True的值），即注册通知系统进行监控我这个程序，在文件运行时调用一次
    # submit_heart_beat_data(model_id='test_model_id', file_name='robo_buy.py', is_enable=True)
    # 第二步：每间隔5-10秒左右提交一次心跳记录，不用给参数is_enable
    # submit_heart_beat_data(model_id='test_model_id', file_name='robo_buy.py')
    # 第三步：停用（关键是is_enable给False的值），即注销通知系统进行监控我这个程序，在计划停止运行程序前调用一次
    # submit_heart_beat_data(model_id='test_model_id', file_name='robo_buy.py', is_enable=False)

    # for i in range(500):
    #     submit_heart_beat_data(model_id='test_model_id', file_name='robo_buy.py')
    #     print('时间：', datetime.datetime.now())
    #     print('active_count', threading.active_count())
    #     time.sleep(0.1)
