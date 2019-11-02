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


class AtrAdxSmaStrategy(BaseStrategy):
    model_id = "m1_02_ATR-ADX-SMA_v1.0"

    atr_length = 10
    atr_ma_length = 10
    adx_length = 5
    adx_entry_point = 25
    sma_window = 25

    parameters = list(BaseStrategy.parameters)
    parameters.extend(['atr_length', 'atr_ma_length', 'adx_length', 'adx_entry_point', 'sma_window'])

    symbol_parameters = {
        # 2019-09-01 2019-10-25 30.61%
        'BTCUSDT.OKEX': {
            'adx_entry_point': 25,
            'adx_length': 25,
            'atr_length': 50,
            'atr_ma_length': 10,
            'sma_window': 15,
            'trailing_percent': 1
        },
        # 2019-09-01 2019-10-25 28.53%
        'BCHUSDT.OKEX': {
            'adx_entry_point': 15,
            'adx_length': 25,
            'atr_length': 60,
            'atr_ma_length': 15,
            'sma_window': 5,
            'trailing_percent': 1
        },
        # 2019-09-01 2019-10-25 38.34%
        'BSVUSDT.OKEX': {
            'adx_entry_point': 25,
            'adx_length': 5,
            'atr_length': 20,
            'atr_ma_length': 5,
            'sma_window': 12,
            'trailing_percent': 0.4
        },
        # 2019-09-01 2019-10-25 64.23%
        'ETHUSDT.OKEX': {
            'adx_entry_point': 25,
            'adx_length': 15,
            'atr_length': 45,
            'atr_ma_length': 5,
            'sma_window': 7,
            'trailing_percent': 1
        },
        # 2019-09-01 2019-10-25 35.00%
        'ETCUSDT.OKEX': {
            'adx_entry_point': 20,
            'adx_length': 5,
            'atr_length': 35,
            'atr_ma_length': 30,
            'sma_window': 15,
            'trailing_percent': 0.2
        },
        # 2019-09-01 2019-10-25 58.0%
        'EOSUSDT.OKEX': {
            'adx_entry_point': 20,
            'adx_length': 5,
            'atr_length': 10,
            'atr_ma_length': 5,
            'sma_window': 29,
            'trailing_percent': 1.1
        },
        # 2019-09-01 2019-10-25 29.46%
        'LTCUSDT.OKEX': {
            'adx_entry_point': 35,
            'adx_length': 30,
            'atr_length': 40,
            'atr_ma_length': 25,
            'sma_window': 22,
            'trailing_percent': 4.8
        },
        # 2019-09-01 2019-10-25 14.96%
        'DASHUSDT.OKEX': {
            'adx_entry_point': 25,
            'adx_length': 30,
            'atr_length': 60,
            'atr_ma_length': 25,
            'sma_window': 6,
            'trailing_percent': 4.5
        }
    }

    def __init__(self, cta_engine, strategy_name, vt_symbol, setting):
        super(AtrAdxSmaStrategy, self).__init__(
            cta_engine, strategy_name, vt_symbol, setting
        )
        self.intra_trade_high = 0
        self.intra_trade_low = 0

        self.bg = BarGenerator(self.on_bar)
        self.am = ArrayManager()

    def on_tick(self, tick: TickData):
        super(AtrAdxSmaStrategy, self).on_tick(tick)
        self.bg.update_tick(tick)

    def on_bar(self, bar: BarData):
        super(AtrAdxSmaStrategy, self).on_bar(bar)
        self.cancel_all()

        self.am.update_bar(bar)
        if not self.am.inited:
            return

        if self.pos == 0:
            self.intra_trade_high = bar.high_price
            self.intra_trade_low = bar.low_price

            atr_array = self.am.atr(self.atr_length, array=True)
            adx_array = self.am.adx(self.adx_length, array=True)
            sma_array = self.am.sma(self.sma_window, array=True)
            atr_value = atr_array[-1]
            atr_ma = atr_array[-self.atr_ma_length:].mean()

            if atr_value > atr_ma and adx_array[-1] > adx_array[-2] > self.adx_entry_point:
                if sma_array[-3] < sma_array[-2] < sma_array[-1]:
                    self.buy(bar.close_price, self.volume(1.5))
                elif sma_array[-3] > sma_array[-2] > sma_array[-1]:
                    self.short(bar.close_price, self.volume(1.5))

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
