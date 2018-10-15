# encoding: UTF-8

from __future__ import print_function

import json
from abc import abstractmethod, abstractproperty
from datetime import datetime

from typing import Dict

from vnpy.api.okexfuture.OkexFutureApi import *
from vnpy.trader.vtFunction import getJsonPath
from vnpy.trader.vtGateway import *

_orderTypeMap = {
    (constant.DIRECTION_LONG, constant.OFFSET_OPEN): OkexFutureOrderType.OpenLong,
    (constant.DIRECTION_SHORT, constant.OFFSET_OPEN): OkexFutureOrderType.OpenShort,
    (constant.DIRECTION_LONG, constant.OFFSET_CLOSE): OkexFutureOrderType.CloseLong,
    (constant.DIRECTION_SHORT, constant.OFFSET_CLOSE): OkexFutureOrderType.CloseShort,
}
_orderTypeMapReverse = {v: k for k, v in _orderTypeMap.items()}

_contractTypeMap = {
    'THISWEEK': OkexFutureContractType.ThisWeek,
    'NEXTWEEK': OkexFutureContractType.NextWeek,
    'QUARTER': OkexFutureContractType.Quarter,
}
_contractTypeMapReverse = {v: k for k, v in _contractTypeMap.items()}

_remoteSymbols = {
    OkexFutureSymbol.BTC,
    OkexFutureSymbol.LTC,
    OkexFutureSymbol.ETH,
    OkexFutureSymbol.ETC,
    OkexFutureSymbol.BCH,
}

# symbols for ui,
# keys:给用户看的symbols : f"{internalSymbol}_{contractType}"
# values: API接口使用的symbol和contractType字段
_symbolsForUi = {(remoteSymbol.upper() + '_' + upperContractType.upper()): (remoteSymbol, remoteContractType)
                 for remoteSymbol in _remoteSymbols
                 for upperContractType, remoteContractType in
                 _contractTypeMap.items()}  # type: Dict[str, List[str, str]]
_symbolsForUiReverse = {v: k for k, v in _symbolsForUi.items()}


#----------------------------------------------------------------------
def localOrderTypeToRemote(direction, offset):  # type: (str, str)->str
    return _orderTypeMap[(direction, offset)]


#----------------------------------------------------------------------
def remoteOrderTypeToLocal(orderType):  # type: (str)->(str, str)
    """
    :param orderType:
    :return: direction, offset
    """
    return _orderTypeMapReverse[orderType]


#----------------------------------------------------------------------
def localContractTypeToRemote(localContractType):
    return _contractTypeMap[localContractType]


#----------------------------------------------------------------------
def remoteContractTypeToLocal(remoteContractType):
    return _contractTypeMapReverse[remoteContractType]


#----------------------------------------------------------------------
def localSymbolToRemote(symbol):  # type: (str)->(OkexFutureSymbol, OkexFutureContractType)
    """
    :return: remoteSymbol, remoteContractType
    """
    return _symbolsForUi[symbol]


#----------------------------------------------------------------------
def remoteSymbolToLocal(remoteSymbol, localContractType):
    return remoteSymbol.upper() + localContractType


########################################################################
class VnpyGateway(VtGateway):
    """
    每个gateway有太多重复代码，难以拓展和维护。
    于是我设计了这个类，将重复代码抽取出来，简化gateway的实现
    """
    
    #----------------------------------------------------------------------
    def __init__(self, eventEngine):
        super(VnpyGateway, self).__init__(eventEngine, self.gatewayName)
    
    #----------------------------------------------------------------------
    @abstractproperty
    def gatewayName(self):  # type: ()->str
        return 'VnpyGateway'
    
    #----------------------------------------------------------------------
    def readConfig(self):
        """
        从json文件中读取设置，并将其内容返回为一个dict
        :一个一个return:
        """
        fileName = self.gatewayName + '_connect.json'
        filePath = getJsonPath(fileName, __file__)
        
        try:
            with open(filePath, 'rt') as f:
                return json.load(f)
        except IOError:
            log = VtLogData()
            log.gatewayName = self.gatewayName
            log.logContent = u'读取连接配置出错，请检查'
            # todo: pop a message box is better
            self.onLog(log)
            return
    
    #----------------------------------------------------------------------
    @abstractmethod
    def loadSetting(self):
        """
        载入设置，在connect的时候会被调用到。
        """
        pass


########################################################################
class _Order(object):
    _lastLocalId = 0
    
    #----------------------------------------------------------------------
    def __ini__(self):
        _Order._lastLocalId += 1
        self.localId = str(_Order._lastLocalId)
        self.remoteId = None
        self.vtOrder = None # type: VtOrderData


########################################################################
class OkexFutureGateway(VnpyGateway):
    """OKEX期货交易接口"""
    
    #----------------------------------------------------------------------
    def __init__(self, eventEngine, *_, **__):  # args, kwargs is needed for compatibility
        """Constructor"""
        super(OkexFutureGateway, self).__init__(eventEngine)
        self.apiKey = None  # type: str
        self.apiSecret = None  # type: str
        self.api = OkexFutureRestClient()
        self.leverRate = 1
        self.symbols = []

        self.tradeID = 0
        self._orders = {}  # type: Dict[str, _Order]
        self._remoteIds = {}  # type: Dict[str, _Order]
        
    #----------------------------------------------------------------------
    @property
    def gatewayName(self):
        return 'OkexFutureGateway'
    
    #----------------------------------------------------------------------
    @property
    def exchange(self):  # type: ()->str
        return constant.EXCHANGE_OKEXFUTURE
    
    #----------------------------------------------------------------------
    def loadSetting(self):
        setting = self.readConfig()
        if setting:
            """连接"""
            # 载入json文件
            try:
                # todo: check by predefined settings names and types
                # or check by validator
                self.apiKey = str(setting['apiKey'])
                self.apiSecret = str(setting['secretKey'])
                self.leverRate = setting['leverRate']
                self.symbols = setting['symbols']
            except KeyError:
                log = VtLogData()
                log.gatewayName = self.gatewayName
                log.logContent = u'连接配置缺少字段，请检查'
                self.onLog(log)
                return
    
    #----------------------------------------------------------------------
    def connect(self):
        self.loadSetting()
        self.api.init(self.apiKey, self.apiSecret)
    
    #----------------------------------------------------------------------
    def subscribe(self, subscribeReq):
        """订阅行情"""
        pass

    #----------------------------------------------------------------------
    def _getOrderByLocalId(self, localId):
        return self._orders[localId]

    #----------------------------------------------------------------------
    def _getOrderByRemoteId(self, remoteId):
        return self._remoteIds[remoteId]

    #----------------------------------------------------------------------
    def _saveRemoteId(self, remoteId, myorder):
        myorder.remoteId = remoteId
        self._remoteIds[remoteId] = myorder

    #----------------------------------------------------------------------
    def _genereteLocalOrder(self, symbol, price, volume, direction, offset):
        myorder = _Order()
        localId = myorder.localId
        self._orders[localId] = myorder
        myorder.vtOrder = VtOrderData.createFromGateway(self,
                                                self.exchange,
                                                localId,
                                                symbol,
                                                price,
                                                volume,
                                                direction,
                                                offset)
        return myorder

    #----------------------------------------------------------------------
    def sendOrder(self, vtRequest): # type: (VtOrderReq)->str
        """发单"""
        myorder = self._genereteLocalOrder(vtRequest.symbol,
                                           vtRequest.price,
                                           vtRequest.volume,
                                           vtRequest.direction,
                                           vtRequest.offset)

        remoteSymbol, remoteContractType = localSymbolToRemote(vtRequest.symbol)
        orderType = _orderTypeMap[(vtRequest.priceType, vtRequest.offset)]  # 开多、开空、平多、平空
        userMarketPrice = False
        
        if vtRequest.priceType == constant.PRICETYPE_MARKETPRICE:
            userMarketPrice = True

        self.api.sendOrder(symbol=remoteSymbol,
                           contractType=remoteContractType,
                           orderType=orderType,
                           volume=vtRequest.volume,
                           price=vtRequest.price,
                           useMarketPrice=userMarketPrice,
                           leverRate=self.leverRate,
                           onSuccess=self._onOrderSent,
                           extra=None,
                           )
        
        return myorder.localId

    #----------------------------------------------------------------------
    def cancelOrder(self, vtCancel):  # type: (VtCancelOrderReq)->None
        """撤单"""
        myorder = self._getOrderByLocalId(vtCancel.orderID)
        symbol, contractType = localSymbolToRemote(vtCancel.symbol)
        self.api.cancelOrder(symbol=symbol,
                             contractType=contractType,
                             orderId=myorder.remoteId,
                             onSuccess=self._onOrderCanceled,
                             extra=myorder,
                             )
        # cancelDict: 不存在的，没有localId就没有remoteId，没有remoteId何来cancel
    
    #----------------------------------------------------------------------
    def queryOrders(self, symbol, contractType,
                    status):  # type: (str, str, OkexFutureOrderStatus)->None
        """
        :param symbol:
        :param contractType: 这个参数可以传'THISWEEK', 'NEXTWEEK', 'QUARTER'，也可以传OkexFutureContractType
        :param status: OkexFutureOrderStatus
        :return:
        """
        
        if contractType in _contractTypeMap:
            localContractType = contractType
            remoteContractType = localContractTypeToRemote(localContractType)
        else:
            remoteContractType = contractType
            localContractType = remoteContractTypeToLocal(remoteContractType)

        self.api.queryOrders(symbol=symbol,
                             contractType=remoteContractType,
                             status=status,
                             onSuccess=self._onQueryOrders,
                             extra=localContractType)
    
    #----------------------------------------------------------------------
    def qryAccount(self):
        self.api.queryUserInfo(onSuccess=self._onQueryAccount)
        """查询账户资金"""
        pass
    
    #----------------------------------------------------------------------
    def qryPosition(self):
        """查询持仓"""
        for remoteSymbol in _remoteSymbols:
            for localContractType, remoteContractType in _contractTypeMap.items():
                self.api.queryPosition(remoteSymbol,
                                       remoteContractType,
                                       onSuccess=self._onQueryPosition,
                                       extra=localContractType
                                       )
    
    #----------------------------------------------------------------------
    def close(self):
        """关闭"""
        self.api.stop()

    #----------------------------------------------------------------------
    def _onOrderSent(self, remoteId, myorder):  #type: (str, _Order)->None
        myorder.remoteId = remoteId
        myorder.vtOrder.status = constant.STATUS_NOTTRADED
        self._saveRemoteId(remoteId, myorder)
        self.onOrder(myorder.vtOrder)

    # #----------------------------------------------------------------------
    # def _pushOrderAsTraded(self, order):
    #     trade = VtTradeData()
    #     trade.gatewayName = order.gatewayName
    #     trade.symbol = order.symbol
    #     trade.vtSymbol = order.vtSymbol
    #     trade.orderID = order.orderID
    #     trade.vtOrderID = order.vtOrderID
    #     self.tradeID += 1
    #     trade.tradeID = str(self.tradeID)
    #     trade.vtTradeID = '.'.join([self.gatewayName, trade.tradeID])
    #     trade.direction = order.direction
    #     trade.price = order.price
    #     trade.volume = order.tradedVolume
    #     trade.tradeTime = datetime.now().strftime('%H:%M:%S')
    #     self.onTrade(trade)
        
    #----------------------------------------------------------------------
    @staticmethod
    def _onOrderCanceled(myorder):  #type: (_Order)->None
        myorder.vtOrder.status = constant.STATUS_CANCELLED

    #----------------------------------------------------------------------
    def _onQueryOrders(self, orders, extra):  # type: (List[OkexFutureOrder], Any)->None
        localContractType = extra
        for order in orders:
            remoteId = order.remoteId
        
            if remoteId in self._remoteIds:
                # 如果订单已经缓存在本地，则尝试更新订单状态
                myorder = self._getOrderByRemoteId(remoteId)
            
                # 有新交易才推送更新
                if order.tradedVolume != myorder.vtOrder.tradedVolume:
                    myorder.vtOrder.tradedVolume = order.tradedVolume
                    myorder.vtOrder.status = constant.STATUS_PARTTRADED
                    self.onOrder(myorder.vtOrder)
            else:
                # 本地无此订单的缓存（例如，用其他工具的下单）
                # 缓存该订单，并推送
                symbol = remoteSymbolToLocal(order.symbol, localContractType)
                direction, offset = remoteOrderTypeToLocal(order.orderType)
                myorder = self._genereteLocalOrder(symbol, order.price, order.volume, direction, offset)
                myorder.vtOrder.tradedVolume = order.tradedVolume
                myorder.remoteId = order.remoteId
                self._saveRemoteId(myorder.remoteId, myorder)
                self.onOrder(myorder.vtOrder)
        
            # # 如果该订单已经交易完成，推送交易完成消息
            # # todo: 这样写会导致同一个订单产生多次交易完成消息
            # if order.status == OkexFutureOrderStatus.Finished:
            #     myorder.vtOrder.status = constant.STATUS_ALLTRADED
            #     self._pushOrderAsTraded(myorder.vtOrder)

    #----------------------------------------------------------------------
    def _onQueryAccount(self, infos, _):  # type: (List[OkexFutureUserInfo], Any)->None
        for info in infos:
            vtAccount = VtAccountData()
            vtAccount.accountID = info.easySymbol
            vtAccount.vtAccountID = self.gatewayName + '.' + vtAccount.accountID
            vtAccount.balance = info.accountRights
            vtAccount.margin = info.keepDeposit
            vtAccount.closeProfit = info.profitReal
            vtAccount.positionProfit = info.profitUnreal
            self.onAccount(vtAccount)

    #----------------------------------------------------------------------
    def _onQueryPosition(self, posinfo, extra):  # type: (OkexFuturePosition, Any)->None
        localContractType = extra
        for info in posinfo.holding:
            # 先生成多头持仓
            pos = VtPositionData()
            pos.gatewayName = self.gatewayName
            pos.symbol = remoteSymbolToLocal(pos.symbol, localContractType)
            pos.exchange = self.exchange
            pos.vtSymbol = '.'.join([pos.symbol, pos.exchange])
        
            pos.direction = constant.DIRECTION_NET
            pos.vtPositionName = '.'.join([pos.vtSymbol, pos.direction])
            pos.position = float(info.buyAmount)
        
            self.onPosition(pos)
        
            # 再生存空头持仓
            pos = VtPositionData()
            pos.gatewayName = self.gatewayName
            pos.symbol = remoteSymbolToLocal(pos.symbol, localContractType)
            pos.exchange = self.exchange
            pos.vtSymbol = '.'.join([pos.symbol, pos.exchange])
        
            pos.direction = constant.DIRECTION_SHORT
            pos.vtPositionName = '.'.join([pos.vtSymbol, pos.direction])
            pos.position = float(info.sellAmount)
        
            self.onPosition(pos)
