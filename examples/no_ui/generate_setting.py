import os
import sys
import json
from datetime import datetime
from logging import INFO

from vnpy.trader.setting import SETTINGS
from vnpy.app.cta_strategy.backtesting import BacktestingEngine
from vnpy.app.cta_strategy.strategies.adx_atr_strategy import (
    AdxAtrStrategy,
)
from vnpy.app.cta_strategy.strategies.boll_atr_strategy import (
    BollAtrStrategy,
)
from vnpy.app.cta_strategy.strategies.cci_atr_strategy import (
    CciAtrStrategy,
)
from vnpy.app.cta_strategy.strategies.cmo_atr_strategy import (
    CmoAtrStrategy,
)
from vnpy.app.cta_strategy.strategies.dema_atr_strategy import (
    DemaAtrStrategy,
)
from vnpy.app.cta_strategy.strategies.donchian_atr_strategy import (
    DonchianAtrStrategy,
)
from vnpy.app.cta_strategy.strategies.ht_atr_strategy import (
    HtAtrStrategy,
)
from vnpy.app.cta_strategy.strategies.kama_atr_strategy import (
    KamaAtrStrategy,
)
from vnpy.app.cta_strategy.strategies.keltner_atr_strategy import (
    KeltnerAtrStrategy,
)
from vnpy.app.cta_strategy.strategies.macd_atr_strategy import (
    MacdAtrStrategy,
)
from vnpy.app.cta_strategy.strategies.rsi_atr_strategy import (
    RsiAtrStrategy,
)
from vnpy.app.cta_strategy.strategies.sar_atr_strategy import (
    SarAtrStrategy,
)
from vnpy.app.cta_strategy.strategies.tema_atr_strategy import (
    TemaAtrStrategy,
)
from vnpy.app.cta_strategy.strategies.trima_atr_strategy import (
    TrimaAtrStrategy,
)

from vnpy.app.cta_strategy.strategies.boll_channel_strategy import (
    BollChannelStrategy,
)
from vnpy.app.cta_strategy.strategies.dual_thrust_strategy import (
    DualThrustStrategy,
)
from vnpy.app.cta_strategy.strategies.king_keltner_strategy import (
    KingKeltnerStrategy,
)
from vnpy.app.cta_strategy.strategies.multi_timeframe_strategy import (
    MultiTimeframeStrategy,
)


def make_pair(it, s, reverse):
    key = '{} {}{}'.format(it['vt_symbol'], s.model_id, ' REV' if reverse else '')
    value = {
        "class_name": s.__name__,
        "vt_symbol": it['vt_symbol'],
        "setting": {
            "reverse": reverse,
            "fixed_size": it['fixed_size']
        }
    }
    return key, value


def main():
    instruments = [{
        'vt_symbol': 'BTCUSDT.OKEX',
        'fixed_size': 20,
        'price_tick': 0.01,
    }, {
        'vt_symbol': 'BTCUSDK.OKEX',
        'fixed_size': 20,
        'price_tick': 0.01,
    }, {
        'vt_symbol': 'BCHUSDT.OKEX',
        'fixed_size': 600,
        'price_tick': 0.01,
    }, {
        'vt_symbol': 'BCHUSDK.OKEX',
        'fixed_size': 600,
        'price_tick': 0.01,
    }, {
        'vt_symbol': 'LTCUSDT.OKEX',
        'fixed_size': 2000,
        'price_tick': 0.001,
    }, {
        'vt_symbol': 'LTCUSDK.OKEX',
        'fixed_size': 2000,
        'price_tick': 0.001,
    }, {
        'vt_symbol': 'ETHUSDT.OKEX',
        'fixed_size': 200,
        'price_tick': 0.001,
    }, {
        'vt_symbol': 'ETHUSDK.OKEX',
        'fixed_size': 200,
        'price_tick': 0.001,
    }, {
        'vt_symbol': 'EOSUSDT.OKEX',
        'fixed_size': 40000,
        'price_tick': 0.001,
    }, {
        'vt_symbol': 'EOSUSDK.OKEX',
        'fixed_size': 40000,
        'price_tick': 0.001,
    }]

    # 14 * 2 = 28
    revertable_strategies = [
        AdxAtrStrategy, BollAtrStrategy, CciAtrStrategy, CmoAtrStrategy,
        DemaAtrStrategy, DonchianAtrStrategy, HtAtrStrategy,
        KamaAtrStrategy, KeltnerAtrStrategy, MacdAtrStrategy, RsiAtrStrategy,
        SarAtrStrategy, TemaAtrStrategy, TrimaAtrStrategy
    ]

    # 5
    other_strategies = [
        BollChannelStrategy, DualThrustStrategy,
        KingKeltnerStrategy, MultiTimeframeStrategy
    ]

    settings = dict()
    # (5 + 28) * 10 = 330
    for it in instruments:
        for s in revertable_strategies:
            k, v = make_pair(it, s, False)
            settings[k] = v

            k, v = make_pair(it, s, True)
            settings[k] = v

        for s in other_strategies:
            k, v = make_pair(it, s, False)
            settings[k] = v

    print(f"Total {len(settings)} strategies")
    with open('cta_strategy_setting.json', 'w', encoding='utf-8') as f:
        json.dump(settings, f, indent=2)


if __name__ == "__main__":
    main()
