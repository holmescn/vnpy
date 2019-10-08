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


class TemaAtrStrategy(BaseAtrStrategy):
    """TEMA/ATR Strategy"""
    model_id = "m1_TEMA_ATR_v1.0"

    tema_length = 15
    atr_length = 22
    atr_ma_length = 10
    trailing_percent = 0.9

    rsi_value = 0
    rsi_buy = 0
    rsi_sell = 0

    parameters = list(BaseAtrStrategy.parameters)
    parameters.extend(["tema_length"])

    def on_pos_zero(self, bar: BarData):
        tema_array = talib.TEMA(self.am.close, self.tema_length)
        if self.atr_value > self.atr_ma:
            if tema_array[-3] > tema_array[-2] < tema_array[-1]:
                self.buy(bar.close_price, self.volume)
            elif tema_array[-3] < tema_array[-2] > tema_array[-1]:
                self.short(bar.close_price, self.volume)
