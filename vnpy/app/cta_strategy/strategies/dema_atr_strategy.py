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


class DemaAtrStrategy(BaseAtrStrategy):
    """DEMA/ATR Strategy"""
    model_id = "m1_DEMA_ATR_v1.0"

    dema_length = 15
    atr_length = 22
    atr_ma_length = 10
    trailing_percent = 0.9

    cmo_value = 0
    cmo_buy = 5
    cmo_sell = -5

    parameters = ["atr_length", "atr_ma_length", "dema_length",
                  "trailing_percent"]

    def on_pos_zero(self, bar: BarData):
        dema_array = talib.DEMA(self.am.close, self.dema_length)
        if self.atr_value > self.atr_ma:
            if dema_array[-3] > dema_array[-2] < dema_array[-1]:
                self.buy(bar.close_price, self.fixed_size)
            elif dema_array[-3] < dema_array[-2] > dema_array[-1]:
                self.short(bar.close_price, self.fixed_size)
