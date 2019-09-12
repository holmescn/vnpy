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


class TrimaAtrStrategy(BaseAtrStrategy):
    """TriMA/ATR Strategy"""
    model_id = "m1_TriMA_ATR_v1.0"

    trima_length = 15
    atr_length = 22
    atr_ma_length = 10
    trailing_percent = 0.9

    rsi_value = 0
    rsi_buy = 0
    rsi_sell = 0

    parameters = ["atr_length", "atr_ma_length", "trima_length",
                  "trailing_percent"]

    def on_pos_zero(self, bar: BarData):
        trima_array = talib.TRIMA(self.am.close, self.trima_length)
        if self.atr_value > self.atr_ma:
            if trima_array[-3] > trima_array[-2] < trima_array[-1]:
                self.buy(bar.close_price, self.fixed_size)
            elif trima_array[-3] < trima_array[-2] > trima_array[-1]:
                self.short(bar.close_price, self.fixed_size)
