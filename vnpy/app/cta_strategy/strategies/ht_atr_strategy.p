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


class HtAtrStrategy(BaseAtrStrategy):
    """HT Trendline/ATR Strategy"""
    model_id = "m1_HT_ATR_v1.0"

    atr_length = 7
    atr_ma_length = 30
    trailing_percent = 1.4

    def on_pos_zero(self, bar: BarData):
        ht_array = talib.HT_TRENDLINE(self.am.close)
        if self.atr_value > self.atr_ma:
            if ht_array[-3] > ht_array[-2] < ht_array[-1]:
                self.buy(bar.close_price, self.volume)
            elif ht_array[-3] < ht_array[-2] > ht_array[-1]:
                self.short(bar.close_price, self.volume)
