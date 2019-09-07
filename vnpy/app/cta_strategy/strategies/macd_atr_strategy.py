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


class MacdAtrStrategy(CtaTemplate):
    """MACD/ATR Strategy"""

    author = "用Python的交易员"

    atr_length = 22
    atr_ma_length = 10
    fast_period = 10
    slow_period = 20
    signal_period = 9
    trailing_percent = 0.8
    fixed_size = 1
    fixed_money = 10000.0

    atr_value = 0
    atr_ma = 0
    intra_trade_high = 0
    intra_trade_low = 0

    parameters = ["atr_length", "atr_ma_length", "fast_period", "slow_period"
                  "signal_period", "trailing_percent", "fixed_size"]
    variables = ["atr_value", "atr_ma", "fast_period", "slow_period"
                 "signal_period"]

    def __init__(self, cta_engine, strategy_name, vt_symbol, setting):
        """"""
        super(MacdAtrStrategy, self).__init__(
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

        atr_array = am.atr(self.atr_length, array=True)
        self.atr_value = atr_array[-1]
        self.atr_ma = atr_array[-self.atr_ma_length:].mean()
        macd, signal, _ = am.macd(self.fast_period, self.slow_period, self.signal_period, array=True)

        if self.pos == 0:
            self.intra_trade_high = bar.high_price
            self.intra_trade_low = bar.low_price

            if self.atr_value > self.atr_ma:
                size = int(self.fixed_money / bar.close_price)
                if macd[-2] < signal[-2] and macd[-1] > signal[-1]:
                    # self.buy(bar.close_price + 5, self.fixed_size)
                    self.short(bar.close_price, size)
                elif macd[-2] > signal[-2] and macd[-1] < signal[-1]:
                    # self.short(bar.close_price - 5, self.fixed_size)
                    self.buy(bar.close_price, size)

        elif self.pos > 0:
            self.intra_trade_high = max(self.intra_trade_high, bar.high_price)
            self.intra_trade_low = bar.low_price

            long_stop = self.intra_trade_high * \
                (1 - self.trailing_percent / 100)
            self.sell(long_stop, abs(self.pos), stop=True)

        elif self.pos < 0:
            self.intra_trade_low = min(self.intra_trade_low, bar.low_price)
            self.intra_trade_high = bar.high_price

            short_stop = self.intra_trade_low * \
                (1 + self.trailing_percent / 100)
            self.cover(short_stop, abs(self.pos), stop=True)

        self.put_event()

    def on_order(self, order: OrderData):
        """
        Callback of new order data update.
        """
        pass

    def on_trade(self, trade: TradeData):
        """
        Callback of new trade data update.
        """
        self.put_event()

    def on_stop_order(self, stop_order: StopOrder):
        """
        Callback of stop order update.
        """
        pass
