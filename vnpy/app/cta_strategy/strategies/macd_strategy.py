import time
from vnpy.app.cta_strategy import (
    CtaTemplate,
    StopOrder,
    TickData,
    BarData,
    TradeData,
    OrderData,
    BarGenerator,
    ArrayManager
)
from vnpy.trader.object import Offset, Direction, Status
from vnpy.app.cta_strategy.submit_trade_mixin import SubmitTradeMixin


class MacdStrategy(CtaTemplate, SubmitTradeMixin):
    """MACD Strategy"""
    author = "用Python的交易员"
    model_id = "ETHUSD_m1_MACD_MACD_v1.0"

    fast_period = 12
    slow_period = 26
    signal_period = 9
    fixed_size = 1

    parameters = ["fast_period", "slow_period", "signal_period"]
    variables = []

    def __init__(self, cta_engine, strategy_name, vt_symbol, setting):
        """"""
        super(MacdStrategy, self).__init__(
            cta_engine, strategy_name, vt_symbol, setting
        )
        self.bg = BarGenerator(self.on_bar)
        self.am = ArrayManager()

    def on_init(self):
        """
        Callback when strategy is inited.
        """
        self.write_log("策略初始化")
        self.load_bar(10)

    def on_start(self):
        """
        Callback when strategy is started.
        """
        self.write_log("策略启动")

    def on_stop(self):
        """
        Callback when strategy is stopped.
        """
        self.write_log("策略停止")

    def on_tick(self, tick: TickData):
        """
        Callback of new tick data update.
        """
        self.bg.update_tick(tick)

    def on_bar(self, bar: BarData):
        """
        Callback of new bar data update.
        """
        self.cancel_all()

        am = self.am
        am.update_bar(bar)
        if not am.inited:
            return

        macd_array, signal_array, _ = am.macd(self.fast_period, self.slow_period, self.signal_period, array=True)

        price = bar.close_price
        if self.pos == 0:
            size = self.fixed_size
            if macd_array[-2] < signal_array[-2] and macd_array[-1] > signal_array[-1]:
                self.buy(price, size)
            elif macd_array[-2] > signal_array[-2] and macd_array[-1] < signal_array[-1]:
                self.short(price, size)

        elif self.pos > 0:
            if macd_array[-2] > signal_array[-2] and macd_array[-1] < signal_array[-1]:
                self.sell(price, abs(self.pos))

        elif self.pos < 0:
            if macd_array[-2] < signal_array[-2] and macd_array[-1] > signal_array[-1]:
                self.cover(price, abs(self.pos))

        self.put_event()

    def on_order(self, order: OrderData):
        """
        Callback of new order data update.
        """
        self.print_order(order)

    def on_trade(self, trade: TradeData):
        """
        Callback of new trade data update.
        """
        self.submit_trade(trade)
        self.print_trade(trade)        
        self.put_event()

    def on_stop_order(self, stop_order: StopOrder):
        """
        Callback of stop order update.
        """
        pass
