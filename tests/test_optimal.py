"""Tests for the optimal basic strategy table."""

from src.evaluation.optimal import OPTIMAL_STRATEGY


class TestOptimalStrategy:
    def test_is_dict(self):
        assert isinstance(OPTIMAL_STRATEGY, dict)

    def test_completeness_360_regular_entries(self):
        """Optimal strategy has 360 regular states (pair split entries are conditional)."""
        regular = {k: v for k, v in OPTIMAL_STRATEGY.items() if not isinstance(k[0], str)}
        assert len(regular) == 360

    def test_valid_actions(self):
        valid = {'hit', 'stand', 'double', 'split'}
        for action in OPTIMAL_STRATEGY.values():
            assert action in valid

    def test_hard_17_plus_stand(self):
        for pv in range(17, 22):
            for dc in range(2, 12):
                assert OPTIMAL_STRATEGY[(pv, dc, False)] == 'stand'

    def test_hard_8_hit(self):
        for dc in range(2, 12):
            assert OPTIMAL_STRATEGY[(8, dc, False)] == 'hit'

    def test_hard_11_doubles(self):
        for dc in range(2, 11):  # doubles vs 2-10
            assert OPTIMAL_STRATEGY[(11, dc, False)] == 'double'

    def test_hard_11_vs_ace(self):
        # 11 vs ace (dealer 11) -> hit in 6-deck basic strategy
        assert OPTIMAL_STRATEGY[(11, 11, False)] == 'hit'

    def test_soft_20_stand(self):
        for dc in range(2, 12):
            assert OPTIMAL_STRATEGY[(20, dc, True)] == 'stand'

    def test_hard_12_vs_4_stand(self):
        assert OPTIMAL_STRATEGY[(12, 4, False)] == 'stand'

    def test_hard_12_vs_2_hit(self):
        assert OPTIMAL_STRATEGY[(12, 2, False)] == 'hit'

    def test_soft_18_vs_9_hit(self):
        assert OPTIMAL_STRATEGY[(18, 9, True)] == 'hit'

    def test_soft_18_vs_2_stand(self):
        assert OPTIMAL_STRATEGY[(18, 2, True)] == 'stand'

    def test_soft_18_vs_5_double(self):
        assert OPTIMAL_STRATEGY[(18, 5, True)] == 'double'

    def test_state_tuple_format(self):
        for state in OPTIMAL_STRATEGY:
            if isinstance(state[0], str):
                # Pair split entry: ('pair', card_value, dealer_upcard)
                label, cv, dc = state
                assert label == 'pair'
                assert isinstance(cv, int)
                assert isinstance(dc, int)
                assert 2 <= cv <= 11
                assert 2 <= dc <= 11
            else:
                pv, dc, soft = state
                assert isinstance(pv, int)
                assert isinstance(dc, int)
                assert isinstance(soft, bool)
                assert 4 <= pv <= 21
                assert 2 <= dc <= 11
