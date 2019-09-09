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
from vnpy.app.cta_strategy.submit_trade_mixin import SubmitTradeMixin


class AdxAtrStrategy(CtaTemplate, SubmitTradeMixin):
    """ADX/ATR Strategy"""

    author = "用Python的交易员"
    model_id = "ETHUSD_m1_ADX_ATR_v1.0"

    atr_length = 22
    atr_ma_length = 10
    adx_length = 5
    trailing_percent = 0.8
    fixed_size = 1

    atr_value = 0
    atr_ma = 0
    adx_value = 0
    intra_trade_high = 0
    intra_trade_low = 0

    parameters = ["atr_length", "atr_ma_length", "adx_length",
                  "trailing_percent"]
    variables = ["atr_value", "atr_ma", "adx_value"]

    def __init__(self, cta_engine, strategy_name, vt_symbol, setting):
        """"""
        super(AdxAtrStrategy, self).__init__(
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

        ma20_array = am.sma(20, array=True)
        atr_array = am.atr(self.atr_length, array=True)
        self.atr_value = atr_array[-1]
        self.atr_ma = atr_array[-self.atr_ma_length:].mean()
        self.adx_value = am.adx(self.adx_length)

        if self.pos == 0:
            self.intra_trade_high = bar.high_price
            self.intra_trade_low = bar.low_price

            if self.atr_value > self.atr_ma and self.adx_value > 25:
                size = self.fixed_size
                if ma20_array[-1] > ma20_array[-2]:
                    # self.buy(bar.close_price + 5, self.fixed_size)
                    self.buy(bar.close_price, size)
                elif ma20_array[-1] < ma20_array[-2]:
                    # self.short(bar.close_price - 5, self.fixed_size)
                    self.short(bar.close_price, size)

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
