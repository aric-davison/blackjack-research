from abc import ABC, abstractmethod


class BaseAlgorithm(ABC):
    """Abstract base class for blackjack strategy algorithms."""

    @property
    @abstractmethod
    def name(self) -> str:
        """String label for reports."""
        ...

    @abstractmethod
    def compute_strategy(self) -> dict:
        """Compute and return a strategy dictionary.

        Returns:
            dict mapping (player_value, dealer_upcard, has_usable_ace) -> action
            where action is one of 'hit', 'stand', 'double', 'split'
        """
        ...
