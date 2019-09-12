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


class BollAtrStrategy(BaseAtrStrategy):
    """BOLL/ATR Strategy"""
    model_id = "m1_BOLL_ATR_v1.0"

    boll_window = 18
    boll_dev = 3.4
    atr_length = 22
    atr_ma_length = 10
    trailing_percent = 0.9

    parameters = ["atr_length", "atr_ma_length", "boll_window", "boll_dev",
                  "trailing_percent"]

    def on_pos_zero(self, bar: BarData):
        up, lo = self.am.boll(self.boll_window, self.boll_dev)
        if self.atr_value > self.atr_ma:
            if bar.close_price > up:
                self.buy(bar.close_price, self.fixed_size)
            elif bar.close_price < lo:
                self.short(bar.close_price, self.fixed_size)
