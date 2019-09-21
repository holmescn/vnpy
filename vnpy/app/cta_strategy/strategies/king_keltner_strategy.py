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
    """King Keltner Strategy"""
    model_id = "m1_KingKeltner_v1.0"

    kk_length = 11
    kk_dev = 1.6
    trailing_percent = 0.8

    kk_up = 0
    kk_down = 0
    intra_trade_high = 0
    intra_trade_low = 0

    long_vt_orderids = []
    short_vt_orderids = []
    vt_orderids = []

    parameters = ['kk_length', 'kk_dev', 'fixed_size']
    variables = ['kk_up', 'kk_down', 'timestamp']

    def __init__(self, cta_engine, strategy_name, vt_symbol, setting):
        """"""
        super(KingKeltnerStrategy, self).__init__(
            cta_engine, strategy_name, vt_symbol, setting
        )

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

        if self.timestamp > bar.datetime.timestamp():
            self.pos = 0
            return
        self.timestamp = bar.datetime.timestamp()

        self.kk_up, self.kk_down = am.keltner(self.kk_length, self.kk_dev)

        if self.pos == 0:
            self.intra_trade_high = bar.high_price
            self.intra_trade_low = bar.low_price
            self.send_oco_order(self.kk_up, self.kk_down, self.fixed_size)

        elif self.pos > 0:
            self.intra_trade_high = max(self.intra_trade_high, bar.high_price)
            self.intra_trade_low = bar.low_price

            vt_orderids = self.sell(self.intra_trade_high * (1 - self.trailing_percent / 100),
                                    abs(self.pos), True)
            self.vt_orderids.extend(vt_orderids)

        elif self.pos < 0:
            self.intra_trade_high = bar.high_price
            self.intra_trade_low = min(self.intra_trade_low, bar.low_price)

            vt_orderids = self.cover(self.intra_trade_low * (1 + self.trailing_percent / 100),
                                     abs(self.pos), True)
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
        """"""
        self.long_vt_orderids = self.buy(buy_price, volume, True)
        self.short_vt_orderids = self.short(short_price, volume, True)

        self.vt_orderids.extend(self.long_vt_orderids)
        self.vt_orderids.extend(self.short_vt_orderids)
