from vnpy.app.cta_strategy.submit_trade_data import submit_trade_data
from vnpy.trader.object import Offset, Direction, Status
from vnpy.app.cta_strategy import (
    TradeData,
    OrderData,
)
from datetime import datetime


class SubmitTradeMixin(object):
    debug = False
    model_id = ""
    hold_trades = dict()

    def submit_trade(self, trade: TradeData):
        direction = "buy" if trade.direction == Direction.LONG else 'sell'
        trade_list = []
        item = {
            "broker_id": "BITMEX",
            "investor_id": "000000",
            "direction": direction,
            "instrument_id": trade.symbol,
            "instrument_name": trade.vt_symbol,
            "model_id": self.model_id,
            "price": trade.price,
            "trade_id": trade.tradeid,
            "trade_time": datetime.now().strftime("%Y-%m-%d ") + trade.time,
            "volume": trade.volume,
            "category": "digital"
        }

        if trade.offset == Offset.OPEN:
            self.hold_trades[trade.orderid] = trade.tradeid
            trade_list.append(item)
        elif trade.orderid in self.hold_trades:
            item["close_trade_id"] = self.hold_trades[trade.orderid]
            trade_list.append(item)    
        else:
            self.write_log("找不到开仓记录")

        if not self.debug and trade_list:
            submit_trade_data(trade_list)

    def print_order(self, order):
        if order.status in (Status.SUBMITTING, Status.ALLTRADED):
            action = '{} {}'.format(order.offset.value, order.direction.value)
            self.write_log("{} {:.3f} x {}".format(action, order.price, order.volume))

    def print_trade(self, trade):
        action = '{} {}'.format(trade.offset.value, trade.direction.value)
        self.write_log("成交：{} {:.2f} x {}".format(action, trade.price, trade.volume))
