import argparse
from functools import partial
from datetime import datetime
from bayes_opt import BayesianOptimization
from vnpy.app.cta_strategy.backtesting import BacktestingEngine, OptimizationSetting
from vnpy.app.cta_strategy.strategies.r_breaker_m1_strategy import RBreakerM1Strategy


def target_func(setup_coef, break_coef, enter_coef1, enter_coef2, trailing_percent, vt_symbol):
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
    engine.add_strategy(RBreakerM1Strategy, {
        "setup_coef": round(setup_coef, 2),
        "break_coef": round(break_coef, 2),
        "enter_coef1": round(enter_coef1, 2),
        "enter_coef2": round(enter_coef2, 2),
        "trailing_percent": round(trailing_percent, 2),
    })    
    engine.run_backtesting()
    engine.calculate_result()
    results = engine.calculate_statistics(output=False)
    target_value = results['total_return']
    return target_value


def main(args):
    pbounds = {
        "setup_coef": (0.05, 1.0),
        "break_coef": (0.05, 1.0),
        "enter_coef1": (0.5, 1.5),
        "enter_coef2": (0.05, 1.0),
        "trailing_percent": (0.01, 10.0),
    }

    optimizer = BayesianOptimization(
        f=partial(target_func, vt_symbol=f'{args.symbol}USDT.OKEX'),
        pbounds=pbounds,
        # verbose = 1 prints only when a maximum is observed
        # verbose = 0 is silent
        verbose=2,
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
