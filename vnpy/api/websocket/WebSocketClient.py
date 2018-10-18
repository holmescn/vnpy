# encoding: UTF-8


########################################################################
import json
import sys

import ssl
import time
import websocket
from threading import Lock, Thread


class WebSocketClient(object):
    """
    Websocket API
    
    实例化之后，应调用start开始后台线程。调用start()函数会自动连接websocket。
    若要终止后台线程，请调用stop()。 stop()函数会顺便断开websocket。
    
    该类默认打包方式为json，若从服务器返回的数据不为json，则会触发onError。
    
    可以覆盖以下回调：
    onConnected
    onDisconnected
    onPacket        # 数据回调，只有在返回的数据帧为text并且内容为json时才会回调
    onError
    
    当然，为了不让用户随意自定义，用自己的init函数覆盖掉原本的init(host)也是个不错的选择。
    
    关于ping：
    在调用start()之后，该类每60s会自动发送一个ping帧至服务器。
    """
    
    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        self.host = None  # type: str

        self.onConnected = self.defaultOnConnected
        self.onDisconnected = self.defaultOnDisconnected
        self.onPacket = self.defaultOnPacket
        self.onError = self.defaultOnError

        self._createConnection = websocket.create_connection
        
        self._ws_lock = Lock()
        self._ws = None  # type: websocket.WebSocket
        
        self._workerThread = None  # type: Thread
        self._pingThread = None  # type: Thread
        self._active = False

    #----------------------------------------------------------------------
    def setCreateConnection(self, func):
        """
        for internal usage
        :param func: a function like websocket.create_connection
        """
        self._createConnection = func

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
        
    #----------------------------------------------------------------------
    def stop(self):
        """
        关闭
        @note 不能从工作线程，也就是websocket的回调中调用
        """
        self._active = False
        self._disconnect()

    #----------------------------------------------------------------------
    def sendPacket(self, dictObj):  # type: (dict)->None
        """发出请求:相当于sendText(json.dumps(dictObj))"""
        return self._getWs().send(json.dumps(dictObj), opcode=websocket.ABNF.OPCODE_TEXT)
    
    #----------------------------------------------------------------------
    def sendText(self, text):  # type: (str)->None
        """发送文本数据"""
        return self._getWs().send(text, opcode=websocket.ABNF.OPCODE_TEXT)
    
    #----------------------------------------------------------------------
    def sendBinary(self, data):  # type: (bytes)->None
        """发送字节数据"""
        return self._getWs().send_binary(data)
    
    #----------------------------------------------------------------------
    def _reconnect(self):
        """重连"""
        if self._active:
            self._disconnect()
            self._connect()
    
    #----------------------------------------------------------------------
    def _connect(self):
        """"""
        self._ws = self._createConnection(self.host, sslopt={'cert_reqs': ssl.CERT_NONE})
        self.onConnected()
    
    #----------------------------------------------------------------------
    def _disconnect(self):
        """
        断开连接
        """
        with self._ws_lock:
            if self._ws:
                self._ws.close()
                self._ws = None

    #----------------------------------------------------------------------
    def _getWs(self):
        with self._ws_lock:
            return self._ws
    
    #----------------------------------------------------------------------
    def _run(self):
        """
        运行，直到stop()被调用
        """

        # todo: onDisconnect
        while self._active:
            try:
                ws = self._getWs()
                if ws:
                    stream = ws.recv()
                    if not stream:                             # recv在阻塞的时候ws被关闭
                        self._reconnect()
                        
                    data = json.loads(stream)
                    self.onPacket(data)
            except websocket.WebSocketConnectionClosedException:  # 在调用recv之前ws就被关闭了
                self._reconnect()
            except:                                            # Python内部错误（onPacket内出错）
                et, ev, tb = sys.exc_info()
                self.onError(et, ev, tb)
                self._reconnect()

    #----------------------------------------------------------------------
    def _runPing(self):
        while self._active:
            try:
                self._ping()
            except:
                et, ev, tb = sys.exc_info()
                # todo: just log this, notifying user is not necessary
                self.onError(et, ev, tb)
            for i in range(60):
                if not self._active:
                    break
                time.sleep(1)
    
    #----------------------------------------------------------------------
    def _ping(self):
        ws = self._getWs()
        if ws:
            ws.send('ping', websocket.ABNF.OPCODE_PING)
    
    #----------------------------------------------------------------------
    @staticmethod
    def defaultOnConnected():
        """
        连接成功回调
        """
        pass
    
    #----------------------------------------------------------------------
    @staticmethod
    def defaultOnDisconnected():
        """
        连接断开回调
        """
        pass
    
    #----------------------------------------------------------------------
    @staticmethod
    def defaultOnPacket(packet):
        """
        数据回调。
        只有在数据为json包的时候才会触发这个回调
        @:param data: dict
        @:return:
        """
        pass
    
    #----------------------------------------------------------------------
    @staticmethod
    def defaultOnError(exceptionType, exceptionValue, tb):
        """Python错误回调"""
        return sys.excepthook(exceptionType, exceptionValue, tb)
