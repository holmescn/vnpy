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
from vnpy.app.cta_strategy.strategies.double_ma_strategy import (
    DoubleMaStrategy,
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
from vnpy.app.cta_strategy.strategies.turtle_signal_strategy import (
    TurtleSignalStrategy,
)


SETTINGS["log.active"] = True
SETTINGS["log.level"] = INFO
SETTINGS["log.console"] = True
SETTINGS["log.file"] = True

if sys.platform == 'win32':
    SETTINGS["database.database"] = "D:\\coin-database.sqlite"


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
        'fixed_size': 200,
        'price_tick': 0.01,
    }, {
        'vt_symbol': 'BCHUSDK.OKEX',
        'fixed_size': 200,
        'price_tick': 0.01,
    }, {
        'vt_symbol': 'LTCUSDT.OKEX',
        'fixed_size': 200,
        'price_tick': 0.001,
    }, {
        'vt_symbol': 'LTCUSDK.OKEX',
        'fixed_size': 200,
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
        'fixed_size': 200,
        'price_tick': 0.001,
    }, {
        'vt_symbol': 'EOSUSDK.OKEX',
        'fixed_size': 200,
        'price_tick': 0.001,
    }]

    # 14 * 2 = 28
    revertable_strategies = [
        AdxAtrStrategy, BollAtrStrategy, CciAtrStrategy, CmoAtrStrategy,
        DemaAtrStrategy, DonchianAtrStrategy, HtAtrStrategy,
        KamaAtrStrategy, KeltnerAtrStrategy, MacdAtrStrategy, RsiAtrStrategy,
        SarAtrStrategy, TemaAtrStrategy, TrimaAtrStrategy
    ]

    # 6
    other_strategies = [
        BollChannelStrategy, DoubleMaStrategy, DualThrustStrategy, KingKeltnerStrategy,
        MultiTimeframeStrategy, TurtleSignalStrategy
    ]

    # (6 + 28) * 10 = 340
    for it in instruments:
        engine = BacktestingEngine()
        engine.set_parameters(
            vt_symbol=it['vt_symbol'],
            interval="1m",
            start=datetime(2019, 8, 1),
            end=datetime(2019, 9, 17),
            slippage=it['price_tick'],
            rate=0.001 * 0.0,
            size=1,
            pricetick=it['price_tick'],
            capital=1_000_000,
        )
        engine.load_data()

        for s in revertable_strategies:
            engine.add_strategy(s, dict(reverse=False, fixed_size=it['fixed_size']))
            print(engine.strategy.model_id)
            engine.run_backtesting()
            engine.calculate_result()
            engine.calculate_statistics()
            engine.clear_data()
            
            engine.add_strategy(s, dict(reverse=True, fixed_size=it['fixed_size']))
            print(engine.strategy.model_id)
            engine.run_backtesting()
            engine.calculate_result()
            engine.calculate_statistics()
            engine.clear_data()

        for s in other_strategies:
            engine.add_strategy(s, dict(fixed_size=it['fixed_size']))
            print(engine.strategy.model_id)
            engine.run_backtesting()
            engine.calculate_result()
            engine.calculate_statistics()
            engine.clear_data()


if __name__ == "__main__":
    main()
