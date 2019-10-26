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


class MultiTimeframeStrategy(BaseStrategy):
    model_id = "m5+15_02_RSI-SMA_v1.0"

    rsi_signal = 20
    rsi_window = 14
    fast_window = 5
    slow_window = 20

    parameters = list(BaseStrategy.parameters)
    parameters.extend(["rsi_signal", "rsi_window", "fast_window", "slow_window"])

    symbol_parameters = {
        # 'BTCUSDT.OKEX': {
        #     'atr_length': 10,
        #     'atr_ma_length': 5,
        #     'adx_length': 25,
        #     'adx_entry_point': 25,
        #     'sma_window': 20,
        #     'trailing_percent': 1.1
        # },
        # 'BCHUSDT.OKEX': {
        #     'atr_length': 25,
        #     'atr_ma_length': 20,
        #     'adx_length': 30,
        #     'adx_entry_point': 35,
        #     'sma_window': 15,
        #     'trailing_percent': 9.0
        # },
        # 'BSVUSDT.OKEX': {
        #     'atr_length': 11,
        #     'atr_ma_length': 10,
        #     'adx_length': 25,
        #     'adx_entry_point': 30,
        #     'sma_window': 13,
        #     'trailing_percent': 3.0
        # },
        # 'ETHUSDT.OKEX': {
        #     'atr_length': 4,
        #     'atr_ma_length': 6,
        #     'adx_length': 28,
        #     'adx_entry_point': 28,
        #     'sma_window': 28,
        #     'trailing_percent': 2
        # },
        # 'ETCUSDT.OKEX': {
        #     'atr_length': 15,
        #     'atr_ma_length': 20,
        #     'adx_length': 25,
        #     'adx_entry_point': 25,
        #     'sma_window': 10,
        #     'trailing_percent': 5.5
        # },
        # 'EOSUSDT.OKEX': {
        #     'atr_length': 15,
        #     'atr_ma_length': 5,
        #     'adx_length': 5,
        #     'adx_entry_point': 22,
        #     'sma_window': 10,
        #     'trailing_percent': 1.0
        # },
        # 'LTCUSDT.OKEX': {
        #     'atr_length': 20,
        #     'atr_ma_length': 16,
        #     'adx_length': 24,
        #     'adx_entry_point': 40,
        #     'sma_window': 18,
        #     'trailing_percent': 5.0
        # },
        # 'DASHUSDT.OKEX': {
        #     'atr_length': 6,
        #     'atr_ma_length': 26,
        #     'adx_length': 8,
        #     'adx_entry_point': 20,
        #     'sma_window': 28,
        #     'trailing_percent': 9.0
        # }
    }

    def __init__(self, cta_engine, strategy_name, vt_symbol, setting):
        """"""
        super(MultiTimeframeStrategy, self).__init__(
            cta_engine, strategy_name, vt_symbol, setting
        )

        if vt_symbol in self.symbol_parameters:
            params = self.symbol_parameters[vt_symbol]
            self.rsi_signal = params['rsi_signal']
            self.rsi_window = params['rsi_window']
            self.fast_window = params['fast_window']
            self.slow_window = params['slow_window']

        self.rsi_value = 0
        self.rsi_long = 0
        self.rsi_short = 0
        self.fast_ma = 0
        self.slow_ma = 0
        self.ma_trend = 0

        self.rsi_long = 50 + self.rsi_signal
        self.rsi_short = 50 - self.rsi_signal

        self.bg5 = BarGenerator(self.on_bar, 5, self.on_5min_bar)
        self.am5 = ArrayManager()

        self.bg15 = BarGenerator(self.on_bar, 15, self.on_15min_bar)
        self.am15 = ArrayManager()

    def on_tick(self, tick: TickData):
        """
        Callback of new tick data update.
        """
        self.bg5.update_tick(tick)

    def on_bar(self, bar: BarData):
        """
        Callback of new bar data update.
        """
        super(MultiTimeframeStrategy, self).on_bar(bar)
        self.bg5.update_bar(bar)
        self.bg15.update_bar(bar)

    def on_5min_bar(self, bar: BarData):
        """"""
        self.cancel_all()

        self.am5.update_bar(bar)
        if not self.am5.inited:
            return

        if not self.ma_trend:
            return

        self.rsi_value = self.am5.rsi(self.rsi_window)

        if self.pos == 0:
            if self.ma_trend > 0 and self.rsi_value >= self.rsi_long:
                self.buy(bar.close_price, self.volume * 2.5)
            elif self.ma_trend < 0 and self.rsi_value <= self.rsi_short:
                self.short(bar.close_price, self.volume * 2.5)

        elif self.pos > 0:
            if self.ma_trend < 0 or self.rsi_value < 50:
                self.sell(bar.close_price, abs(self.pos))

        elif self.pos < 0:
            if self.ma_trend > 0 or self.rsi_value > 50:
                self.cover(bar.close_price, abs(self.pos))

        self.put_event()

    def on_15min_bar(self, bar: BarData):
        """"""
        self.am15.update_bar(bar)
        if not self.am15.inited:
            return

        self.fast_ma = self.am15.sma(self.fast_window)
        self.slow_ma = self.am15.sma(self.slow_window)

        if self.fast_ma > self.slow_ma:
            self.ma_trend = 1
        else:
            self.ma_trend = -1
