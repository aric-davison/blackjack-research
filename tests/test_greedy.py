"""Tests for the greedy algorithm."""

from src.algorithms.greedy import GreedyAlgorithm


class TestGreedyAlgorithm:
    def setup_method(self):
        self.algo = GreedyAlgorithm()
        self.strategy = self.algo.compute_strategy()

    def test_name(self):
        assert self.algo.name == "greedy"

    def test_returns_dict(self):
        assert isinstance(self.strategy, dict)

    def test_completeness_360_entries(self):
        assert len(self.strategy) == 360

    def test_valid_actions(self):
        valid = {'hit', 'stand', 'double', 'split'}
        for action in self.strategy.values():
            assert action in valid

    def test_stand_on_17_plus(self):
        for pv in range(17, 22):
            for dc in range(2, 12):
                for soft in [True, False]:
                    assert self.strategy[(pv, dc, soft)] == 'stand'

    def test_hit_on_4_to_9(self):
        for pv in range(4, 10):
            for dc in range(2, 12):
                for soft in [True, False]:
                    assert self.strategy[(pv, dc, soft)] == 'hit'

    def test_double_on_10_and_11(self):
        for pv in [10, 11]:
            for dc in range(2, 12):
                for soft in [True, False]:
                    assert self.strategy[(pv, dc, soft)] == 'double'

    def test_hit_on_12_to_16(self):
        for pv in range(12, 17):
            for dc in range(2, 12):
                for soft in [True, False]:
                    assert self.strategy[(pv, dc, soft)] == 'hit'

    def test_never_splits(self):
        for action in self.strategy.values():
            assert action != 'split'

    def test_spot_checks(self):
        assert self.strategy[(4, 2, False)] == 'hit'
        assert self.strategy[(11, 11, True)] == 'double'
        assert self.strategy[(17, 6, False)] == 'stand'
        assert self.strategy[(14, 10, True)] == 'hit'
        assert self.strategy[(21, 2, False)] == 'stand'
