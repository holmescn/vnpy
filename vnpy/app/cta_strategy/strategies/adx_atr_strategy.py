from vnpy.app.cta_strategy import (
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


class AdxAtrStrategy(BaseAtrStrategy):
    """ADX/ATR Strategy"""
    model_id = "m1_ADX_ATR_v1.0"

    adx_length = 14
    atr_length = 22
    atr_ma_length = 10
    trailing_percent = 0.9

    adx_value = 0

    parameters = ["atr_length", "atr_ma_length", "trailing_percent", "adx_length"]

    def on_pos_zero(self, bar: BarData):
        ma20_array = self.am.sma(20, array=True)
        self.adx_value = self.am.adx(self.adx_length)
        if self.atr_value > self.atr_ma and self.adx_value > 25:
            if ma20_array[-1] > ma20_array[-2]:
                self.buy(bar.close_price, self.fixed_size)
            elif ma20_array[-1] < ma20_array[-2]:
                self.short(bar.close_price, self.fixed_size)

