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
        # 'BTCUSDT.OKEX': {
        #     'k1': 1.5,
        #     'k2': 0.3
        # },
        # 'BCHUSDT.OKEX': {
        #     'k1': 1.0,
        #     'k2': 0.4
        # },
        # 'BSVUSDT.OKEX': {
        #     'k1': 1.7,
        #     'k2': 0.5
        # },
        # 'ETHUSDT.OKEX': {
        #     'k1': 0.1,
        #     'k2': 0.6
        # },
        # 'ETCUSDT.OKEX': {
        #     'k1': 0.9,
        #     'k2': 0.4
        # },
        # 'EOSUSDT.OKEX': {
        #     'k1': 1.5,
        #     'k2': 0.2
        # },
        # 'LTCUSDT.OKEX': {
        #     'k1': 0.7,
        #     'k2': 0.2
        # },
        # 'DASHUSDT.OKEX': {
        #     'k1': 1.4,
        #     'k2': 0.2
        # }
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

        self.last_bar = bar
        self.put_event()
