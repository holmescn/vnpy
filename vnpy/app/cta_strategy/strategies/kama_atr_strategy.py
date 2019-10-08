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


class KamaAtrStrategy(BaseAtrStrategy):
    """KAMA/ATR Strategy"""
    model_id = "m1_KAMA_ATR_v1.0"

    kama_length = 15
    atr_length = 22
    atr_ma_length = 10
    trailing_percent = 0.9

    parameters = list(BaseAtrStrategy.parameters)
    parameters.extend(["kama_length"])

    def on_pos_zero(self, bar: BarData):
        kama_array = talib.KAMA(self.am.close, self.kama_length)
        if self.atr_value > self.atr_ma:
            if kama_array[-3] > kama_array[-2] < kama_array[-1]:
                self.buy(bar.close_price, self.volume)
            elif kama_array[-3] < kama_array[-2] > kama_array[-1]:
                self.short(bar.close_price, self.volume)
