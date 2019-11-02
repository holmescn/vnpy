import argparse
from functools import partial
from datetime import datetime
from bayes_opt import BayesianOptimization
from vnpy.app.cta_strategy.backtesting import BacktestingEngine, OptimizationSetting
from vnpy.app.cta_strategy.strategies.keltner_cci_m15_strategy import KeltnerCciM15Strategy


def target_func(keltner_length, keltner_dev, cci_window, atr_window, sl_multiplier, vt_symbol):
    engine = BacktestingEngine()
    engine.set_parameters(
        vt_symbol=vt_symbol,
        interval="1m",
        start=datetime(2019, 9, 1),
        end=datetime(2019, 10, 25),
        rate=0.0,
        slippage=0.0,
        size=1,
        pricetick=0.01,
        capital=200_000,
    )
    engine.output = lambda m: None

    engine.load_data()
    engine.add_strategy(KeltnerCciM15Strategy, {
        "keltner_length": round(keltner_length, 2),
        "keltner_dev": round(keltner_dev, 2),
        "cci_window": round(cci_window, 2),
        "atr_window": round(atr_window, 2),
        "sl_multiplier": round(sl_multiplier, 2),
    })
    engine.run_backtesting()
    engine.calculate_result()
    results = engine.calculate_statistics(output=False)
    target_value = results['total_return']
    return target_value


def main(args):
    pbounds = {
        "keltner_length": (5.0, 50.0),
        "keltner_dev": (0.1, 5),
        "cci_window": (5.0, 60.0),
        "atr_window": (5.0, 60.0),
        "sl_multiplier": (1.0, 5.0),
    }

    optimizer = BayesianOptimization(
        f=partial(target_func, vt_symbol=f'{args.symbol}USDT.OKEX'),
        pbounds=pbounds,
        # verbose = 2 prints every observed values
        # verbose = 1 prints only when a maximum is observed
        # verbose = 0 is silent
        verbose=1,
        random_state=1,
    )

    optimizer.maximize(
        init_points=50,
        n_iter=500,
    )
    print(optimizer.max)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('symbol', type=str, action='store')
    main(parser.parse_args())
