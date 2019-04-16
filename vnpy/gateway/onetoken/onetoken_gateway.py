# encoding: UTF-8
"""
"""

import hashlib
import hmac
import sys
import time
import json
from copy import copy
from datetime import datetime
from threading import Lock
from urllib.parse import urlencode

from requests import ConnectionError

from vnpy.api.rest import Request, RestClient
from vnpy.api.websocket import WebsocketClient
from vnpy.trader.constant import (
    Direction,
    Exchange,
    OrderType,
    Product,
    Status,
    Offset
)
from vnpy.trader.gateway import BaseGateway
from vnpy.trader.object import (
    TickData,
    OrderData,
    TradeData,
    PositionData,
    AccountData,
    ContractData,
    OrderRequest,
    CancelRequest,
    SubscribeRequest,
)
from urllib.parse import urlparse


REST_HOST = 'https://1token.trade/api/v1/trade'

DIRECTION_VT2ONETOKEN = {Direction.LONG: "b", Direction.SHORT: "s"}
DIRECTION_ONETOKEN2VT = {v: k for k, v in DIRECTION_VT2ONETOKEN.items()}


class OnetokenGateway(BaseGateway):
    """
    VN Trader Gateway for 1Token connection
    """

    default_setting = {
        "OT Key": "",
        "OT Secret": "",
        "交易所": "",
        "账户": "",
        "会话数": 3,
        "代理地址": "127.0.0.1",
        "代理端口": 1080,
    }

    def __init__(self, event_engine):
        """Constructor"""
        super(OnetokenGateway, self).__init__(event_engine, "1Token")

        self.rest_api = OnetokenRestApi(self)

    def connect(self, setting: dict):
        """"""
        key = setting["OT Key"]
        secret = setting["OT Secret"]
        session_number = setting["会话数"]
        exchange = setting["交易所"].lower()
        account = setting["账户"]
        proxy_host = setting["代理地址"]
        proxy_port = setting["代理端口"]
        self.rest_api.connect(key, secret, session_number,
                              exchange, account, proxy_host, proxy_port)

    def subscribe(self, req: SubscribeRequest):
        """"""
        pass
        # self.ws_api.subscribe(req)

    def send_order(self, req: OrderRequest):
        """"""
        return self.rest_api.send_order(req)

    def cancel_order(self, req: CancelRequest):
        """"""
        self.rest_api.cancel_order(req)

    def query_account(self):
        """"""
        pass

    def query_position(self):
        """"""
        pass

    def close(self):
        """"""
        self.rest_api.stop()


class OnetokenRestApi(RestClient):
    """
    1Token REST API
    """

    def __init__(self, gateway: BaseGateway):
        """"""
        super(OnetokenRestApi, self).__init__()

        self.gateway = gateway
        self.gateway_name = gateway.gateway_name

        self.key = ""
        self.secret = ""
        self.exchange = ""

        self.order_count = 1_000_000
        self.order_count_lock = Lock()

        self.connect_time = 0
        self.account = ""

    def sign(self, request):
        """
        Generate 1Token signature.
        """
        method = request.method

        endpoint = request.path
        parsed_url = urlparse(endpoint)
        path = parsed_url.path

        nonce = str(int(time.time() * 1e6))
        data = request.data
        json_str = data if data else ''

        message = method + path + nonce + json_str

        signature = hmac.new(bytes(self.secret, 'utf8'), bytes(message, 'utf8'), digestmod=hashlib.sha256).hexdigest()

        headers = {'Api-Nonce': nonce,
                   'Api-Key': self.key,
                   'Api-Signature': signature,
                   'Content-Type': 'application/json'}
        request.headers = headers

        return request

    def connect(
            self,
            key: str,
            secret: str,
            session_number: int,
            exchange: str,
            account: str,
            proxy_host: str,
            proxy_port: int,
    ):
        """
        Initialize connection to REST server.
        """
        self.key = key
        self.secret = secret
        self.exchange = exchange
        self.account = account

        self.connect_time = (
                int(datetime.now().strftime("%y%m%d%H%M%S")) * self.order_count
        )

        self.init(REST_HOST, proxy_host, proxy_port)

        self.start(session_number)

        self.gateway.write_log("REST API启动成功")

        self.query_account()

    def _new_order_id(self):
        with self.order_count_lock:
            self.order_count += 1
            return self.order_count

    def query_account(self):  # get balance and positions at the same time
        """"""
        self.add_request(
            "GET",
            "/{}/{}/info".format(self.exchange, self.account),
            callback=self.on_query_account
        )

    def on_query_account(self, data, request):
        """This is for WS Example"""
        for account_data in data["position"]:
            _type = account_data['type']
            if 'spot' in _type:  #统计balance
                account = AccountData(
                    accountid=account_data["contract"],
                    balance=float(account_data["total_amount"]),
                    frozen=float(account_data["frozen"]),
                    gateway_name=self.gateway_name
                )
                self.gateway.on_account(account)
            elif _type == 'future':  #期货合约
                long_position = PositionData(
                    symbol=account_data["contract"],
                    exchange=Exchange.OKEX,   # todo add Exchange
                    direction=Direction.LONG,
                    volume=account_data['total_amount_long'],
                    frozen=account_data['total_amount_long'] - account_data['available_long'],
                    gateway_name=self.gateway_name,
                    # yd_volume=?
                )
                short_position = PositionData(
                    symbol=account_data["contract"],
                    exchange=Exchange.OKEX,   # todo add Exchange
                    direction=Direction.SHORT,
                    volume=account_data['total_amount_short'],
                    frozen=account_data['total_amount_short'] - account_data['available_short'],
                    gateway_name=self.gateway_name,
                    # yd_volume=?
                )
                self.gateway.on_position(long_position)
                self.gateway.on_position(short_position)

        self.gateway.write_log("账户资金查询成功")
        self.gateway.write_log("账户持仓查询成功")

    def send_order(self, req: OrderRequest):
        """"""
        orderid = str(self.connect_time + self._new_order_id())

        data = {
            'contract': self.exchange + '/' + req.symbol,
            'price': float(req.price),
            "bs": DIRECTION_VT2ONETOKEN[req.direction],
            'amount': float(req.volume),
            'client_oid': orderid
        }

        if req.offset == Offset.CLOSE:
            data['options'] = {'close': True}
        data = json.dumps(data)
        order = req.create_order_data(orderid, self.gateway_name)

        self.add_request(
            method="POST",
            path="/{}/{}/orders".format(self.exchange, self.account),
            callback=self.on_send_order,
            data=data,
            params={},
            extra=order,
            on_failed=self.on_send_order_failed,
            on_error=self.on_send_order_error
        )

        self.gateway.on_order(order)
        return order.vt_orderid

    def cancel_order(self, req: CancelRequest):
        """"""
        params = {
            'client_oid': req.orderid
        }

        self.add_request(
            method="DELETE",
            path="/{}/{}/orders".format(self.exchange, self.account),
            callback=self.on_cancel_order,
            params=params,
            on_error=self.on_cancel_order_error,
            extra=req
        )

    def on_send_order(self, data, request):
        """Websocket will push a new order status"""
        pass

    def on_send_order_failed(self, status_code: str, request: Request):
        """
        Callback when sending order failed on server.
        """
        order = request.extra
        order.status = Status.REJECTED
        self.gateway.on_order(order)

        msg = f"委托失败，状态码：{status_code}，信息：{request.response.text}"
        self.gateway.write_log(msg)

    def on_send_order_error(
            self, exception_type: type, exception_value: Exception, tb, request: Request
    ):
        """
        Callback when sending order caused exception.
        """
        order = request.extra
        order.status = Status.REJECTED
        self.gateway.on_order(order)

        # Record exception if not ConnectionError
        if not issubclass(exception_type, ConnectionError):
            self.on_error(exception_type, exception_value, tb, request)

    def on_cancel_order(self, data, request):
        """Websocket will push a new order status"""
        pass

    def on_cancel_order_error(
            self, exception_type: type, exception_value: Exception, tb, request: Request
    ):
        """
        Callback when cancelling order failed on server.
        """
        # Record exception if not ConnectionError
        if not issubclass(exception_type, ConnectionError):
            self.on_error(exception_type, exception_value, tb, request)
