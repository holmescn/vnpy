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


class BollChannelCciStrategy(BaseStrategy):
    model_id = "m1_02_BollChannel-CCI_v1.0"

    boll_window = 18
    boll_dev = 3.4
    cci_window = 10
    atr_window = 30
    sl_multiplier = 5.2

    parameters = list(BaseStrategy.parameters)
    parameters.extend([
        "boll_window", "boll_dev", "cci_window",
        "atr_window", "sl_multiplier"
    ])
    symbol_parameters = {
        'BTCUSDT.OKEX': {
            'boll_window': 19,
            'boll_dev': 7,
            'cci_window': 30,
            'atr_window': 35,
            'sl_multiplier': 11,
        },
        # 'BCHUSDT.OKEX': {
        # },
        # 'BSVUSDT.OKEX': {
        # },
        # 'ETHUSDT.OKEX': {
        # },
        # 'ETCUSDT.OKEX': {
        # },
        # 'EOSUSDT.OKEX': {
        # },
        # 'LTCUSDT.OKEX': {
        # },
        # 'DASHUSDT.OKEX': {
        # }
    }

    def __init__(self, cta_engine, strategy_name, vt_symbol, setting):
        """"""
        super(BollChannelCciStrategy, self).__init__(
            cta_engine, strategy_name, vt_symbol, setting
        )
        self._boll_window = self.boll_window
        self._boll_dev = self.boll_dev
        self._cci_window = self.cci_window
        self._atr_window = self.atr_window
        self._sl_multiplier = self.sl_multiplier

        if vt_symbol in self.symbol_parameters:
            params = self.symbol_parameters[vt_symbol]
            self._boll_window = params['boll_window']
            self._boll_dev = params['boll_dev']
            self._cci_window = params['cci_window']
            self._atr_window = params['atr_window']
            self._sl_multiplier = params['sl_multiplier']

        self.intra_trade_high = 0
        self.intra_trade_low = 0

        self.bg = BarGenerator(self.on_bar, 15, self.on_15min_bar)
        self.am = ArrayManager()

    def on_tick(self, tick: TickData):
        """
        Callback of new tick data update.
        """
        self.bg.update_tick(tick)

    def on_bar(self, bar: BarData):
        """
        Callback of new bar data update.
        """
        super(BollChannelCciStrategy, self).on_bar(bar)
        self.bg.update_bar(bar)

    def on_15min_bar(self, bar: BarData):
        """"""
        self.cancel_all()

        am = self.am
        am.update_bar(bar)
        if not am.inited:
            return

        boll_up, boll_down = am.boll(self._boll_window, self._boll_dev)
        cci_value = am.cci(self._cci_window)
        atr_value = am.atr(self._atr_window)

        if self.pos == 0:
            self.intra_trade_high = bar.high_price
            self.intra_trade_low = bar.low_price

            if cci_value > 0:
                self.buy(boll_up, self.volume, stop=True)
            elif cci_value < 0:
                self.short(boll_down, self.volume, stop=True)

        elif self.pos > 0:
            self.intra_trade_high = max(self.intra_trade_high, bar.high_price)
            self.intra_trade_low = bar.low_price

            long_stop = self.intra_trade_high - atr_value * self._sl_multiplier
            self.sell(long_stop, abs(self.pos), stop=True)

        elif self.pos < 0:
            self.intra_trade_high = bar.high_price
            self.intra_trade_low = min(self.intra_trade_low, bar.low_price)

            short_stop = self.intra_trade_low + atr_value * self._sl_multiplier
            self.cover(short_stop, abs(self.pos), stop=True)

        self.put_event()
