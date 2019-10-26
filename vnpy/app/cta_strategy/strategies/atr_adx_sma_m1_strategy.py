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
            'atr_ma_length': 2,
            'adx_length': 25,
            'adx_entry_point': 20,
            'sma_window': 30,
            'trailing_percent': 1
        },
        'BCHUSDT.OKEX': {
            'atr_length': 10,
            'atr_ma_length': 7,
            'adx_length': 20,
            'adx_entry_point': 40,
            'sma_window': 15,
            'trailing_percent': 9.0
        },
        'BSVUSDT.OKEX': {
            'atr_length': 35,
            'atr_ma_length': 8,
            'adx_length': 40,
            'adx_entry_point': 30,
            'sma_window': 30,
            'trailing_percent': 2
        },
        'ETHUSDT.OKEX': {
            'atr_length': 15,
            'atr_ma_length': 6,
            'adx_length': 15,
            'adx_entry_point': 20,
            'sma_window': 30,
            'trailing_percent': 10
        },
        'ETCUSDT.OKEX': {
            'atr_length': 35,
            'atr_ma_length': 5,
            'adx_length': 20,
            'adx_entry_point': 30,
            'sma_window': 55,
            'trailing_percent': 5.0
        },
        'EOSUSDT.OKEX': {
            'atr_length': 25,
            'atr_ma_length': 6,
            'adx_length': 5,
            'adx_entry_point': 20,
            'sma_window': 20,
            'trailing_percent': 1.0
        },
        'LTCUSDT.OKEX': {
            'atr_length': 40,
            'atr_ma_length': 4.0,
            'adx_length': 35,
            'adx_entry_point': 30,
            'sma_window': 20,
            'trailing_percent': 5.0
        },
        'DASHUSDT.OKEX': {
            'atr_length': 35,
            'atr_ma_length': 5,
            'adx_length': 15,
            'adx_entry_point': 25,
            'sma_window': 5,
            'trailing_percent': 10
        }
    }

    def __init__(self, cta_engine, strategy_name, vt_symbol, setting):
        super(AtrAdxSmaM1Strategy, self).__init__(
            cta_engine, strategy_name, vt_symbol, setting
        )

        if vt_symbol in self.symbol_parameters:
            params = self.symbol_parameters[vt_symbol]
            self.atr_length = params['atr_length']
            self.atr_ma_length = params['atr_ma_length']
            self.adx_length = params['adx_length']
            self.adx_entry_point = params['adx_entry_point']
            self.sma_length = params['sma_window']
            self.trailing_percent = params['trailing_percent']

    def check_entry(self, bar: BarData):
        atr_array = self.am.atr(self.atr_length, array=True)
        adx_array = self.am.adx(self.adx_length, array=True)
        sma_array = self.am.sma(self.sma_window, array=True)
        atr_value = atr_array[-1]
        atr_ma = atr_array[-self.atr_ma_length:].mean()

        if atr_value > atr_ma and adx_array[-1] > adx_array[-2] > self.adx_entry_point:
            if sma_array[-3] < sma_array[-2] < sma_array[-1]:
                self.buy(bar.close_price, self.volume)
            elif sma_array[-3] > sma_array[-2] > sma_array[-1]:
                self.short(bar.close_price, self.volume)
