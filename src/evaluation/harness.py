"""Evaluation harness for running blackjack strategy simulations."""

import time
import tracemalloc

from src.engine.game import BlackjackGame
from src.core.player import Player


class EvaluationHarness:
    """Runs a strategy through many hands and collects performance metrics."""

    def __init__(self, num_hands=1_000_000, bet=10, num_decks=6):
        self.num_hands = num_hands
        self.bet = bet
        self.num_decks = num_decks

    def evaluate(self, strategy, algorithm_name):
        """Play num_hands using the given strategy and return metrics.

        Args:
            strategy: dict mapping (player_value, dealer_upcard, has_usable_ace) -> action
            algorithm_name: string label for reports

        Returns:
            dict with keys: algorithm, hands_played, wins, losses, pushes,
            blackjacks, win_rate, average_return, house_edge,
            runtime_seconds, peak_memory_bytes
        """
        starting_chips = 10_000_000_000
        game = BlackjackGame(num_decks=self.num_decks)
        player = Player("eval", starting_chips=starting_chips)

        wins = 0
        losses = 0
        pushes = 0
        blackjacks = 0

        tracemalloc.start()
        start_time = time.perf_counter()

        for _ in range(self.num_hands):
            if game.needs_new_deck:
                game.deck.reset()

            chips_before = player.chips
            game.start_round(player, bet=self.bet)

            # Check for natural blackjack
            if game.player_hand.is_blackjack():
                blackjacks += 1
                game.player_stand()
            else:
                # Check for pair split before regular play
                hand = game.player_hand
                if hand.can_split():
                    card_value = hand.cards[0].value
                    dealer_uc = game.dealer_upcard.value
                    if strategy.get(('pair', card_value, dealer_uc)) == 'split':
                        game.execute_action('split')

                # Play the hand(s) using strategy lookups
                while not game.game_over:
                    state = game.get_state()
                    num_cards = len(game.player_hand.cards)
                    action = self._lookup_action(strategy, state, num_cards)
                    game.execute_action(action)

            # Categorize result
            profit = player.chips - chips_before
            if profit > 0:
                wins += 1
            elif profit < 0:
                losses += 1
            else:
                pushes += 1

        end_time = time.perf_counter()
        _, peak_memory = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        runtime_seconds = end_time - start_time
        total_wagered = self.num_hands * self.bet
        net_profit = player.chips - starting_chips
        win_rate = wins / self.num_hands if self.num_hands > 0 else 0
        average_return = net_profit / self.num_hands if self.num_hands > 0 else 0
        house_edge = -net_profit / total_wagered if total_wagered > 0 else 0

        return {
            'algorithm': algorithm_name,
            'hands_played': self.num_hands,
            'wins': wins,
            'losses': losses,
            'pushes': pushes,
            'blackjacks': blackjacks,
            'win_rate': win_rate,
            'average_return': average_return,
            'house_edge': house_edge,
            'runtime_seconds': runtime_seconds,
            'peak_memory_bytes': peak_memory,
        }

    @staticmethod
    def _lookup_action(strategy, state, num_cards):
        """Look up action from strategy with fallbacks.

        - Missing state -> 'stand'
        - 'double' with num_cards > 2 -> 'hit'
        - 'split' with num_cards > 2 -> 'hit'
        """
        action = strategy.get(state, 'stand')
        if action == 'double' and num_cards > 2:
            action = 'hit'
        elif action == 'split' and num_cards > 2:
            action = 'hit'
        return action

    @staticmethod
    def compute_accuracy(strategy, optimal_strategy):
        """Compute the percentage of states where strategy matches optimal.

        Args:
            strategy: dict mapping state tuples to actions
            optimal_strategy: dict mapping state tuples to actions

        Returns:
            float: fraction of matching states (0.0 to 1.0)
        """
        if not optimal_strategy:
            return 0.0
        matches = 0
        total = len(optimal_strategy)
        for state, optimal_action in optimal_strategy.items():
            if strategy.get(state) == optimal_action:
                matches += 1
        return matches / total if total > 0 else 0.0
