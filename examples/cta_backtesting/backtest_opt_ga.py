import argparse
import random
from multiprocessing import Pool, cpu_count
from pprint import pprint
from datetime import datetime
from deap import base, creator, tools
from deap.algorithms import varAnd, varOr
from vnpy.app.cta_strategy.backtesting import BacktestingEngine, OptimizationSetting

from vnpy.app.cta_strategy.strategies.r_breaker_m1_strategy import RBreakerM1Strategy

opt_setting = OptimizationSetting()
opt_setting.set_target("total_return")

opt_setting.add_parameter('setup_coef', 0.05, 1, 0.05)
opt_setting.add_parameter('break_coef', 0.05, 1, 0.05)
opt_setting.add_parameter('enter_coef1', 0.5, 1.5, 0.05)
opt_setting.add_parameter('enter_coef2', 0.05, 1, 0.05)
opt_setting.add_parameter('trailing_percent', 0.1, 10, 0.1)


def evaluate(individual, vt_symbol):
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
        k: round(v, 2) for k, v in individual.items()
    })    
    engine.run_backtesting()
    engine.calculate_result()
    results = engine.calculate_statistics(output=False)
    target_value = results[opt_setting.target_name]
    return target_value,


def initIndividual(icls):
    return icls(**{
        k: random.choice(v)
        for k, v in opt_setting.params.items()
    })


def crossover(ind1, ind2):
    for k in opt_setting.params:
        if random.random() < 0.5:
            ind1[k] = ind2[k]
        else:
            ind2[k] = ind1[k]
    return ind1, ind2


def mutate(individual, indpb):
    for k in individual:
        if random.random() < indpb:
            individual[k] = random.choice(opt_setting.params[k])
    return individual,


def main(args):
    pop_size = 50
    n_gen = 100
    vt_symbol = f"{args.symbol}USDT.OKEX"

    creator.create("FitnessMax", base.Fitness, weights=(1.0,))
    creator.create("Individual", dict, fitness=creator.FitnessMax)

    toolbox = base.Toolbox()
    toolbox.register("individual", initIndividual, creator.Individual)
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)
    toolbox.register("mate", crossover)
    toolbox.register("mutate", mutate, indpb=0.1)
    toolbox.register("select", tools.selTournament, tournsize=3)
    toolbox.register("evaluate", evaluate)

    pop = toolbox.population(n=pop_size)

    # Evaluate the entire population
    pool = Pool(cpu_count())
    results = [pool.apply_async(evaluate, (dict(ind), vt_symbol))
                for ind in pop]
    fitnesses = [r.get() for r in results]

    best_fit = 0.0
    best_ind = None
    for ind, fit in zip(pop, fitnesses):
        ind.fitness.values = fit
        if fit[0] > best_fit:
            best_fit = fit[0]
            best_ind = ind
            print(f"Found best: {best_fit:.2f}")
            pprint({k: round(v, 2) for k, v in best_ind.items()})
            print('\n')

    for g in range(n_gen):
        # Select the next generation individuals
        offspring = map(toolbox.clone, toolbox.select(pop, len(pop)))
        
        # Apply crossover and mutation on the offspring
        offspring = varAnd(offspring, toolbox, cxpb=0.5, mutpb=0.2)

        # Evaluate the individuals with an invalid fitness
        invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
        results = [pool.apply_async(evaluate, (dict(ind), vt_symbol))
                    for ind in invalid_ind]
        fitnesses = [r.get() for r in results]
        for ind, fit in zip(invalid_ind, fitnesses):
            ind.fitness.values = fit
            if fit[0] > best_fit:
                best_fit = fit[0]
                best_ind = ind
                print(f"Found best: {best_fit:.2f} in gen {g}")
                pprint({k: round(v, 2) for k, v in best_ind.items()})
                print('\n')

        # The population is entirely replaced by the offspring
        pop[:] = offspring


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('symbol', type=str, action='store')
    main(parser.parse_args())
