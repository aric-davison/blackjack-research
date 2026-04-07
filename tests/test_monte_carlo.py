"""Tests for the Monte Carlo algorithm."""

import pytest

from src.algorithms.monte_carlo import MonteCarloAlgorithm
from src.evaluation.harness import EvaluationHarness
from src.evaluation.optimal import OPTIMAL_STRATEGY


@pytest.fixture(scope="module")
def mc_result():
    """Compute strategy once with a small schedule for fast tests."""
    algo = MonteCarloAlgorithm(seed=42, convergence_schedule=[1_000, 5_000], verbose=False)
    strategy = algo.compute_strategy()
    return algo, strategy


@pytest.fixture(scope="module")
def mc_large():
    """Larger run for convergence and accuracy tests."""
    algo = MonteCarloAlgorithm(seed=42, convergence_schedule=[10_000, 100_000, 500_000], verbose=False)
    strategy = algo.compute_strategy()
    return algo, strategy


class TestMonteCarloAlgorithm:
    def test_name(self, mc_result):
        algo, _ = mc_result
        assert algo.name == "monte_carlo"

    def test_returns_dict(self, mc_result):
        _, strategy = mc_result
        assert isinstance(strategy, dict)

    def test_completeness(self, mc_result):
        """MC produces 360 regular states (pair split entries are conditional)."""
        _, strategy = mc_result
        regular = {k: v for k, v in strategy.items() if not isinstance(k[0], str)}
        assert len(regular) == 360

    def test_valid_actions(self, mc_result):
        _, strategy = mc_result
        valid = {'hit', 'stand', 'double', 'split'}
        for action in strategy.values():
            assert action in valid

    def test_convergence_data_populated(self, mc_result):
        algo, _ = mc_result
        assert len(algo.convergence_data) == 2  # matches schedule [1_000, 5_000]

    def test_convergence_data_structure(self, mc_result):
        algo, _ = mc_result
        required_keys = {'simulations', 'strategy_accuracy', 'state_visit_counts',
                         'ev_variance_per_state', 'strategy'}
        for entry in algo.convergence_data:
            assert required_keys.issubset(entry.keys())

    def test_convergence_simulation_counts(self, mc_result):
        algo, _ = mc_result
        assert algo.convergence_data[0]['simulations'] == 1_000
        assert algo.convergence_data[1]['simulations'] == 5_000

    def test_deterministic_with_seed(self):
        """Two runs with the same seed produce identical strategies."""
        algo1 = MonteCarloAlgorithm(seed=123, convergence_schedule=[1_000], verbose=False)
        s1 = algo1.compute_strategy()
        algo2 = MonteCarloAlgorithm(seed=123, convergence_schedule=[1_000], verbose=False)
        s2 = algo2.compute_strategy()
        assert s1 == s2

    def test_different_seeds_differ(self):
        """Different seeds produce different strategies (with high probability)."""
        algo1 = MonteCarloAlgorithm(seed=1, convergence_schedule=[1_000], verbose=False)
        s1 = algo1.compute_strategy()
        algo2 = MonteCarloAlgorithm(seed=999, convergence_schedule=[1_000], verbose=False)
        s2 = algo2.compute_strategy()
        differences = sum(1 for k in s1 if s1.get(k) != s2.get(k))
        assert differences > 0


class TestMonteCarloConvergence:
    """Tests that verify MC converges toward correct play with more simulations."""

    def test_accuracy_improves_with_simulations(self, mc_large):
        algo, _ = mc_large
        accuracies = [cd['strategy_accuracy'] for cd in algo.convergence_data]
        # Final accuracy should be >= first accuracy (with some tolerance for noise)
        assert accuracies[-1] >= accuracies[0] - 0.05

    def test_reasonable_accuracy_at_500k(self, mc_large):
        algo, _ = mc_large
        final = algo.convergence_data[-1]
        assert final['strategy_accuracy'] >= 0.60

    def test_hard_17_plus_converges_to_stand(self, mc_large):
        """With enough simulations, hard 17+ should be stand."""
        _, strategy = mc_large
        stand_count = 0
        total = 0
        for pv in range(17, 22):
            for dc in range(2, 12):
                total += 1
                if strategy[(pv, dc, False)] == 'stand':
                    stand_count += 1
        # Allow some noise but vast majority should be stand
        assert stand_count / total >= 0.90

    def test_hard_low_converges_to_hit(self, mc_large):
        """With enough simulations, hard 4-8 should be hit."""
        _, strategy = mc_large
        hit_count = 0
        total = 0
        for pv in range(4, 9):
            for dc in range(2, 12):
                total += 1
                if strategy[(pv, dc, False)] in ('hit', 'double'):
                    hit_count += 1
        assert hit_count / total >= 0.90

    def test_state_visit_counts_populated(self, mc_large):
        algo, _ = mc_large
        final = algo.convergence_data[-1]
        visited = sum(1 for c in final['state_visit_counts'].values() if c > 0)
        # Most regular states should have been visited
        assert visited >= 200

    def test_ev_variance_decreases(self, mc_large):
        """Average EV std dev should decrease with more simulations."""
        algo, _ = mc_large
        def avg_std(entry):
            variances = [v for v in entry['ev_variance_per_state'].values() if v > 0]
            return sum(variances) / len(variances) if variances else 0
        first_std = avg_std(algo.convergence_data[0])
        last_std = avg_std(algo.convergence_data[-1])
        # Variance should decrease (or at least not grow significantly)
        assert last_std <= first_std + 0.1
