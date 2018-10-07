# encoding: UTF-8


########################################################################
import json
import ssl
import sys
import time
from abc import abstractmethod
from threading import Thread

import websocket


class WebsocketClient(object):
    """Websocket API"""
    
    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        self.host = None  # type: str
        
        self._ws = None  # type: websocket.WebSocket
        self._workerThread = None  # type: Thread
        self._pingThread = None  # type: Thread
        self._active = False

    #----------------------------------------------------------------------
    def init(self, host):
        self.host = host
    
    #----------------------------------------------------------------------
    def start(self):
        """启动"""
        self._connect()
        
        self._active = True
        self._workerThread = Thread(target=self._run)
        self._workerThread.start()
        
        self._pingThread = Thread(target=self._runPing)
        self._pingThread.start()
        
        self.onConnect()
        
    #----------------------------------------------------------------------
    def stop(self):
        """
        关闭
        @note 不能从工作线程，也就是websocket的回调中调用
        """
        self._active = False
        self._disconnect()

    #----------------------------------------------------------------------
    def sendReq(self, req):  # type: (dict)->None
        """发出请求"""
        return self._ws.send(json.dumps(req), opcode=websocket.ABNF.OPCODE_TEXT)
    
    #----------------------------------------------------------------------
    def sendText(self, text):  # type: (str)->None
        """发出请求"""
        return self._ws.send(text, opcode=websocket.ABNF.OPCODE_TEXT)
    
    #----------------------------------------------------------------------
    def sendData(self, data):  # type: (bytes)->None
        """发出请求"""
        return self._ws.send_binary(data)
    
    #----------------------------------------------------------------------
    def _reconnect(self):
        """重连"""
        self._disconnect()
        self._connect()
    
    #----------------------------------------------------------------------
    def _connect(self):
        """"""
        self._ws = websocket.create_connection(self.host, sslopt={'cert_reqs': ssl.CERT_NONE})
        self.onConnect()
    
    #----------------------------------------------------------------------
    def _disconnect(self):
        """"""
        self._ws.close()
    
    #----------------------------------------------------------------------
    def _run(self):
        """运行"""
        while self._active:
            try:
                stream = self._ws.recv()
                data = json.loads(stream)
                self.onMessage(data)
            except:
                et, ev, tb = sys.exc_info()
                self.onError(et, ev, tb)
                if self._active:
                    self._reconnect()
    
    #----------------------------------------------------------------------
    def _runPing(self):
        while self._active:
            self._ping()
            for i in range(60):
                if not self._active:
                    break
                time.sleep(1)
    
    #----------------------------------------------------------------------
    def _ping(self):
        return self._ws.send('ping', websocket.ABNF.OPCODE_PING)
    
    #----------------------------------------------------------------------
    @abstractmethod
    def onConnect(self):
        """连接回调"""
        pass
    
    #----------------------------------------------------------------------
    @abstractmethod
    def onMessage(self, packet):
        """
        数据回调。
        只有在数据为json包的时候才会触发这个回调
        @:param data: dict
        @:return:
        """
        pass
    
    #----------------------------------------------------------------------
    @abstractmethod
    def onError(self, exceptionType, exceptionValue, tb):
        """错误回调"""
        pass
