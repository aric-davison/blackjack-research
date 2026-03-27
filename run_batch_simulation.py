"""Run batch simulations (N trials per algorithm) and log results to CSV."""

import csv
import os
import statistics
import time
import tracemalloc
from datetime import datetime

from src.algorithms.brute_force import BruteForceAlgorithm
from src.algorithms.dynamic_programming import DynamicProgrammingAlgorithm
from src.algorithms.greedy import GreedyAlgorithm
from src.evaluation.harness import EvaluationHarness
from src.evaluation.optimal import OPTIMAL_STRATEGY

NUM_TRIALS = 100
NUM_HANDS = 1_000_000
BET = 10

algorithms = [
    BruteForceAlgorithm(),
    DynamicProgrammingAlgorithm(),
    GreedyAlgorithm(),
]

DISPLAY_NAMES = {
    'dynamic_programming': 'DP (memo)',
}

harness = EvaluationHarness(num_hands=NUM_HANDS, bet=BET)

os.makedirs('logs', exist_ok=True)
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
csv_path = f'logs/batch_{timestamp}.csv'

CSV_FIELDS = [
    'algorithm', 'trial', 'num_hands',
    'wins', 'losses', 'pushes', 'blackjacks',
    'win_rate', 'average_return', 'house_edge',
    'sim_runtime_seconds',
    'strategy_accuracy', 'compute_time_seconds', 'compute_memory_bytes',
]

all_results = {}

with open(csv_path, 'w', newline='') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=CSV_FIELDS)
    writer.writeheader()

    for algo in algorithms:
        display = DISPLAY_NAMES.get(algo.name, algo.name)

        # Phase 1: Compute strategy once
        print(f"\n{'='*60}")
        print(f"Computing strategy: {display}")
        print(f"{'='*60}")
        tracemalloc.start()
        t0 = time.perf_counter()
        strategy = algo.compute_strategy()
        compute_time = time.perf_counter() - t0
        _, compute_memory = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        accuracy = EvaluationHarness.compute_accuracy(strategy, OPTIMAL_STRATEGY)
        print(f"  Accuracy: {accuracy:.1%}  |  Compute: {compute_time:.4f}s  |  Memory: {compute_memory / 1024:.1f} KB")

        # Phase 2: Run N trials
        print(f"Running {NUM_TRIALS} trials of {NUM_HANDS:,} hands each...")
        algo_rows = []
        for trial in range(1, NUM_TRIALS + 1):
            result = harness.evaluate(strategy, algo.name)
            row = {
                'algorithm': algo.name,
                'trial': trial,
                'num_hands': NUM_HANDS,
                'wins': result['wins'],
                'losses': result['losses'],
                'pushes': result['pushes'],
                'blackjacks': result['blackjacks'],
                'win_rate': result['win_rate'],
                'average_return': result['average_return'],
                'house_edge': result['house_edge'],
                'sim_runtime_seconds': result['runtime_seconds'],
                'strategy_accuracy': accuracy,
                'compute_time_seconds': compute_time,
                'compute_memory_bytes': compute_memory,
            }
            writer.writerow(row)
            csvfile.flush()
            algo_rows.append(row)

            if trial == 1 or trial % 10 == 0:
                print(f"  {display}: trial {trial}/{NUM_TRIALS} complete")

        all_results[algo.name] = algo_rows

# Phase 3: Summary table
print(f"\n{'='*70}")
print(f"BATCH SUMMARY — {NUM_TRIALS} trials x {NUM_HANDS:,} hands, ${BET} bet")
print(f"{'='*70}")
print(f"{'Algorithm':<20} {'Accuracy':>10} {'Win Rate':>18} {'House Edge':>18} {'Avg Return':>20}")
print(f"{'-'*20} {'-'*10} {'-'*18} {'-'*18} {'-'*20}")

for algo in algorithms:
    name = algo.name
    display = DISPLAY_NAMES.get(name, name)
    rows = all_results[name]

    acc = rows[0]['strategy_accuracy']
    wr = [r['win_rate'] for r in rows]
    he = [r['house_edge'] for r in rows]
    ar = [r['average_return'] for r in rows]

    wr_mean, wr_std = statistics.mean(wr), statistics.stdev(wr)
    he_mean, he_std = statistics.mean(he), statistics.stdev(he)
    ar_mean, ar_std = statistics.mean(ar), statistics.stdev(ar)

    print(f"{display:<20} {acc:>10.1%} "
          f"{wr_mean:>8.2%} +/- {wr_std:.2%}  "
          f"{he_mean:>8.2%} +/- {he_std:.2%}  "
          f"${ar_mean:>+8.4f} +/- {ar_std:.4f}")

print(f"\nResults saved to: {csv_path}")
