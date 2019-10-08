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


class RsiAtrStrategy(BaseAtrStrategy):
    """RSI/ATR Strategy"""
    model_id = "m1_RSI_ATR_v1.0"

    rsi_length = 5
    rsi_entry = 16
    atr_length = 22
    atr_ma_length = 10
    trailing_percent = 0.9

    rsi_value = 0
    rsi_buy = 0
    rsi_sell = 0

    parameters = list(BaseAtrStrategy.parameters)
    parameters.extend(["rsi_length", "rsi_entry"])
    variables = list(BaseAtrStrategy.variables)
    variables.extend(["rsi_value", "rsi_buy", "rsi_sell"])

    def on_pos_zero(self, bar: BarData):
        self.rsi_value = self.am.rsi(self.rsi_length)
        if self.atr_value > self.atr_ma:
            if self.rsi_value > self.rsi_buy:
                self.buy(bar.close_price, self.volume)
            elif self.rsi_value < self.rsi_sell:
                self.short(bar.close_price, self.volume)
