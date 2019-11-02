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


class AtrSmaStrategy(BaseStrategy):
    model_id = "m1_02_ATR-SMA_r_v1.0"

    atr_length = 10
    sma_window = 25
    n_atr = 2
    trailing_percent = 0.0

    parameters = list(BaseStrategy.parameters)
    parameters.extend(['atr_length', 'sma_window', 'n_atr', "trailing_percent"])

    symbol_parameters = {
        # 2019-09-01 2019-10-25 37.73%
        'BTCUSDT.OKEX': {
            'atr_length': 15,
            'n_atr': 3.5,
            'sma_window': 25,
            'trailing_percent': 4.9
        },
        # 2019-09-01 2019-10-25 32.25%
        'BCHUSDT.OKEX': {
            'atr_length': 15,
            'n_atr': 7.3,
            'sma_window': 35,
            'trailing_percent': 8.2
        },
        # 2019-09-01 2019-10-25 48.27%
        'BSVUSDT.OKEX': {
            'atr_length': 15,
            'n_atr': 3.0,
            'sma_window': 10,
            'trailing_percent': 15.9
        },
        # 2019-09-01 2019-10-25 55.65%
        'ETHUSDT.OKEX': {
            'atr_length': 40,
            'n_atr': 2.9,
            'sma_window': 35,
            'trailing_percent': 3.6
        },
        # 2019-09-01 2019-10-25 32.25%
        'ETCUSDT.OKEX': {
            'atr_length': 25,
            'n_atr': 9.5,
            'sma_window': 30,
            'trailing_percent': 6.3
        },
        # 2019-09-01 2019-10-25 62.29%
        'EOSUSDT.OKEX': {
            'atr_length': 50,
            'n_atr': 5.6,
            'sma_window': 30,
            'trailing_percent': 8.0
        },
        # 2019-09-01 2019-10-25 33.27%
        'LTCUSDT.OKEX': {
            'atr_length': 45,
            'n_atr': 7.6,
            'sma_window': 55,
            'trailing_percent': 11.5
        },
        # 2019-09-01 2019-10-25 21.42%
        'DASHUSDT.OKEX': {
            'atr_length':30,
            'n_atr': 3.1,
            'sma_window': 30,
            'trailing_percent': 12.6
        }
    }

    def __init__(self, cta_engine, strategy_name, vt_symbol, setting):
        super(AtrSmaStrategy, self).__init__(
            cta_engine, strategy_name, vt_symbol, setting
        )
        self.intra_trade_high = 0
        self.intra_trade_low = 0

        self.bg = BarGenerator(self.on_bar)
        self.am = ArrayManager()

    def on_tick(self, tick: TickData):
        super(AtrSmaStrategy, self).on_tick(tick)
        self.bg.update_tick(tick)

    def on_bar(self, bar: BarData):
        super(AtrSmaStrategy, self).on_bar(bar)
        self.cancel_all()

        self.am.update_bar(bar)
        if not self.am.inited:
            return

        if self.pos == 0:
            self.intra_trade_high = bar.high_price
            self.intra_trade_low = bar.low_price

            atr_value = self.am.atr(self.atr_length)
            sma_value = self.am.sma(self.sma_window)
            up = sma_value + atr_value * self.n_atr
            down = sma_value - atr_value * self.n_atr

            if bar.close_price > up:
                self.short(bar.close_price, self.volume(1.5))
            elif bar.close_price < down:
                self.buy(bar.close_price, self.volume(1.5))

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
