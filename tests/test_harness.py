"""Tests for the evaluation harness."""

import pytest

from src.evaluation.harness import EvaluationHarness
from src.evaluation.optimal import OPTIMAL_STRATEGY
from src.algorithms.greedy import GreedyAlgorithm


@pytest.fixture
def greedy_result():
    algo = GreedyAlgorithm()
    strategy = algo.compute_strategy()
    harness = EvaluationHarness(num_hands=10_000, bet=10)
    return harness.evaluate(strategy, algo.name)


class TestHarnessResults:
    def test_returns_all_keys(self, greedy_result):
        expected_keys = {
            'algorithm', 'hands_played', 'wins', 'losses', 'pushes',
            'blackjacks', 'win_rate', 'average_return', 'house_edge',
            'runtime_seconds', 'peak_memory_bytes',
        }
        assert set(greedy_result.keys()) == expected_keys

    def test_wins_losses_pushes_sum(self, greedy_result):
        total = greedy_result['wins'] + greedy_result['losses'] + greedy_result['pushes']
        assert total == greedy_result['hands_played']

    def test_algorithm_name(self, greedy_result):
        assert greedy_result['algorithm'] == 'greedy'

    def test_win_rate_in_range(self, greedy_result):
        assert 0.0 <= greedy_result['win_rate'] <= 1.0

    def test_blackjacks_nonneg(self, greedy_result):
        assert greedy_result['blackjacks'] >= 0

    def test_runtime_positive(self, greedy_result):
        assert greedy_result['runtime_seconds'] > 0

    def test_hands_played(self, greedy_result):
        assert greedy_result['hands_played'] == 10_000


class TestLookupAction:
    def test_missing_state_fallback(self):
        strategy = {}
        action = EvaluationHarness._lookup_action(strategy, (99, 99, False), 2)
        assert action == 'stand'

    def test_double_fallback_to_hit(self):
        strategy = {(10, 5, False): 'double'}
        action = EvaluationHarness._lookup_action(strategy, (10, 5, False), 3)
        assert action == 'hit'

    def test_split_fallback_to_hit(self):
        strategy = {(16, 5, False): 'split'}
        action = EvaluationHarness._lookup_action(strategy, (16, 5, False), 3)
        assert action == 'hit'


class TestAccuracy:
    def test_accuracy_100_self_compare(self):
        accuracy = EvaluationHarness.compute_accuracy(OPTIMAL_STRATEGY, OPTIMAL_STRATEGY)
        assert accuracy == 1.0

    def test_accuracy_0_empty(self):
        accuracy = EvaluationHarness.compute_accuracy({}, OPTIMAL_STRATEGY)
        assert accuracy == 0.0
