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
from vnpy.app.cta_strategy.base_strategy import BaseAtrStrategy


class AdxAtrStrategy(BaseAtrStrategy):
    """ADX/ATR Strategy"""
    model_id = "m1_ADX_ATR_v1.0"

    adx_length = 21
    sma_window = 20
    atr_length = 37
    atr_ma_length = 46
    trailing_percent = 0.3

    adx_value = 0

    parameters = list(BaseAtrStrategy.parameters)
    parameters.extend(['adx_length', 'sma_window'])

    symbol_parameters = {
        'BTCUSDT.OKEX': {
            'adx_length': 5,
            'sma_length': 28,
            'atr_length': 6,
            'atr_ma_length': 27,
            'trailing_percent': 0.1
        }
    }

    def __init__(self, cta_engine, strategy_name, vt_symbol, setting):
        super(AdxAtrStrategy, self).__init__(
            cta_engine, strategy_name, vt_symbol, setting
        )
        self._adx_length = self.adx_length
        self._sma_length = self.sma_window
        if vt_symbol in self.symbol_parameters:
            params = self.symbol_parameters[vt_symbol]
            self._adx_length = params['adx_length']
            self._sma_length = params['sma_window']
            self._atr_length = params['atr_length']
            self._atr_ma_length = params['atr_ma_length']
            self._trailing_percent = params['trailing_percent']

    def on_pos_zero(self, bar: BarData):
        ma20_array = self.am.sma(self._sma_length, array=True)
        self.adx_value = self.am.adx(self.adx_length)
        if self.atr_value > self.atr_ma and self.adx_value > 25:
            if ma20_array[-3] < ma20_array[-2] < ma20_array[-1]:
                self.buy(bar.close_price, self.volume)
            elif ma20_array[-3] > ma20_array[-2] > ma20_array[-1]:
                self.short(bar.close_price, self.volume)
