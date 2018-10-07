# encoding: UTF-8
import json
import unittest

from Promise import Promise
from vnpy.restful.WebsocketClient import WebsocketClient


class TestWebsocketClient(WebsocketClient):
    
    def __init__(self):
        urlBase = 'wss://echo.websocket.org'
        super(TestWebsocketClient, self).__init__(urlBase)
        self.p = Promise()
    
    def onMessage(self, packet):
        self.p.set_result(packet)
        pass
    
    def onConnect(self):
        pass
    
    def onError(self, exceptionType, exceptionValue, tb):
        self.p.set_exception(exceptionValue)
        pass


class WebsocketClientTest(unittest.TestCase):
    
    def setUp(self):
        self.c = TestWebsocketClient()
        self.c.start()
    
    def tearDown(self):
        self.c.stop()
    
    def test_sendReq(self):
        req = {
            'name': 'val'
        }
        self.c.sendReq(req)
        res = self.c.p.get(3)
        
        self.assertEqual(res, req)
