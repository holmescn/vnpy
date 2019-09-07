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
from vnpy.app.cta_strategy.base import Offset
import numpy as np


class TestStrategy(CtaTemplate):
    """Test Strategy"""

    author = "用Python的交易员"

    adx_length = 10
    sma_length = 20
    fixed_money = 10000.0

    parameters = ["adx_length", "sma_length"]
    variables = []

    def __init__(self, cta_engine, strategy_name, vt_symbol, setting):
        """"""
        super(TestStrategy, self).__init__(
            cta_engine, strategy_name, vt_symbol, setting
        )
        self.bg = BarGenerator(self.on_bar)
        self.am = ArrayManager()
        self.k_price = 0.0
        self.profits = []

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

        sma_array = am.sma(self.sma_length, array=True)
        adx_array = am.adx(self.adx_length, array=True)

        if self.pos == 0:
            if adx_array[-1] > 25 and adx_array[-1] > adx_array[-2]:
                size = int(self.fixed_money / bar.close_price)
                if sma_array[-1] > sma_array[-2]:
                    # self.buy(bar.close_price + 5, self.fixed_size)
                    self.buy(bar.close_price, size)
                    # print(f"{bar.datetime} 趋势增强向上，买多 {size}")
                elif sma_array[-1] < sma_array[-2]:
                    # self.short(bar.close_price - 5, self.fixed_size)
                    self.short(bar.close_price, size)
                    # print(f"{bar.datetime} 趋势增强向下，买空 {size}")

        elif self.pos > 0:
            profit = (bar.close_price - self.k_price) * self.pos
            self.profits.append(profit)
            print("{} 持多 profit={:.1f} ADX={:.1f} SMA={:.1f} price={:.2f}".format(bar.datetime, profit, adx_array[-1], sma_array[-1], bar.close_price))
            if profit > 0:
                max_val = max(self.profits)
                max_idx = self.profits.index(max_val)
                if max_val > 0 and profit < max_val * 0.5 * np.exp(len(self.profits) - max_idx):
                    self.sell(bar.close_price, abs(self.pos))
                    print("{} 平多 profit={:.2f}".format(bar.datetime, profit))
            elif sma_array[-1] < sma_array[-2]:
                self.sell(bar.close_price, abs(self.pos))
                print("{} 平多 profit={:.2f}".format(bar.datetime, profit))

        elif self.pos < 0:
            profit = (bar.close_price - self.k_price) * self.pos
            self.profits.append(profit)
            print("{} 持空 profit={:.1f} ADX={:.1f} SMA={:.1f} price={:.2f}".format(bar.datetime, profit, adx_array[-1], sma_array[-1], bar.close_price))
            if profit > 0:
                max_val = max(self.profits)
                max_idx = self.profits.index(max_val)
                if max_val > 0 and  profit < max_val * 0.5 * np.exp(len(self.profits) - max_idx):
                    self.cover(bar.close_price, abs(self.pos))
                    print("{} 平空 profit={:.2f}".format(bar.datetime, profit))
            if sma_array[-1] > sma_array[-2]:
                self.cover(bar.close_price, abs(self.pos))
                print("{} 平空 profit={:.2f}".format(bar.datetime, profit))

        self.put_event()

    def on_order(self, order: OrderData):
        """
        Callback of new order data update.
        """
        super(TestStrategy, self).on_order(order)

    def on_trade(self, trade: TradeData):
        """
        Callback of new trade data update.
        """
        super(TestStrategy, self).on_trade(trade)

        if trade.offset == Offset.OPEN:
            self.k_price = trade.price
        elif trade.offset in (Offset.CLOSE, Offset.CLOSEYESTERDAY, Offset.CLOSEYESTERDAY):
            self.k_price = 0.0
            self.profits = []
        self.put_event()

    def on_stop_order(self, stop_order: StopOrder):
        """
        Callback of stop order update.
        """
        pass
