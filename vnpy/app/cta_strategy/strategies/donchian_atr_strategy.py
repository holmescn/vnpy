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

    donchian_window = 6
    atr_length = 23
    atr_ma_length = 14
    trailing_percent = 0.1

    donchian_up = 0
    donchian_down = 0

    parameters = list(BaseAtrStrategy.parameters)
    parameters.extend(["donchian_window"])

    def on_pos_zero(self, bar: BarData):
        dema_array = talib.DEMA(self.am.close, self.donchian_window)
        self.donchian_up, self.donchian_down = self.am.donchian(self.donchian_window)
        if dema_array[-2] < dema_array[-1] and bar.high_price >= self.donchian_up:
            self.buy(bar.close_price, self.volume)
        elif dema_array[-2] > dema_array[-1] and bar.low_price <= self.donchian_down:
            self.short(bar.close_price, self.volume)
