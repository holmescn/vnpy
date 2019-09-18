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
from vnpy.app.cta_strategy.submit_trade_data import submit_trade_data
from datetime import datetime
from time import sleep


class BaseStrategy(CtaTemplate):
    should_send_trade = True

    author = "用Python的交易员"

    datetime: datetime = None
    model_id = ''
    fixed_size = 1
    last_trade_id = None

    def __init__(self, cta_engine, strategy_name, vt_symbol, setting):
        """"""
        super(BaseStrategy, self).__init__(
            cta_engine, strategy_name, vt_symbol, setting
        )
        self.reverse = setting.get('reverse', False)
        self.model_id = '{}_{}{}'.format(self.vt_symbol, self.model_id, '_rev' if self.reverse else '')

    def submit_trade(self, trade: TradeData):
        direction = "buy" if trade.direction == Direction.LONG else 'sell'
        trade_list = []
        item = {
            "broker_id": trade.exchange.value,
            "investor_id": "000000",
            "direction": direction,
            "instrument_id": trade.symbol,
            "instrument_name": trade.vt_symbol,
            "model_id": self.model_id,
            "price": trade.price,
            "trade_id": '%s_%s_%s' % (self.model_id, self.datetime.strftime('%Y%m%d'), trade.tradeid),
            "trade_time": self.datetime.strftime("%Y-%m-%d %H:%M:%S"),
            "volume": trade.volume,
            "category": "digital"
        }

        if trade.offset == Offset.OPEN:
            self.last_trade_id = item['trade_id']
            trade_list.append(item)
        elif self.last_trade_id and trade.offset in (Offset.CLOSE, Offset.CLOSEYESTERDAY, Offset.CLOSETODAY):
            item["close_trade_id"] = self.last_trade_id
            trade_list.append(item)    
            self.last_trade_id = None
        else:
            self.write_log("找不到开仓记录")

        if self.should_send_trade and trade_list:
            submit_trade_data(trade_list)
            sleep(0.05)

    def print_order(self, order):
        if order.status in (Status.SUBMITTING, Status.ALLTRADED):
            action = '{} {}'.format(order.offset.value, order.direction.value)
            self.write_log("{} {:.3f} x {}".format(action, order.price, order.volume))

    def print_trade(self, trade):
        action = '{} {}'.format(trade.offset.value, trade.direction.value)
        self.write_log("成交：{} {:.2f} x {}".format(action, trade.price, trade.volume))

    def on_init(self):
        """
        Callback when strategy is inited.
        """
        self.write_log("策略初始化")
        self.load_bar(3)

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

    def buy(self, price: float, volume: float, stop: bool = False, lock: bool = False):
        if self.reverse:
            return super(BaseStrategy, self).short(price, volume, stop, lock)
        return super(BaseStrategy, self).buy(price, volume, stop, lock)

    def short(self, price: float, volume: float, stop: bool = False, lock: bool = False):
        if self.reverse:
            return super(BaseStrategy, self).buy(price, volume, stop, lock)
        return super(BaseStrategy, self).short(price, volume, stop, lock)


class BaseAtrStrategy(BaseStrategy):
    atr_length = 22
    atr_ma_length = 10
    trailing_percent = 0.9

    atr_value = 0
    atr_ma = 0
    intra_trade_high = 0
    intra_trade_low = 0

    variables = ["atr_value", "atr_ma"]

    def __init__(self, cta_engine, strategy_name, vt_symbol, setting):
        """"""
        super(BaseAtrStrategy, self).__init__(
            cta_engine, strategy_name, vt_symbol, setting
        )
        self.bg = BarGenerator(self.on_bar)
        self.am = ArrayManager()
        self.fixed_size = setting.get('fixed_size', 1)

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
        self.date_str = bar.datetime.strftime('%F')

        am = self.am
        am.update_bar(bar)
        if not am.inited:
            return

        atr_array = am.atr(self.atr_length, array=True)
        self.atr_value = atr_array[-1]
        self.atr_ma = atr_array[-self.atr_ma_length:].mean()

        if self.pos == 0:
            self.intra_trade_high = bar.high_price
            self.intra_trade_low = bar.low_price
            self.on_pos_zero(bar)

        elif self.pos > 0:
            self.intra_trade_high = max(self.intra_trade_high, bar.high_price)
            self.intra_trade_low = bar.low_price

            long_stop = self.intra_trade_high * (1 - self.trailing_percent / 100)
            self.sell(long_stop, abs(self.pos), stop=True)

        elif self.pos < 0:
            self.intra_trade_low = min(self.intra_trade_low, bar.low_price)
            self.intra_trade_high = bar.high_price

            short_stop = self.intra_trade_low * (1 + self.trailing_percent / 100)
            self.cover(short_stop, abs(self.pos), stop=True)

        self.put_event()

    def on_pos_zero(self, bar: BarData):
        pass

    def on_stop_order(self, stop_order: StopOrder):
        """
        Callback of stop order update.
        """
        pass
