from vnpy.app.cta_strategy import (
    CtaTemplate,
    StopOrder,
    Direction,
    TickData,
    BarData,
    TradeData,
    OrderData,
    BarGenerator,
    ArrayManager,
)
from vnpy.trader.object import Offset, Direction, Status
from vnpy.app.cta_strategy.base_strategy import BaseStrategy


class TurtleSignalStrategy(BaseStrategy):
    """Turtle Strategy"""
    model_id = "Turtle_v1.0"

    entry_window = 20
    exit_window = 10
    atr_window = 20
    fixed_size = 100

    entry_up = 0
    entry_down = 0
    exit_up = 0
    exit_down = 0
    atr_value = 0

    long_entry = 0
    short_entry = 0
    long_stop = 0
    short_stop = 0

    parameters = ["entry_window", "exit_window", "atr_window", "fixed_size"]
    variables = ["entry_up", "entry_down", "exit_up", "exit_down", "atr_value"]

    def __init__(self, cta_engine, strategy_name, vt_symbol, setting):
        """"""
        super(TurtleSignalStrategy, self).__init__(
            cta_engine, strategy_name, vt_symbol, setting
        )

        self.bg = BarGenerator(self.on_bar)
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
        super(TurtleSignalStrategy, self).on_bar(bar)
        self.cancel_all()

        self.am.update_bar(bar)
        if not self.am.inited:
            return

        # Only calculates new entry channel when no position holding
        if not self.pos:
            self.entry_up, self.entry_down = self.am.donchian(
                self.entry_window
            )

        self.exit_up, self.exit_down = self.am.donchian(self.exit_window)

        if not self.pos:
            self.atr_value = self.am.atr(self.atr_window)

            self.long_entry = 0
            self.short_entry = 0
            self.long_stop = 0
            self.short_stop = 0

            self.send_buy_orders(self.entry_up)
            self.send_short_orders(self.entry_down)
        elif self.pos > 0:
            self.send_buy_orders(self.entry_up)

            sell_price = max(self.long_stop, self.exit_down)
            self.sell(sell_price, abs(self.pos), True)

        elif self.pos < 0:
            self.send_short_orders(self.entry_down)

            cover_price = min(self.short_stop, self.exit_up)
            self.cover(cover_price, abs(self.pos), True)

        self.put_event()

    def on_trade(self, trade: TradeData):
        """
        Callback of new trade data update.
        """
        if trade.direction == Direction.LONG:
            self.long_entry = trade.price
            self.long_stop = self.long_entry - 2 * self.atr_value
        else:
            self.short_entry = trade.price
            self.short_stop = self.short_entry + 2 * self.atr_value

        self.submit_trade(trade)
        self.print_trade(trade)
        self.put_event()

    def send_buy_orders(self, price):
        """"""
        t = self.pos / self.fixed_size

        if t < 1:
            self.buy(price, self.fixed_size, True)

        if t < 2:
            self.buy(price + self.atr_value * 0.5, self.fixed_size, True)

        if t < 3:
            self.buy(price + self.atr_value, self.fixed_size, True)

        if t < 4:
            self.buy(price + self.atr_value * 1.5, self.fixed_size, True)

    def send_short_orders(self, price):
        """"""
        t = self.pos / self.fixed_size

        if t > -1:
            self.short(price, self.fixed_size, True)

        if t > -2:
            self.short(price - self.atr_value * 0.5, self.fixed_size, True)

        if t > -3:
            self.short(price - self.atr_value, self.fixed_size, True)

        if t > -4:
            self.short(price - self.atr_value * 1.5, self.fixed_size, True)
