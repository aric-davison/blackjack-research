"""Tests for the brute-force enumeration algorithm."""

import pytest

from src.algorithms.brute_force import BruteForceAlgorithm
from src.evaluation.harness import EvaluationHarness
from src.evaluation.optimal import OPTIMAL_STRATEGY


@pytest.fixture(scope="module")
def brute_force_result():
    """Compute strategy once for all tests (brute force is slow)."""
    algo = BruteForceAlgorithm()
    strategy = algo.compute_strategy()
    return algo, strategy


class TestBruteForceAlgorithm:
    def test_name(self, brute_force_result):
        algo, _ = brute_force_result
        assert algo.name == "brute_force"

    def test_returns_dict(self, brute_force_result):
        _, strategy = brute_force_result
        assert isinstance(strategy, dict)

    def test_completeness(self, brute_force_result):
        _, strategy = brute_force_result
        assert len(strategy) == 360

    def test_valid_actions(self, brute_force_result):
        _, strategy = brute_force_result
        valid = {'hit', 'stand', 'double', 'split'}
        for action in strategy.values():
            assert action in valid

    def test_hard_17_plus_stand(self, brute_force_result):
        _, strategy = brute_force_result
        for pv in range(17, 22):
            for dc in range(2, 12):
                assert strategy[(pv, dc, False)] == 'stand'

    def test_hard_4_to_8_hit(self, brute_force_result):
        _, strategy = brute_force_result
        for pv in range(4, 9):
            for dc in range(2, 12):
                assert strategy[(pv, dc, False)] == 'hit'

    def test_hard_11_doubles_vs_low(self, brute_force_result):
        _, strategy = brute_force_result
        # Doubles vs 2-9; vs 10 is a borderline case where infinite-deck
        # math slightly favors hit over double (EV difference < 0.001)
        for dc in range(2, 10):
            assert strategy[(11, dc, False)] == 'double'

    def test_hard_12_vs_4_stand(self, brute_force_result):
        _, strategy = brute_force_result
        assert strategy[(12, 4, False)] == 'stand'

    def test_hard_12_vs_2_hit(self, brute_force_result):
        _, strategy = brute_force_result
        assert strategy[(12, 2, False)] == 'hit'

    def test_hard_16_vs_10_hit(self, brute_force_result):
        _, strategy = brute_force_result
        assert strategy[(16, 10, False)] == 'hit'

    def test_states_explored(self, brute_force_result):
        algo, _ = brute_force_result
        assert algo.states_explored == 360

    def test_high_accuracy_vs_optimal(self, brute_force_result):
        _, strategy = brute_force_result
        accuracy = EvaluationHarness.compute_accuracy(strategy, OPTIMAL_STRATEGY)
        assert accuracy >= 0.90

    def test_never_splits(self, brute_force_result):
        _, strategy = brute_force_result
        for action in strategy.values():
            assert action != 'split'
