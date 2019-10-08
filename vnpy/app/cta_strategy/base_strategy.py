import pickle
from copy import copy
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
from vnpy.trader.setting import SETTINGS

from datetime import datetime
from time import sleep
from hashlib import md5


class BaseStrategy(CtaTemplate):
    author = "用 Python 的交易员"

    model_id = ''

    parameters = ['percent']
    variables = ["buy_trade_list", "sell_trade_list"]

    def __init__(self, cta_engine, strategy_name, vt_symbol, setting):
        """"""
        super(BaseStrategy, self).__init__(
            cta_engine, strategy_name, vt_symbol, setting
        )
        self.enable_submit_trade_data = SETTINGS.get('submit_trade_data.enable', False)
        self.percent = setting.get('percent', 0.5)
        self.reverse = setting.get('reverse', False)
        self._model_id = '{}_{}{}'.format(self.vt_symbol, self.model_id, '_rev' if self.reverse else '')

        self.buy_trade_list = []
        self.sell_trade_list = []
        self.bar: BarData = None
        self.datetime: datetime = None
        self.avg_vol = 0.01
        self.trade_records = []

    @property
    def vt_modelid(self):
        return self._model_id

    @property
    def volume(self):
        if self.bar:
            vol = 200_000 * self.percent / self.bar.close_price
            vol = min(max(self.bar.volume, self.avg_vol), vol)
            if vol > 5000:
                vol = round(vol / 1000, 1) * 1000
            elif vol > 500:
                vol = round(vol / 100, 1) * 100
            elif vol > 10:
                vol = round(vol / 10, 0) * 10
            elif vol > 1:
                vol = round(vol, 0)
            return vol
        return self.avg_vol

    def submit_trade(self, trade: TradeData):
        direction = "buy" if trade.direction == Direction.LONG else 'sell'
        trade_id = trade.tradeid.replace(trade.vt_symbol, self._model_id)
        trade_id = 'DIGIT_' + md5(trade_id.encode('utf-8')).hexdigest()

        current_trade = {
            "broker_id": trade.exchange.value,
            "investor_id": "000000",
            "direction": direction,
            "instrument_id": trade.symbol.replace('-', ''),
            "instrument_name": trade.vt_symbol,
            "model_id": self._model_id,
            "price": trade.price,
            "trade_id": trade_id,
            "trade_time": self.datetime.strftime("%Y-%m-%d %H:%M:%S"),
            "volume": trade.volume,
            "category": "digital"
        }

        send_list = []
        if trade.offset == Offset.OPEN:
            send_list.append(copy(current_trade))
            self.trade_records.append(copy(current_trade))

            if trade.direction == Direction.LONG:
                self.buy_trade_list.append(current_trade)
            elif trade.direction == Direction.SHORT:
                self.sell_trade_list.append(current_trade)

        elif trade.offset in (Offset.CLOSE, Offset.CLOSEYESTERDAY, Offset.CLOSETODAY):
            trade_list = []
            if trade.direction == Direction.LONG:
                trade_list = self.sell_trade_list
            elif trade.direction == Direction.SHORT:
                trade_list = self.buy_trade_list

            for open_trade in trade_list:
                close_trade = copy(current_trade)
                close_trade['close_trade_id'] = open_trade['trade_id']
                if close_trade['volume'] > open_trade['volume']:
                    close_trade['volume'] = open_trade['volume']
                    current_trade['volume'] -= open_trade['volume']
                open_trade['volume'] = round(open_trade['volume'] - close_trade['volume'], 2)
                send_list.append(close_trade)
                self.trade_records.append(copy(close_trade))

                if open_trade['volume'] > 0:
                    break

            self.buy_trade_list = [t for t in self.buy_trade_list if t['volume'] > 0]
            self.sell_trade_list = [t for t in self.sell_trade_list if t['volume'] > 0]

            with open(f'tradedata_1/{self._model_id}.pkl', 'wb') as f:
                pickle.dump(self.trade_records, f)

        if self.enable_submit_trade_data and False:
            submit_trade_data(send_list)

    def print_order(self, order):
        if order.status in (Status.SUBMITTING, Status.ALLTRADED):
            action = '{} {}'.format(order.offset.value, order.direction.value)
            self.write_log("{} {:.3f} x {}".format(action, order.price, order.volume))

    def print_trade(self, trade):
        action = '{} {}'.format(trade.offset.value, trade.direction.value)
        self.write_log("成交：{} {:.2f} x {} {}".format(action, trade.price, trade.volume, trade.tradeid))

    def on_init(self):
        """
        Callback when strategy is inited.
        """
        self.write_log("策略初始化")
        self.load_bar(2)

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

    def on_bar(self, bar: BarData):
        super(BaseStrategy, self).on_bar(bar)
        self.datetime = bar.datetime
        self.bar = bar
        if self.avg_vol < 0.1:
            self.avg_vol = bar.volume
        elif bar.volume > 0:
            self.avg_vol = self.avg_vol * 0.5 + bar.volume * 0.5

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
        if volume < 0.01:
            return

        if self.reverse:
            return super(BaseStrategy, self).short(price, volume, stop, lock)
        return super(BaseStrategy, self).buy(price, volume, stop, lock)

    def short(self, price: float, volume: float, stop: bool = False, lock: bool = False):
        if volume < 0.01:
            return

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

    parameters = list(BaseStrategy.parameters)
    parameters.extend(["atr_length", "atr_ma_length", "trailing_percent"])
    variables = list(BaseStrategy.variables)
    variables.extend(["atr_value", "atr_ma"])

    def __init__(self, cta_engine, strategy_name, vt_symbol, setting):
        """"""
        super(BaseAtrStrategy, self).__init__(
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
        super(BaseAtrStrategy, self).on_bar(bar)
        self.cancel_all()

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
