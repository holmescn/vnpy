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
        # 2019-09-01 2019-10-25
        # 'BTCUSDT.OKEX': {
        # },
        # 2019-09-01 2019-10-25
        # 'BCHUSDT.OKEX': {
        # },
        # 2019-09-01 2019-10-25
        # 'BSVUSDT.OKEX': {
        # },
        # 2019-09-01 2019-10-25
        # 'ETHUSDT.OKEX': {
        # },
        # 2019-09-01 2019-10-25
        # 'ETCUSDT.OKEX': {
        # },
        # 2019-09-01 2019-10-25
        # 'EOSUSDT.OKEX': {
        # },
        # 2019-09-01 2019-10-25
        # 'LTCUSDT.OKEX': {
        # },
        # 2019-09-01 2019-10-25
        # 'DASHUSDT.OKEX': {
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
        self.cancel_all()

        self.am5.update_bar(bar)
        if not self.am5.inited:
            return

        if not self.ma_trend:
            return

        rsi_value = self.am5.rsi(self.rsi_window)

        if self.pos == 0:
            if self.ma_trend > 0 and rsi_value >= self.rsi_long:
                self.buy(bar.close_price, self.volume(2.5))
            elif self.ma_trend < 0 and rsi_value <= self.rsi_short:
                self.short(bar.close_price, self.volume(2.5))

        elif self.pos > 0:
            if self.ma_trend < 0 or rsi_value < 50:
                self.sell(bar.close_price, abs(self.pos))

        elif self.pos < 0:
            if self.ma_trend > 0 or rsi_value > 50:
                self.cover(bar.close_price, abs(self.pos))

        self.put_event()

    def on_15min_bar(self, bar: BarData):
        self.am15.update_bar(bar)
        if not self.am15.inited:
            return

        self.fast_ma = self.am15.sma(self.fast_window)
        self.slow_ma = self.am15.sma(self.slow_window)

        if self.fast_ma > self.slow_ma:
            self.ma_trend = 1
        else:
            self.ma_trend = -1
