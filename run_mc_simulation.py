"""Run Monte Carlo convergence simulation and display results."""

import csv
import os
import time
import tracemalloc
from datetime import datetime

from src.algorithms.monte_carlo import MonteCarloAlgorithm
from src.evaluation.harness import EvaluationHarness
from src.evaluation.optimal import OPTIMAL_STRATEGY
from src.evaluation.export import export_strategies_csv

NUM_EVAL_HANDS = 1_000_000
BET = 10

CONVERGENCE_CSV_FIELDS = [
    'simulations', 'strategy_accuracy', 'states_visited', 'avg_ev_std', 'elapsed_seconds',
]

RESULTS_CSV_FIELDS = [
    'algorithm', 'num_hands', 'bet',
    'wins', 'losses', 'pushes', 'blackjacks',
    'win_rate', 'average_return', 'house_edge', 'net_profit',
    'strategy_accuracy',
    'compute_time_seconds', 'compute_memory_bytes',
    'sim_runtime_seconds', 'sim_peak_memory_bytes',
    'wall_clock_total_seconds',
]

print("=" * 70)
print("Monte Carlo Convergence Analysis")
print("=" * 70)

algo = MonteCarloAlgorithm(seed=42)

print(f"\nRunning MC simulation across {len(algo.convergence_schedule)} intervals...")
print(f"Schedule: {', '.join(f'{n:,}' for n in algo.convergence_schedule)} hands\n")

tracemalloc.start()
compute_start = time.perf_counter()
strategy = algo.compute_strategy()
compute_time = time.perf_counter() - compute_start
_, compute_memory = tracemalloc.get_traced_memory()
tracemalloc.stop()

print(f"Total compute time: {compute_time:.2f}s")
print(f"Peak memory: {compute_memory / 1024:.1f} KB")

# Convergence table
print(f"\n{'Simulations':>14} {'Accuracy':>10} {'States Visited':>16} {'Avg EV Std':>12}")
print(f"{'-'*14} {'-'*10} {'-'*16} {'-'*12}")
for cd in algo.convergence_data:
    visited = sum(1 for c in cd['state_visit_counts'].values() if c > 0)
    variances = [v for v in cd['ev_variance_per_state'].values() if v > 0]
    avg_std = sum(variances) / len(variances) if variances else 0
    print(f"{cd['simulations']:>14,} {cd['strategy_accuracy']:>10.1%} {visited:>16,} {avg_std:>12.4f}")

# Evaluate final strategy
print(f"\n{'='*70}")
print(f"Evaluating final strategy ({NUM_EVAL_HANDS:,} hands, ${BET} bet)")
print(f"{'='*70}")

final_accuracy = EvaluationHarness.compute_accuracy(strategy, OPTIMAL_STRATEGY)
print(f"Final strategy accuracy vs optimal: {final_accuracy:.1%}")

harness = EvaluationHarness(num_hands=NUM_EVAL_HANDS, bet=BET)
result = harness.evaluate(strategy, algo.name)

print(f"  Wins:       {result['wins']:>10,}")
print(f"  Losses:     {result['losses']:>10,}")
print(f"  Pushes:     {result['pushes']:>10,}")
print(f"  Blackjacks: {result['blackjacks']:>10,}")
print(f"  Win rate:   {result['win_rate']:>10.2%}")
print(f"  Avg return: ${result['average_return']:>+9.4f} per hand")
print(f"  House edge: {result['house_edge']:>10.2%}")
print(f"  Sim time:   {result['runtime_seconds']:>10.2f}s")

os.makedirs('logs', exist_ok=True)
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

convergence_csv = f'logs/mc_convergence_{timestamp}.csv'
with open(convergence_csv, 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=CONVERGENCE_CSV_FIELDS)
    writer.writeheader()
    for cd in algo.convergence_data:
        visited = sum(1 for c in cd['state_visit_counts'].values() if c > 0)
        variances = [v for v in cd['ev_variance_per_state'].values() if v > 0]
        avg_std = sum(variances) / len(variances) if variances else 0
        writer.writerow({
            'simulations': cd['simulations'],
            'strategy_accuracy': cd['strategy_accuracy'],
            'states_visited': visited,
            'avg_ev_std': avg_std,
            'elapsed_seconds': cd.get('elapsed_seconds', ''),
        })

results_csv = f'logs/mc_results_{timestamp}.csv'
with open(results_csv, 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=RESULTS_CSV_FIELDS)
    writer.writeheader()
    writer.writerow({
        'algorithm': algo.name,
        'num_hands': NUM_EVAL_HANDS,
        'bet': BET,
        'wins': result['wins'],
        'losses': result['losses'],
        'pushes': result['pushes'],
        'blackjacks': result['blackjacks'],
        'win_rate': result['win_rate'],
        'average_return': result['average_return'],
        'house_edge': result['house_edge'],
        'net_profit': result['average_return'] * NUM_EVAL_HANDS,
        'strategy_accuracy': final_accuracy,
        'compute_time_seconds': compute_time,
        'compute_memory_bytes': compute_memory,
        'sim_runtime_seconds': result['runtime_seconds'],
        'sim_peak_memory_bytes': result['peak_memory_bytes'],
        'wall_clock_total_seconds': compute_time + result['runtime_seconds'],
    })

strategy_csv = f'logs/strategies_mc_{timestamp}.csv'
export_strategies_csv(strategy_csv, {'optimal': OPTIMAL_STRATEGY, algo.name: strategy})
print(f"\nConvergence saved to:    {convergence_csv}")
print(f"Results saved to:        {results_csv}")
print(f"Strategy tables saved to: {strategy_csv}")
