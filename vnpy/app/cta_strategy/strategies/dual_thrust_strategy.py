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
    model_id = "m1_02_DualThrust_v1.0"

    k1 = 0.6
    k2 = 0.7

    parameters = list(BaseStrategy.parameters)
    parameters.extend(["k1", "k2"])

    symbol_parameters = {
        # 2019-09-01 2019-10-25 32.24%
        'BTCUSDT.OKEX': {
            'k1': 0.94,
            'k2': 0.44
        },
        # 2019-09-01 2019-10-25 22.76%
        'BCHUSDT.OKEX': {
            'k1': 0.96,
            'k2': 0.28
        },
        # 2019-09-01 2019-10-25 21.03%
        'BSVUSDT.OKEX': {
            'k1': 0.25,
            'k2': 0.16
        },
        # 2019-09-01 2019-10-25 39.38%
        'ETHUSDT.OKEX': {
            'k1': 0.17,
            'k2': 0.41
        },
        # 2019-09-01 2019-10-25 23.53%
        'ETCUSDT.OKEX': {
            'k1': 0.48,
            'k2': 0.14
        },
        # 2019-09-01 2019-10-25 35.21%
        'EOSUSDT.OKEX': {
            'k1': 0.35,
            'k2': 0.65
        },
        # 2019-09-01 2019-10-25 17%
        'LTCUSDT.OKEX': {
            'k1': 0.71,
            'k2': 0.14
        },
        # 2019-09-01 2019-10-25 8.78%
        'DASHUSDT.OKEX': {
            'k1': 0.35,
            'k2': 0.03
        }
    }

    def __init__(self, cta_engine, strategy_name, vt_symbol, setting):
        super(DualThrustStrategy, self).__init__(
            cta_engine, strategy_name, vt_symbol, setting
        )
        if vt_symbol in self.symbol_parameters:
            params = self.symbol_parameters[vt_symbol]
            self.k1 = params['k1']
            self.k2 = params['k2']

        self.last_bar = None

        self.day_open = 0
        self.day_high = 0
        self.day_low = 0

        self.range = 0
        self.long_entry = 0
        self.short_entry = 0
        self.exit_time = time(hour=14, minute=55)

        self.long_entered = False
        self.short_entered = False

        self.bg = BarGenerator(self.on_bar)
        self.am = ArrayManager()

    def on_tick(self, tick: TickData):
        self.bg.update_tick(tick)

    def on_bar(self, bar: BarData):
        super(DualThrustStrategy, self).on_bar(bar)
        self.cancel_all()

        if self.last_bar is None:
            self.last_bar = bar
            return

        if self.last_bar.datetime.date() != bar.datetime.date():
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

        if self.pos == 0:
            if bar.close_price > self.day_open:
                if not self.long_entered:
                    self.buy(self.long_entry, self.volume(1.5), stop=True)
            else:
                if not self.short_entered:
                    self.short(self.short_entry, self.volume(1.5), stop=True)

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

        self.last_bar = bar
        self.put_event()
