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


class MacdAtrStrategy(BaseAtrStrategy):
    """MACD/ATR Strategy"""
    model_id = "m1_MACD_ATR_v1.0"

    fast_period = 10
    slow_period = 20
    signal_period = 9
    atr_length = 22
    atr_ma_length = 10
    trailing_percent = 0.9

    parameters = list(BaseAtrStrategy.parameters)
    parameters.extend(["fast_period", "slow_period", "signal_period"])

    def on_pos_zero(self, bar: BarData):
        macd, signal, _ = self.am.macd(self.fast_period, self.slow_period, self.signal_period, array=True)
        if self.atr_value > self.atr_ma:
            if macd[-2] < signal[-2] and macd[-1] > signal[-1]:
                self.buy(bar.close_price, self.volume)
            elif macd[-2] > signal[-2] and macd[-1] < signal[-1]:
                self.short(bar.close_price, self.volume)
