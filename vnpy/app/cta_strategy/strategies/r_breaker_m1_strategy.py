from vnpy.app.cta_strategy import (
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


class RBreakerM1Strategy(BaseStrategy):
    model_id = "m1_02_RBreakerRaw_v1.0"

    setup_coef = 0.35
    break_coef = 0.25
    enter_coef1 = 1.07
    enter_coef2 = 0.07
    trailing_percent = 0.07

    parameters = list(BaseStrategy.parameters)
    parameters.extend([
        'setup_coef',
        'break_coef',
        'enter_coef1',
        'enter_coef2',
        'trailing_percent'
    ])

    symbol_parameters = {
        # 2019-09-01 2019-10-25 32.02%
        'BTCUSDT.OKEX': {
            'break_coef': 0.3,
            'enter_coef1': 1.3,
            'enter_coef2': 0.2,
            'setup_coef': 0.55,
            'trailing_percent': 6,
        },
        # 2019-09-01 2019-10-25 30.59%
        'BCHUSDT.OKEX': {
            'break_coef': 0.25,
            'enter_coef1': 0.7,
            'enter_coef2': 0.3,
            'setup_coef': 0.85,
            'trailing_percent': 7
        },
        # 2019-09-01 2019-10-25 32.85%
        'BSVUSDT.OKEX': {
            'break_coef': 0.75,
            'enter_coef1': 1.35,
            'enter_coef2': 0.3,
            'setup_coef': 0.4,
            'trailing_percent': 5
        },
        # 2019-09-01 2019-10-25 45.39%
        'ETHUSDT.OKEX': {
            'break_coef': 0.7,
            'enter_coef1': 1.3,
            'enter_coef2': 0.95,
            'setup_coef': 0.5,
            'trailing_percent': 10
        },
        # 2019-09-01 2019-10-25 28.62%
        'ETCUSDT.OKEX': {
            'break_coef': 0.3,
            'enter_coef1': 1.3,
            'enter_coef2': 0.1,
            'setup_coef': 0.65,
            'trailing_percent': 6
        },
        # 2019-09-01 2019-10-25 49.08%
        'EOSUSDT.OKEX': {
            'break_coef': 0.6,
            'enter_coef1': 0.85,
            'enter_coef2': 0.75,
            'setup_coef': 0.6,
            'trailing_percent': 9
        },
        # 2019-09-01 2019-10-25 33.57%
        'LTCUSDT.OKEX': {
            'break_coef': 0.3,     
            'enter_coef1': 1.15,   
            'enter_coef2': 0.5,    
            'setup_coef': 0.55,    
            'trailing_percent': 5.1
        },
        # 2019-09-01 2019-10-25 17.73%
        'DASHUSDT.OKEX': {
            'break_coef': 0.9,
            'enter_coef1': 1.4,
            'enter_coef2': 0.1,
            'setup_coef': 0.85,
            'trailing_percent': 5.6
        }
    }

    def __init__(self, cta_engine, strategy_name, vt_symbol, setting):
        super(RBreakerM1Strategy, self).__init__(
            cta_engine, strategy_name, vt_symbol, setting
        )
    
        self.intra_trade_high = 0
        self.intra_trade_low = 0

        self.buy_break = 0   # 突破买入价
        self.sell_setup = 0  # 观察卖出价
        self.sell_enter = 0  # 反转卖出价
        self.buy_enter = 0   # 反转买入价
        self.buy_setup = 0   # 观察买入价
        self.sell_break = 0  # 突破卖出价

        # 昨日開高低收
        self.day_high = 0
        self.day_open = 0
        self.day_close = 0
        self.day_low = 0
        self.day_counter = 0

        self.bg = BarGenerator(self.on_bar)
        self.am = ArrayManager()

    def on_tick(self, tick: TickData):
        self.bg.update_tick(tick)

    def on_bar(self, bar: BarData):
        super(RBreakerM1Strategy, self).on_bar(bar)
        self.cancel_all()

        self.am.update_bar(bar)
        if not self.am.inited:
            return

        if self.day_counter % 720 == 0:
            if self.day_counter >= 720:
                self.buy_setup = self.day_low - self.setup_coef*(self.day_high - self.day_close)
                self.sell_setup = self.day_high + self.setup_coef*(self.day_close - self.day_low)
                self.buy_enter = (self.enter_coef1/2)*(self.day_high + self.day_low) - self.enter_coef2*self.day_high
                self.sell_enter = (self.enter_coef1/2)*(self.day_high + self.day_low) - self.enter_coef2*self.day_low
                self.buy_break = self.sell_setup + self.break_coef*(self.sell_setup - self.buy_setup)
                self.sell_break = self.buy_setup + self.break_coef*(self.sell_setup - self.buy_setup)

            self.day_open = bar.open_price
            self.day_high = bar.high_price
            self.day_low = bar.low_price
            self.day_close = bar.close_price
        else:
            self.day_high = max(self.day_high, bar.high_price)
            self.day_low = min(self.day_low, bar.low_price)
            self.day_close = bar.close_price

        self.day_counter += 1
        if self.day_counter <= 720:
            return

        if self.pos == 0:
            self.intra_trade_high = bar.high_price
            self.intra_trade_low = bar.low_price

            if bar.high_price > self.sell_setup and bar.close_price > self.sell_setup:
                self.buy(self.buy_break, self.volume(2.0), stop=True)
            elif bar.high_price > self.sell_setup and bar.close_price < self.sell_setup:
                self.short(self.sell_enter, self.volume(2.0), stop=True)
            elif bar.low_price < self.buy_setup and bar.close_price < self.buy_setup:
                self.short(self.sell_break, self.volume(2.0), stop=True)
            elif bar.low_price < self.buy_setup and bar.close_price > self.buy_setup:
                self.buy(self.buy_enter, self.volume(2.0), stop=True)

        elif self.pos > 0:
            self.intra_trade_high = max(self.intra_trade_high, bar.high_price)
            self.intra_trade_low = bar.low_price

            long_stop = self.intra_trade_high * (1 - self.trailing_percent / 100)
            self.sell(long_stop, abs(self.pos), stop=True)

        elif self.pos < 0:
            self.intra_trade_high = bar.high_price
            self.intra_trade_low = min(self.intra_trade_low, bar.low_price)

            short_stop = self.intra_trade_low * (1 + self.trailing_percent / 100)
            self.cover(short_stop, abs(self.pos), stop=True)

        self.put_event()
