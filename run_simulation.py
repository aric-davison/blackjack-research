"""Run 1,000,000-hand simulations for each algorithm and display results."""

import csv
import os
import time
import tracemalloc
from datetime import datetime

from src.algorithms.brute_force import BruteForceAlgorithm
from src.algorithms.dynamic_programming import DynamicProgrammingAlgorithm
from src.algorithms.greedy import GreedyAlgorithm
from src.evaluation.harness import EvaluationHarness
from src.evaluation.optimal import OPTIMAL_STRATEGY
from src.evaluation.export import export_strategies_csv

NUM_HANDS = 1_000_000
BET = 10

RESULTS_CSV_FIELDS = [
    'algorithm', 'num_hands', 'bet',
    'wins', 'losses', 'pushes', 'blackjacks',
    'win_rate', 'average_return', 'house_edge', 'net_profit',
    'strategy_accuracy',
    'compute_time_seconds', 'compute_memory_bytes',
    'sim_runtime_seconds', 'sim_peak_memory_bytes',
    'wall_clock_total_seconds',
]

algorithms = [
    BruteForceAlgorithm(),
    DynamicProgrammingAlgorithm(),
    GreedyAlgorithm(),
]

harness = EvaluationHarness(num_hands=NUM_HANDS, bet=BET)

DISPLAY_NAMES = {
    'dynamic_programming': 'DP (memo)',
}

strategies = {'optimal': OPTIMAL_STRATEGY}

results = []
for algo in algorithms:
    display = DISPLAY_NAMES.get(algo.name, algo.name)
    print(f"\n{'='*60}")
    print(f"Computing strategy: {display}")
    print(f"{'='*60}")
    tracemalloc.start()
    compute_start = time.perf_counter()
    strategy = algo.compute_strategy()
    compute_time = time.perf_counter() - compute_start
    _, compute_memory = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    strategies[algo.name] = strategy
    accuracy = EvaluationHarness.compute_accuracy(strategy, OPTIMAL_STRATEGY)
    print(f"Strategy accuracy vs optimal: {accuracy:.1%}")
    print(f"Strategy compute time: {compute_time:.4f}s")
    print(f"Strategy compute peak memory: {compute_memory / 1024:.1f} KB")

    print(f"Simulating {NUM_HANDS:,} hands...")
    result = harness.evaluate(strategy, algo.name)
    result['strategy_accuracy'] = accuracy
    result['compute_time'] = compute_time
    result['compute_memory'] = compute_memory
    result['wall_clock_total'] = compute_time + result['runtime_seconds']
    results.append(result)

    print(f"  Wins:       {result['wins']:>10,}")
    print(f"  Losses:     {result['losses']:>10,}")
    print(f"  Pushes:     {result['pushes']:>10,}")
    print(f"  Blackjacks: {result['blackjacks']:>10,}")
    print(f"  Win rate:   {result['win_rate']:>10.2%}")
    print(f"  Avg return: ${result['average_return']:>+9.4f} per hand")
    print(f"  House edge: {result['house_edge']:>10.2%}")
    print(f"  Runtime:    {result['runtime_seconds']:>10.2f}s")

# Summary comparison
print(f"\n{'='*72}")
print(f"SUMMARY — {NUM_HANDS:,} hands, ${BET} bet")
print(f"{'='*72}")
print(f"{'Algorithm':<20} {'Compute':>10} {'Sim Time':>10} {'Wall Total':>12} {'Win Rate':>10} {'House Edge':>12} {'Net P/L':>12} {'Accuracy':>10}")
print(f"{'-'*20} {'-'*10} {'-'*10} {'-'*12} {'-'*10} {'-'*12} {'-'*12} {'-'*10}")
for r in results:
    net = r['average_return'] * NUM_HANDS
    display = DISPLAY_NAMES.get(r['algorithm'], r['algorithm'])
    print(f"{display:<20} {r['compute_time']:>9.4f}s {r['runtime_seconds']:>9.2f}s {r['wall_clock_total']:>11.2f}s "
          f"{r['win_rate']:>10.2%} {r['house_edge']:>11.2%} ${net:>+11,.0f} {r['strategy_accuracy']:>10.1%}")

os.makedirs('logs', exist_ok=True)
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

results_csv = f'logs/results_{timestamp}.csv'
with open(results_csv, 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=RESULTS_CSV_FIELDS)
    writer.writeheader()
    for r in results:
        writer.writerow({
            'algorithm': r['algorithm'],
            'num_hands': NUM_HANDS,
            'bet': BET,
            'wins': r['wins'],
            'losses': r['losses'],
            'pushes': r['pushes'],
            'blackjacks': r['blackjacks'],
            'win_rate': r['win_rate'],
            'average_return': r['average_return'],
            'house_edge': r['house_edge'],
            'net_profit': r['average_return'] * NUM_HANDS,
            'strategy_accuracy': r['strategy_accuracy'],
            'compute_time_seconds': r['compute_time'],
            'compute_memory_bytes': r['compute_memory'],
            'sim_runtime_seconds': r['runtime_seconds'],
            'sim_peak_memory_bytes': r['peak_memory_bytes'],
            'wall_clock_total_seconds': r['wall_clock_total'],
        })

strategy_csv = f'logs/strategies_{timestamp}.csv'
export_strategies_csv(strategy_csv, strategies)
print(f"\nResults saved to:        {results_csv}")
print(f"Strategy tables saved to: {strategy_csv}")
