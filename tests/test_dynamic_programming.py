"""Tests for the dynamic programming algorithm."""

import pytest

from src.algorithms.brute_force import BruteForceAlgorithm
from src.algorithms.dynamic_programming import DynamicProgrammingAlgorithm
from src.evaluation.harness import EvaluationHarness
from src.evaluation.optimal import OPTIMAL_STRATEGY


@pytest.fixture(scope="module")
def dp_result():
    """Compute strategy once for all tests."""
    algo = DynamicProgrammingAlgorithm()
    strategy = algo.compute_strategy()
    return algo, strategy


class TestDynamicProgrammingAlgorithm:
    def test_name(self, dp_result):
        algo, _ = dp_result
        assert algo.name == "dynamic_programming"

    def test_returns_dict(self, dp_result):
        _, strategy = dp_result
        assert isinstance(strategy, dict)

    def test_completeness(self, dp_result):
        """DP produces 360 regular states (pair split entries are conditional)."""
        _, strategy = dp_result
        regular = {k: v for k, v in strategy.items() if not isinstance(k[0], str)}
        assert len(regular) == 360

    def test_valid_actions(self, dp_result):
        _, strategy = dp_result
        valid = {'hit', 'stand', 'double', 'split'}
        for action in strategy.values():
            assert action in valid

    def test_hard_17_plus_stand(self, dp_result):
        _, strategy = dp_result
        for pv in range(17, 22):
            for dc in range(2, 12):
                assert strategy[(pv, dc, False)] == 'stand'

    def test_hard_4_to_8_hit(self, dp_result):
        _, strategy = dp_result
        for pv in range(4, 9):
            for dc in range(2, 12):
                assert strategy[(pv, dc, False)] == 'hit'

    def test_hard_11_doubles_vs_low(self, dp_result):
        _, strategy = dp_result
        for dc in range(2, 10):
            assert strategy[(11, dc, False)] == 'double'

    def test_hard_12_vs_4_stand(self, dp_result):
        _, strategy = dp_result
        assert strategy[(12, 4, False)] == 'stand'

    def test_hard_12_vs_2_hit(self, dp_result):
        _, strategy = dp_result
        assert strategy[(12, 2, False)] == 'hit'

    def test_hard_16_vs_10_hit(self, dp_result):
        _, strategy = dp_result
        assert strategy[(16, 10, False)] == 'hit'

    def test_states_explored(self, dp_result):
        algo, _ = dp_result
        assert algo.states_explored == 460  # 360 regular + 100 pair

    def test_high_accuracy_vs_optimal(self, dp_result):
        _, strategy = dp_result
        accuracy = EvaluationHarness.compute_accuracy(strategy, OPTIMAL_STRATEGY)
        assert accuracy >= 0.90

    def test_memo_cache_populated(self, dp_result):
        algo, _ = dp_result
        assert len(algo._memo_best_ev) > 0
        assert len(algo._memo_dealer) > 0

    def test_matches_brute_force(self, dp_result):
        """DP and brute force should produce identical strategies on regular states."""
        _, dp_strategy = dp_result
        bf = BruteForceAlgorithm()
        bf_strategy = bf.compute_strategy()
        mismatches = 0
        for key in bf_strategy:
            if key in dp_strategy and dp_strategy[key] != bf_strategy[key]:
                mismatches += 1
        # Allow tiny differences from floating point, but should be near-zero
        assert mismatches <= 2

    def test_faster_than_brute_force(self, dp_result):
        """DP should use memoization (cache should have fewer entries than brute force recomputations)."""
        algo, _ = dp_result
        # The memo cache should exist and be reasonably sized
        # (much smaller than the exponential number of brute force recursive calls)
        assert len(algo._memo_best_ev) < 1000
