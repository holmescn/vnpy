from datetime import time
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
from vnpy.app.cta_strategy.base_strategy import BaseStrategy


class DualThrustStrategy(BaseStrategy):
    """Duel Thrust Strategy"""
    model_id = "m1_DualThrust_UNK_v1.0"

    k1 = 0.6
    k2 = 0.7

    bars = []

    day_open = 0
    day_high = 0
    day_low = 0

    range = 0
    long_entry = 0
    short_entry = 0
    exit_time = time(hour=14, minute=55)

    long_entered = False
    short_entered = False

    parameters = list(BaseStrategy.parameters)
    parameters.extend(["k1", "k2"])
    variables = list(BaseStrategy.variables)
    variables.extend(["range", "long_entry", "short_entry"])

    def __init__(self, cta_engine, strategy_name, vt_symbol, setting):
        """"""
        super(DualThrustStrategy, self).__init__(
            cta_engine, strategy_name, vt_symbol, setting
        )

        self.bg = BarGenerator(self.on_bar)
        self.am = ArrayManager()
        self.bars = []

    def on_tick(self, tick: TickData):
        """
        Callback of new tick data update.
        """
        self.bg.update_tick(tick)

    def on_bar(self, bar: BarData):
        """
        Callback of new bar data update.
        """
        super(DualThrustStrategy, self).on_bar(bar)
        self.cancel_all()

        self.bars.append(bar)
        if len(self.bars) <= 2:
            return
        else:
            self.bars.pop(0)
        last_bar = self.bars[-2]

        if last_bar.datetime.date() != bar.datetime.date():
            if self.day_high:
                self.range = self.day_high - self.day_low
                self.long_entry = bar.open_price + self.k1 * self.range
                self.short_entry = bar.open_price - self.k2 * self.range

            self.day_open = bar.open_price
            self.day_high = bar.high_price
            self.day_low = bar.low_price

            self.long_entered = False
            self.short_entered = False
        else:
            self.day_high = max(self.day_high, bar.high_price)
            self.day_low = min(self.day_low, bar.low_price)

        if not self.range:
            return

        if bar.datetime.time() < self.exit_time:
            if self.pos == 0:
                if bar.close_price > self.day_open:
                    if not self.long_entered:
                        self.buy(self.long_entry, self.volume, stop=True)
                else:
                    if not self.short_entered:
                        self.short(self.short_entry, self.volume, stop=True)

            elif self.pos > 0:
                self.long_entered = True

                self.sell(self.short_entry, self.pos, stop=True)

                if not self.short_entered:
                    self.short(self.short_entry, self.pos, stop=True)

            elif self.pos < 0:
                self.short_entered = True

                self.cover(self.long_entry, abs(self.pos), stop=True)

                if not self.long_entered:
                    self.buy(self.long_entry, abs(self.pos), stop=True)

        else:
            if self.pos > 0:
                self.sell(bar.close_price * 0.99, abs(self.pos))
            elif self.pos < 0:
                self.cover(bar.close_price * 1.01, abs(self.pos))

        self.put_event()
