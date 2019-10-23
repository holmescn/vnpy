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

    dema_length = 20
    atr_length = 29
    atr_ma_length = 30
    trailing_percent = 1.2

    cmo_value = 0
    cmo_buy = 5
    cmo_sell = -5

    parameters = list(BaseAtrStrategy.parameters)
    parameters.extend(["dema_length"])

    def on_pos_zero(self, bar: BarData):
        dema_array = talib.DEMA(self.am.close, self.dema_length)
        if self.atr_value > self.atr_ma:
            if dema_array[-3] > dema_array[-2] < dema_array[-1]:
                self.buy(bar.close_price, self.volume)
            elif dema_array[-3] < dema_array[-2] > dema_array[-1]:
                self.short(bar.close_price, self.volume)
