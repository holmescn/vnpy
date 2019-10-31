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

    parameters = []
    variables = ["buy_trade_list", "sell_trade_list", "balance"]

    def __init__(self, cta_engine, strategy_name, vt_symbol, setting):
        super(BaseStrategy, self).__init__(
            cta_engine, strategy_name, vt_symbol, setting
        )
        self.enable_submit_trade_data = SETTINGS.get('submit_trade_data.enable', False)
        self.reverse = setting.get('reverse', False)
        self.vt_modelid = '{}_{}{}'.format(self.vt_symbol, self.model_id, '_rev' if self.reverse else '')

        self.balance = 200_000
        self.buy_trade_list = []
        self.sell_trade_list = []
        self.bar: BarData = None
        self.datetime: datetime = None
        self.vol_list = []
        self.trade_records = []

    def volume(self, multiplier=1.0):
        avg_vol = sum(self.vol_list) / len(self.vol_list) if self.vol_list else 0.0
        if self.bar:
            vol_ubound = self.balance * 0.9 / self.bar.close_price
            vol = min(avg_vol * multiplier, vol_ubound)
            return round(vol, 2)
        return avg_vol

    def submit_trade(self, trade: TradeData):
        direction = "buy" if trade.direction == Direction.LONG else 'sell'
        trade_id = trade.tradeid.replace(trade.vt_symbol, self.vt_modelid)
        trade_id = 'DIGIT_' + md5(trade_id.encode('utf-8')).hexdigest()

        current_trade = {
            "broker_id": trade.exchange.value,
            "investor_id": "000000",
            "direction": direction,
            "instrument_id": trade.symbol.replace('-', ''),
            "instrument_name": trade.vt_symbol,
            "model_id": self.vt_modelid,
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

            with open(f'tradedata/{self.vt_modelid}.pkl', 'wb') as f:
                pickle.dump(self.trade_records, f)

        # if self.enable_submit_trade_data:
        #     submit_trade_data(send_list)

    def print_trade(self, trade):
        action = '{} {}'.format(trade.offset.value, trade.direction.value)
        self.write_log("成交：{} {:.2f} x {} {} {:.2f}".format(action, trade.price, trade.volume, trade.tradeid, self.balance))

    def on_init(self):
        self.load_bar(1)

    def on_start(self):
        self.write_log("策略启动")

    def on_stop(self):
        self.write_log("策略停止")

    def on_bar(self, bar: BarData):
        super(BaseStrategy, self).on_bar(bar)
        self.datetime = bar.datetime
        self.bar = bar
        self.vol_list.append(bar.volume)
        if len(self.vol_list) > 10:
            self.vol_list = self.vol_list[-10:]

    def on_order(self, order: OrderData):
        pass

    def on_trade(self, trade: TradeData):
        if trade.offset == Offset.OPEN:
            self.balance -= trade.volume * trade.price
        elif trade.offset in (Offset.CLOSE, Offset.CLOSETODAY, Offset.CLOSEYESTERDAY):
            self.balance += trade.volume * trade.price

        self.submit_trade(trade)
        self.print_trade(trade)
        self.put_event()

    def on_stop_order(self, stop_order: StopOrder):
        pass

    def buy(self, price: float, volume: float, stop: bool = False, lock: bool = False):
        if volume < 0.01:
            return []

        if self.reverse:
            return super(BaseStrategy, self).short(price, volume, stop, lock)
        return super(BaseStrategy, self).buy(price, volume, stop, lock)

    def short(self, price: float, volume: float, stop: bool = False, lock: bool = False):
        if volume < 0.01:
            return []

        if self.reverse:
            return super(BaseStrategy, self).buy(price, volume, stop, lock)
        return super(BaseStrategy, self).short(price, volume, stop, lock)


class BaseM1Strategy(BaseStrategy):
    trailing_percent = 0.0
    parameters = list(BaseStrategy.parameters)
    parameters.extend(["trailing_percent"])

    def __init__(self, cta_engine, strategy_name, vt_symbol, setting):
        super(BaseM1Strategy, self).__init__(
            cta_engine, strategy_name, vt_symbol, setting
        )
        self.intra_trade_high = 0
        self.intra_trade_low = 0

        self.bg = BarGenerator(self.on_bar)
        self.am = ArrayManager()

    def on_tick(self, tick: TickData):
        self.bg.update_tick(tick)

    def on_bar(self, bar: BarData):
        super(BaseM1Strategy, self).on_bar(bar)
        self.cancel_all()

        self.am.update_bar(bar)
        if not self.am.inited:
            return

        if self.pos == 0:
            self.intra_trade_high = bar.high_price
            self.intra_trade_low = bar.low_price
            self.check_entry(bar)

        elif self.pos > 0:
            self.intra_trade_high = max(self.intra_trade_high, bar.high_price)
            self.intra_trade_low = bar.low_price

            long_stop = self.intra_trade_high * (1 - self.trailing_percent / 100)
            self.sell(long_stop, abs(self.pos), stop=True)

        elif self.pos < 0:
            self.intra_trade_high = bar.high_price
            self.intra_trade_low = min(self.intra_trade_low, bar.low_price)

            short_stop = self.intra_trade_low * (1 + self.trailing_percent / 100)
            self.cover(short_stop, abs(self.pos), stop=True)

        self.put_event()

    def check_entry(self, bar: BarData):
        pass
