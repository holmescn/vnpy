import talib
from vnpy.app.cta_strategy import (
    CtaTemplate,
    StopOrder,
    TickData,
    BarData,
    TradeData,
    OrderData,
    BarGenerator,
    ArrayManager,
)
from vnpy.trader.object import Offset, Direction, Status
from vnpy.app.cta_strategy.base_strategy import BaseAtrStrategy


class CmoAtrStrategy(BaseAtrStrategy):
    """CMO/ATR Strategy"""
    model_id = "m1_CMO_ATR_v1.0"

    cmo_length = 20
    atr_length = 22
    atr_ma_length = 10
    trailing_percent = 0.9

    cmo_value = 0
    cmo_buy = 5
    cmo_sell = -5

    parameters = ["atr_length", "atr_ma_length", "cmo_length",
                  "trailing_percent", "fixed_size"]
    variables = ["atr_value", "atr_ma", "cmo_value", "cmo_buy", "cmo_sell", "timestamp"]

    def on_pos_zero(self, bar: BarData):
        cmo_array = talib.CMO(self.am.close, self.cmo_length)
        self.cmo_value = cmo_array[-1]
        if self.atr_value > self.atr_ma:
            if self.cmo_value > self.cmo_buy and cmo_array[-1] > cmo_array[-2]:
                self.buy(bar.close_price, self.fixed_size)
            elif self.cmo_value < self.cmo_buy and cmo_array[-1] < cmo_array[-2]:
                self.short(bar.close_price, self.fixed_size)
