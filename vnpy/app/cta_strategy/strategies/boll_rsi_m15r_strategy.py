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


class BollRsiAtrM15rStrategy(BaseStrategy):
    model_id = "m15_02_BOLL-RSI-ATR_r_v1.0"

    boll_window = 18
    boll_dev = 3.4
    rsi_window = 50
    rsi_entry = 10
    atr_window = 30
    sl_multiplier = 5.2

    parameters = list(BaseStrategy.parameters)
    parameters.extend([
        "boll_window", "boll_dev",
        "rsi_window", "rsi_entry",
        "atr_window", "sl_multiplier"
    ])
    symbol_parameters = {
        # 2019-09-01 2019-10-25 37.58%
        'BTCUSDT.OKEX': {
            'atr_window': 65,
            'boll_dev': 8.15,
            'boll_window': 15,
            'rsi_entry': 9.0,
            'rsi_length': 25,
            'sl_multiplier': 1.1
        },
        # 2019-09-01 2019-10-25 41.79%
        'BCHUSDT.OKEX': {
            'atr_window': 80,
            'boll_dev': 2.6,
            'boll_window': 10,
            'rsi_entry': 17.5,
            'rsi_length': 30,
            'sl_multiplier': 2.0
        },
        # 2019-09-01 2019-10-25 42.40%
        'BSVUSDT.OKEX': {
            'atr_window': 50,
            'boll_dev': 1.1,
            'boll_window': 35,
            'rsi_entry': 21.0,
            'rsi_length': 60,
            'sl_multiplier': 3.9
        },
        # 2019-09-01 2019-10-25 38.91%
        'ETHUSDT.OKEX': {
            'atr_window': 45,   
            'boll_dev': 1.15,   
            'boll_window': 55,  
            'rsi_entry': 10.5,  
            'rsi_length': 60,   
            'sl_multiplier': 2.0
        },
        # 2019-09-01 2019-10-25 47.39%
        'ETCUSDT.OKEX': {
            'atr_window': 15,   
            'boll_dev': 2.1,    
            'boll_window': 10,  
            'rsi_entry': 34.5,  
            'rsi_length': 35,   
            'sl_multiplier': 1.8
        },
        # 2019-09-01 2019-10-25 36.81%
        'EOSUSDT.OKEX': {
            'atr_window': 30,
            'boll_dev': 2.95,
            'boll_window': 15,
            'rsi_entry': 6.5,
            'rsi_length': 20,
            'sl_multiplier': 2.4
        },
        # 2019-09-01 2019-10-25 34.92%
        'LTCUSDT.OKEX': {
            'atr_window': 15,
            'boll_dev': 2.7,
            'boll_window': 45,
            'rsi_entry': 36.5,
            'rsi_length': 45,
            'sl_multiplier': 3.4
        },
        # 2019-09-01 2019-10-25 11.24%
        'DASHUSDT.OKEX': {
            'atr_window': 30,   
            'boll_dev': 7.2,    
            'boll_window': 45,  
            'rsi_entry': 37.5,  
            'rsi_length': 20,   
            'sl_multiplier': 4.5
        }
    }

    def __init__(self, cta_engine, strategy_name, vt_symbol, setting):
        super(BollRsiAtrM15rStrategy, self).__init__(
            cta_engine, strategy_name, vt_symbol, setting
        )

        self.intra_trade_high = 0
        self.intra_trade_low = 0

        self.bg = BarGenerator(self.on_bar, 15, self.on_15min_bar)
        self.am = ArrayManager()

    def on_tick(self, tick: TickData):
        self.bg.update_tick(tick)

    def on_bar(self, bar: BarData):
        super(BollRsiAtrM15rStrategy, self).on_bar(bar)
        self.bg.update_bar(bar)

    def on_15min_bar(self, bar: BarData):
        self.cancel_all()

        am = self.am
        am.update_bar(bar)
        if not am.inited:
            return

        boll_up, boll_down = am.boll(self.boll_window, self.boll_dev)
        rsi_value = am.rsi(self.rsi_window)
        atr_value = am.atr(self.atr_window)

        if self.pos == 0:
            self.intra_trade_high = bar.high_price
            self.intra_trade_low = bar.low_price

            if rsi_value > self.rsi_entry:
                self.short(boll_up, self.volume(7.5), stop=True)
            elif rsi_value < -self.rsi_entry:
                self.buy(boll_down, self.volume(7.5), stop=True)

        elif self.pos > 0:
            self.intra_trade_high = max(self.intra_trade_high, bar.high_price)
            self.intra_trade_low = bar.low_price

            long_stop = self.intra_trade_high - atr_value * self.sl_multiplier
            self.sell(long_stop, abs(self.pos), stop=True)

        elif self.pos < 0:
            self.intra_trade_high = bar.high_price
            self.intra_trade_low = min(self.intra_trade_low, bar.low_price)

            short_stop = self.intra_trade_low + atr_value * self.sl_multiplier
            self.cover(short_stop, abs(self.pos), stop=True)

        self.put_event()
