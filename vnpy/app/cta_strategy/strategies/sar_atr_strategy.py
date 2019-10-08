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


class SarAtrStrategy(BaseAtrStrategy):
    """SAR/ATR Strategy"""
    model_id = "m1_SAR_ATR_v1.0"

    sar_k1 = 0.02
    sar_k2 = 0.2
    atr_length = 22
    atr_ma_length = 10
    trailing_percent = 0.9

    rsi_value = 0
    rsi_buy = 0
    rsi_sell = 0

    parameters = list(BaseAtrStrategy.parameters)
    parameters.extend(["sar_k1", "sar_k2"])

    def on_pos_zero(self, bar: BarData):
        sar_array = talib.SAR(self.am.high, self.am.low, self.sar_k1, self.sar_k2)
        if self.atr_value > self.atr_ma:
            if self.am.close[-2] < sar_array[-2] and bar.close_price > sar_array[-1]:
                self.buy(bar.close_price, self.volume)
            elif self.am.close[-2] > sar_array[-2] and bar.close_price < sar_array[-1]:
                self.short(bar.close_price, self.volume)
