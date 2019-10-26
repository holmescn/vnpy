from pprint import pprint
from vnpy.app.cta_strategy.backtesting import BacktestingEngine, OptimizationSetting
from vnpy.app.cta_strategy.strategies.dual_thrust_strategy import DualThrustStrategy
from datetime import datetime

def optimize(vt_symbol):
    engine = BacktestingEngine()
    engine.set_parameters(
        vt_symbol=vt_symbol,
        interval="1m",
        start=datetime(2019, 9, 1),
        end=datetime(2019, 10, 20),
        rate=0.0,
        slippage=0.0,
        size=1,
        pricetick=0.01,
        capital=200_000,
    )

    engine.add_strategy(DualThrustStrategy, {})
    engine.load_data()

    setting = OptimizationSetting()
    setting.set_target("total_return")

    setting.add_parameter('k1', 0.1, 5, 0.1)
    setting.add_parameter('k2', 0.1, 5, 0.1)

    return engine.run_ga_optimization(setting, population_size=20, ngen_size=500)


results = dict()
for symbol in ['BTC', 'BCH', 'BSV', 'ETH', 'ETC', 'EOS', 'LTC', 'DASH']:
    vt_symbol = f"{symbol}USDT.OKEX"
    results[vt_symbol] = optimize(vt_symbol)


for vt_symbol, opt_r in results.items():
    print('\n', vt_symbol)
    for p, r, _ in opt_r:
        for k, v in p.items():
            print(f'{k} {v:.2f}')
        print(f"total_return: {r:.3f}\n")
