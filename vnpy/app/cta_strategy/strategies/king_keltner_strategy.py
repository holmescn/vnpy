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


class KingKeltnerStrategy(BaseStrategy):
    model_id = "m1_02_KingKeltner_v1.0"

    kk_length = 11
    kk_dev = 1.6
    trailing_percent = 0.8

    parameters = list(BaseStrategy.parameters)
    parameters.extend(['kk_length', 'kk_dev', 'trailing_percent'])

    symbol_parameters = {
        # 2019-09-01 2019-10-25 58.09%
        'BTCUSDT.OKEX': {
            'kk_dev': 0.1,
            'kk_length': 10,
            'trailing_percent': 0.2
        },
        # 2019-09-01 2019-10-25 49.86%
        'BCHUSDT.OKEX': {
            'kk_dev': 0.6,
            'kk_length': 55,
            'trailing_percent': 0.4
        },
        # 2019-09-01 2019-10-25 
        # 'BSVUSDT.OKEX': {
        #     'kk_length': 16,
        #     'kk_dev': 2.9,
        #     'trailing_percent': 0.5,
        # },
        # 2019-09-01 2019-10-25 
        # 'ETHUSDT.OKEX': {
        #     'kk_length': 8,
        #     'kk_dev': 0.3,
        #     'trailing_percent': 0.2,
        # },
        # 2019-09-01 2019-10-25 
        # 'ETCUSDT.OKEX': {
        #     'kk_length': 11,
        #     'kk_dev': 0.8,
        #     'trailing_percent': 0.2,
        # },
        # 2019-09-01 2019-10-25 
        # 'EOSUSDT.OKEX': {
        #     'kk_length': 13,
        #     'kk_dev': 1.4,
        #     'trailing_percent': 0.7,
        # },
        # 2019-09-01 2019-10-25 
        # 'LTCUSDT.OKEX': {
        #     'kk_length': 8.0,
        #     'kk_dev': 5.9,
        #     'trailing_percent': 4.6,
        # },
        # 2019-09-01 2019-10-25 
        # 'DASHUSDT.OKEX': {
        #     'kk_length': 19,
        #     'kk_dev': 8.5,
        #     'trailing_percent': 3.2,
        # }
    }

    def __init__(self, cta_engine, strategy_name, vt_symbol, setting):
        """"""
        super(KingKeltnerStrategy, self).__init__(
            cta_engine, strategy_name, vt_symbol, setting
        )

        if vt_symbol in self.symbol_parameters:
            params = self.symbol_parameters[vt_symbol]
            self.kk_length = params['kk_length']
            self.kk_dev = params['kk_dev']
            self.trailing_percent = params['trailing_percent']

        self.intra_trade_high = 0
        self.intra_trade_low = 0

        self.long_vt_orderids = []
        self.short_vt_orderids = []
        self.vt_orderids = []

        self.bg = BarGenerator(self.on_bar, 5, self.on_5min_bar)
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
        super(KingKeltnerStrategy, self).on_bar(bar)
        self.bg.update_bar(bar)

    def on_5min_bar(self, bar: BarData):
        """"""
        for orderid in self.vt_orderids:
            self.cancel_order(orderid)
        self.vt_orderids.clear()

        am = self.am
        am.update_bar(bar)
        if not am.inited:
            return

        kk_up, kk_down = am.keltner(self.kk_length, self.kk_dev)

        if self.pos == 0:
            self.intra_trade_high = bar.high_price
            self.intra_trade_low = bar.low_price
            self.send_oco_order(kk_up, kk_down, self.volume(2.5))

        elif self.pos > 0:
            self.intra_trade_high = max(self.intra_trade_high, bar.high_price)
            self.intra_trade_low = bar.low_price

            vt_orderids = self.sell(self.intra_trade_high * (1 - self.trailing_percent / 100), abs(self.pos), True)
            self.vt_orderids.extend(vt_orderids)

        elif self.pos < 0:
            self.intra_trade_high = bar.high_price
            self.intra_trade_low = min(self.intra_trade_low, bar.low_price)

            vt_orderids = self.cover(self.intra_trade_low * (1 + self.trailing_percent / 100), abs(self.pos), True)
            self.vt_orderids.extend(vt_orderids)

        self.put_event()

    def on_trade(self, trade: TradeData):
        """
        Callback of new trade data update.
        """
        if self.pos != 0:
            if self.pos > 0:
                for short_orderid in self.short_vt_orderids:
                    self.cancel_order(short_orderid)

            elif self.pos < 0:
                for buy_orderid in self.long_vt_orderids:
                    self.cancel_order(buy_orderid)

            for orderid in (self.long_vt_orderids + self.short_vt_orderids):
                if orderid in self.vt_orderids:
                    self.vt_orderids.remove(orderid)

        self.submit_trade(trade)
        self.print_trade(trade)
        self.put_event()

    def send_oco_order(self, buy_price, short_price, volume):
        self.long_vt_orderids = self.buy(buy_price, volume, True)
        self.short_vt_orderids = self.short(short_price, volume, True)

        self.vt_orderids.extend(self.long_vt_orderids)
        self.vt_orderids.extend(self.short_vt_orderids)
