"""Run 1,000,000-hand simulations for each algorithm and display results."""

from src.algorithms.brute_force import BruteForceAlgorithm
from src.algorithms.greedy import GreedyAlgorithm
from src.evaluation.harness import EvaluationHarness
from src.evaluation.optimal import OPTIMAL_STRATEGY

NUM_HANDS = 1_000_000
BET = 10

algorithms = [
    BruteForceAlgorithm(),
    GreedyAlgorithm(),
]

harness = EvaluationHarness(num_hands=NUM_HANDS, bet=BET)

results = []
for algo in algorithms:
    print(f"\n{'='*60}")
    print(f"Computing strategy: {algo.name}")
    print(f"{'='*60}")
    strategy = algo.compute_strategy()

    accuracy = EvaluationHarness.compute_accuracy(strategy, OPTIMAL_STRATEGY)
    print(f"Strategy accuracy vs optimal: {accuracy:.1%}")

    print(f"Simulating {NUM_HANDS:,} hands...")
    result = harness.evaluate(strategy, algo.name)
    result['strategy_accuracy'] = accuracy
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
print(f"\n{'='*60}")
print(f"SUMMARY — {NUM_HANDS:,} hands, ${BET} bet")
print(f"{'='*60}")
print(f"{'Algorithm':<15} {'Win Rate':>10} {'House Edge':>12} {'Net P/L':>12} {'Accuracy':>10}")
print(f"{'-'*15} {'-'*10} {'-'*12} {'-'*12} {'-'*10}")
for r in results:
    net = r['average_return'] * NUM_HANDS
    print(f"{r['algorithm']:<15} {r['win_rate']:>10.2%} {r['house_edge']:>11.2%} "
          f"${net:>+11,.0f} {r['strategy_accuracy']:>10.1%}")
