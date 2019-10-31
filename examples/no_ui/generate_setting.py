import os
import sys
import json
from datetime import datetime
from logging import INFO

from vnpy.trader.setting import SETTINGS
from vnpy.app.cta_strategy.backtesting import BacktestingEngine
from vnpy.app.cta_strategy.strategies.atr_adx_sma_m1_strategy import (
    AtrAdxSmaM1Strategy,
)
# from vnpy.app.cta_strategy.strategies.cci_atr_strategy import (
#     CciAtrStrategy,
# )
# from vnpy.app.cta_strategy.strategies.cmo_atr_strategy import (
#     CmoAtrStrategy,
# )
# from vnpy.app.cta_strategy.strategies.dema_atr_strategy import (
#     DemaAtrStrategy,
# )
# from vnpy.app.cta_strategy.strategies.donchian_atr_strategy import (
#     DonchianAtrStrategy,
# )
# from vnpy.app.cta_strategy.strategies.ht_atr_strategy import (
#     HtAtrStrategy,
# )
# from vnpy.app.cta_strategy.strategies.kama_atr_strategy import (
#     KamaAtrStrategy,
# )
# from vnpy.app.cta_strategy.strategies.keltner_atr_strategy import (
#     KeltnerAtrStrategy,
# )
# from vnpy.app.cta_strategy.strategies.macd_atr_strategy import (
#     MacdAtrStrategy,
# )
# from vnpy.app.cta_strategy.strategies.rsi_atr_strategy import (
#     RsiAtrStrategy,
# )
# from vnpy.app.cta_strategy.strategies.sar_atr_strategy import (
#     SarAtrStrategy,
# )
# from vnpy.app.cta_strategy.strategies.tema_atr_strategy import (
#     TemaAtrStrategy,
# )
# from vnpy.app.cta_strategy.strategies.trima_atr_strategy import (
#     TrimaAtrStrategy,
# )

from vnpy.app.cta_strategy.strategies.boll_cci_m15_strategy import (
    BollCciM15Strategy,
)
from vnpy.app.cta_strategy.strategies.dual_thrust_strategy import (
    DualThrustStrategy,
)
from vnpy.app.cta_strategy.strategies.king_keltner_strategy import (
    KingKeltnerStrategy,
)
# from vnpy.app.cta_strategy.strategies.multi_timeframe_strategy import (
#     MultiTimeframeStrategy,
# )

def make_pair(it, s, reverse):
    key = '{} {}{}'.format(it['vt_symbol'], s.model_id, ' REV' if reverse else '')
    value = {
        "class_name": s.__name__,
        # "vt_symbol": it['vt_symbol'].replace('-', ''),
        "vt_symbol": it['vt_symbol'],
        "setting": {
            "reverse": reverse,
        }
    }
    return key, value


def main():
    instruments = [{
        'vt_symbol': 'BTC-USDT.OKEX',
        'price_tick': 0.01,
    }, {
        'vt_symbol': 'BCH-USDT.OKEX',
        'price_tick': 0.01,
    }, {
        'vt_symbol': 'BSV-USDT.OKEX',
        'price_tick': 0.01,
    }, {
        'vt_symbol': 'LTC-USDT.OKEX',
        'price_tick': 0.001,
    }, {
        'vt_symbol': 'ETH-USDT.OKEX',
        'price_tick': 0.001,
    }, {
        'vt_symbol': 'ETC-USDT.OKEX',
        'price_tick': 0.001,
    }, {
        'vt_symbol': 'EOS-USDT.OKEX',
        'price_tick': 0.001,
    }, {
        'vt_symbol': 'DASH-USDT.OKEX',
        'price_tick': 0.001,
    }]

    #
    strategy_classes = [
        AtrAdxSmaM1Strategy, BollCciM15Strategy,
        DualThrustStrategy, KingKeltnerStrategy
    ]

    settings = dict()
    # 4 * 8 = 32
    for it in instruments:
        for s in strategy_classes:
            k, v = make_pair(it, s, False)
            settings[k] = v

    print(f"Total {len(settings)} strategies")
    with open('cta_strategy_setting.json', 'w', encoding='utf-8') as f:
        json.dump(settings, f, indent=2)


if __name__ == "__main__":
    main()
