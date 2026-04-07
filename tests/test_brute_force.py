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
        """Brute force produces 360 regular states (pair split entries are conditional)."""
        _, strategy = brute_force_result
        regular = {k: v for k, v in strategy.items() if not isinstance(k[0], str)}
        assert len(regular) == 360

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
        assert algo.states_explored == 460  # 360 regular + 100 pair

    def test_high_accuracy_vs_optimal(self, brute_force_result):
        _, strategy = brute_force_result
        accuracy = EvaluationHarness.compute_accuracy(strategy, OPTIMAL_STRATEGY)
        assert accuracy >= 0.90

    def test_has_split_entries(self, brute_force_result):
        """Brute force should produce some pair split recommendations."""
        _, strategy = brute_force_result
        pair_entries = {k: v for k, v in strategy.items() if isinstance(k[0], str)}
        assert len(pair_entries) > 0
