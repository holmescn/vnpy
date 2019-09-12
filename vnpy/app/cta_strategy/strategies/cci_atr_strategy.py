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


class CciAtrStrategy(BaseAtrStrategy):
    """CCI/ATR Strategy"""
    model_id = "m1_CCI_ATR_v1.0"

    cci_length = 5
    atr_length = 22
    atr_ma_length = 10
    trailing_percent = 0.9

    cci_value = 0
    cci_buy = 100
    cci_sell = -100

    parameters = ["atr_length", "atr_ma_length", "cci_length",
                  "trailing_percent"]
    variables = ["atr_value", "atr_ma", "cci_value", "cci_buy", "cci_sell"]

    def on_pos_zero(self, bar: BarData):
        self.cci_value = self.am.cci(self.cci_length)
        if self.atr_value > self.atr_ma:
            if self.cci_value > self.cci_buy:
                self.buy(bar.close_price, self.fixed_size)
            elif self.cci_value < self.cci_sell:
                self.short(bar.close_price, self.fixed_size)
