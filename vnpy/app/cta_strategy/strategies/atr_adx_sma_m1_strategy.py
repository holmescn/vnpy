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
from vnpy.app.cta_strategy.base_strategy import BaseM1Strategy


class AtrAdxSmaM1Strategy(BaseM1Strategy):
    model_id = "m1_02_ATR-ADX-SMA_v1.0"

    atr_length = 10
    atr_ma_length = 10
    adx_length = 5
    adx_entry_point = 25
    sma_window = 25

    parameters = list(BaseM1Strategy.parameters)
    parameters.extend(['atr_length', 'atr_ma_length', 'adx_length', 'adx_entry_point', 'sma_length'])

    symbol_parameters = {
        'BTCUSDT.OKEX': {
            'atr_length': 10,
            'atr_ma_length': 5,
            'adx_length': 25,
            'adx_entry_point': 25,
            'sma_window': 20,
            'trailing_percent': 1.1
        },
        'BCHUSDT.OKEX': {
            'atr_length': 10,
            'atr_ma_length': 5,
            'adx_length': 25,
            'adx_entry_point': 25,
            'sma_window': 20,
            'trailing_percent': 1.1
        },
        # 'BSVUSDT.OKEX': {
        # },
        # 'ETHUSDT.OKEX': {
        # },
        # 'ETCUSDT.OKEX': {
        # }
    }

    def __init__(self, cta_engine, strategy_name, vt_symbol, setting):
        super(AtrAdxSmaM1Strategy, self).__init__(
            cta_engine, strategy_name, vt_symbol, setting
        )
        self._adx_length = self.adx_length
        self._adx_entry_point = self.adx_entry_point
        self._atr_length = self.atr_length
        self._atr_ma_length = self.atr_ma_length
        self._sma_window = self.sma_window

        if vt_symbol in self.symbol_parameters:
            params = self.symbol_parameters[vt_symbol]
            self._atr_length = params['atr_length']
            self._atr_ma_length = params['atr_ma_length']
            self._adx_length = params['adx_length']
            self._adx_entry_point = params['adx_entry_point']
            self._sma_length = params['sma_window']
            self._trailing_percent = params['trailing_percent']

    def check_entry(self, bar: BarData):
        atr_array = self.am.atr(self._atr_length, array=True)
        adx_array = self.am.adx(self._adx_length, array=True)
        sma_array = self.am.sma(self._sma_window, array=True)
        atr_value = atr_array[-1]
        atr_ma = atr_array[-self._atr_ma_length:].mean()

        if atr_value > atr_ma and adx_array[-1] > adx_array[-2] > self._adx_entry_point:
            if sma_array[-3] < sma_array[-2] < sma_array[-1]:
                self.buy(bar.close_price, self.volume)
            elif sma_array[-3] > sma_array[-2] > sma_array[-1]:
                self.short(bar.close_price, self.volume)
