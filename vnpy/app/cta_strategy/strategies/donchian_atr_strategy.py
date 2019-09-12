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


class DonchianAtrStrategy(BaseAtrStrategy):
    """Donchian/ATR Strategy"""
    model_id = "m1_Donchian_ATR_v1.0"

    donchian_window = 5
    atr_length = 22
    atr_ma_length = 10
    trailing_percent = 0.9

    donchian_up = 0
    donchian_down = 0

    parameters = ["atr_length", "atr_ma_length", "donchian_window",
                  "trailing_percent"]

    def on_pos_zero(self, bar: BarData):
        dema_array = talib.DEMA(self.am.close, self.donchian_window)
        self.donchian_up, self.donchian_down = self.am.donchian(self.donchian_window)
        if dema_array[-2] < dema_array[-1] and bar.high_price >= self.donchian_up:
            self.buy(bar.close_price, self.fixed_size)
        elif dema_array[-2] > dema_array[-1] and bar.low_price <= self.donchian_down:
            self.short(bar.close_price, self.fixed_size)
