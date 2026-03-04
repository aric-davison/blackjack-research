from .base import BaseAlgorithm


class GreedyAlgorithm(BaseAlgorithm):
    """Simple greedy heuristic that ignores dealer upcard and soft/hard distinction."""

    @property
    def name(self) -> str:
        return "greedy"

    def compute_strategy(self) -> dict:
        """Compute greedy strategy over all 360 states.

        Decision rules (applied in order):
        1. player_value >= 17 -> stand
        2. player_value in (10, 11) -> double
        3. player_value <= 11 -> hit (covers 4-9 after rule 2)
        4. player_value 12-16 -> hit
        """
        strategy = {}
        for player_value in range(4, 22):
            for dealer_upcard in range(2, 12):
                for has_usable_ace in [True, False]:
                    if player_value >= 17:
                        action = 'stand'
                    elif player_value in (10, 11):
                        action = 'double'
                    else:
                        action = 'hit'
                    strategy[(player_value, dealer_upcard, has_usable_ace)] = action
        return strategy
