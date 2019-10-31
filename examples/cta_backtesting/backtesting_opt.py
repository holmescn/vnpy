from pprint import pprint
from sys import argv
from vnpy.app.cta_strategy.backtesting import BacktestingEngine, OptimizationSetting
from vnpy.app.cta_strategy.strategies.atr_adx_sma_m1_strategy import AtrAdxSmaM1Strategy
from vnpy.app.cta_strategy.strategies.boll_cci_m15_strategy import BollCciM15Strategy
from vnpy.app.cta_strategy.strategies.dual_thrust_strategy import DualThrustStrategy
from vnpy.app.cta_strategy.strategies.king_keltner_strategy import KingKeltnerStrategy
from vnpy.app.cta_strategy.strategies.r_breaker_m1_strategy import RBreakerM1Strategy
from datetime import datetime

def optimize(vt_symbol):
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

    engine.add_strategy(RBreakerM1Strategy, {})
    # engine.load_data()
    # engine.run_backtesting()
    # engine.calculate_result()
    # engine.calculate_statistics()

    setting = OptimizationSetting()
    setting.set_target("total_return")

    setting.add_parameter('setup_coef', 0.05, 1, 0.05)
    setting.add_parameter('break_coef', 0.05, 1, 0.05)
    setting.add_parameter('enter_coef1', 0.5, 1.5, 0.05)
    setting.add_parameter('enter_coef2', 0.05, 1, 0.05)
    setting.add_parameter('trailing_percent', 1, 10, 1)

    return engine.run_ga_optimization(setting, population_size=20, ngen_size=1000)


# ['BTC', 'BCH', 'BSV', 'ETH', 'ETC', 'EOS', 'LTC', 'DASH']:
symbol = argv[1]
vt_symbol = f"{symbol}USDT.OKEX"
for x in optimize(vt_symbol):
    params, r, _ = x
    print(symbol)
    pprint(params)
    print("total_returns = ", r)


# for vt_symbol, opt_r in results.items():
#     print('\n', vt_symbol)
#     for p, r, _ in opt_r:
#         for k, v in p.items():
#             print(f'{k} {v:.2f}')
#         print(f"total_return: {r:.3f}\n")
