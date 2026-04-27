"""Monte Carlo algorithm for computing optimal blackjack strategy.

Learns strategy by simulating actual hands through the game engine,
using exploring starts to estimate expected value for each (state, action) pair.
Tracks convergence across multiple simulation intervals.
"""

import random
import math
import time
import sys

from .base import BaseAlgorithm
from src.engine.game import BlackjackGame
from src.core.player import Player
from src.evaluation.optimal import OPTIMAL_STRATEGY
from src.evaluation.harness import EvaluationHarness


class MonteCarloAlgorithm(BaseAlgorithm):

    def __init__(self, num_decks=6, seed=None, convergence_schedule=None, verbose=True):
        self.num_decks = num_decks
        self.seed = seed
        self.verbose = verbose
        self.convergence_schedule = convergence_schedule or [
            10_000, 100_000, 500_000, 1_000_000, 5_000_000, 10_000_000
        ]
        # Welford's online stats: {(state_key, action): (count, mean, M2)}
        self.ev_data = {}
        # Visit counts per state
        self.state_visits = {}
        # Per-interval snapshots
        self.convergence_data = []

    @property
    def name(self) -> str:
        return "monte_carlo"

    def compute_strategy(self) -> dict:
        """Run MC simulation across all convergence intervals.

        Returns the final strategy (from the largest interval).
        Populates self.convergence_data with per-interval snapshots.
        """
        rng = random.Random(self.seed)
        # Seed global random state too (Deck.shuffle uses random.shuffle)
        if self.seed is not None:
            random.seed(self.seed)
        game = BlackjackGame(num_decks=self.num_decks)
        player = Player("mc_learner", starting_chips=10_000_000_000)
        bet = 10

        max_hands = max(self.convergence_schedule)
        checkpoint_idx = 0
        self.ev_data = {}
        self.state_visits = {}
        self.convergence_data = []

        start_time = time.time()
        last_print_time = start_time
        print_interval = 2.0  # seconds between progress updates

        if self.verbose:
            print(f"Monte Carlo: simulating {max_hands:,} hands...")

        for hand_num in range(1, max_hands + 1):
            self._simulate_hand(game, player, rng, bet)

            # Progress update on a time interval
            if self.verbose:
                now = time.time()
                if now - last_print_time >= print_interval:
                    elapsed = now - start_time
                    rate = hand_num / elapsed
                    remaining = (max_hands - hand_num) / rate if rate > 0 else 0
                    pct = hand_num / max_hands * 100
                    print(f"\r  {hand_num:>12,} / {max_hands:,} hands "
                          f"({pct:5.1f}%) | {rate:,.0f} hands/sec | "
                          f"~{remaining:.0f}s remaining", end="", flush=True)
                    last_print_time = now

            # Snapshot at each checkpoint
            if checkpoint_idx < len(self.convergence_schedule) and \
               hand_num == self.convergence_schedule[checkpoint_idx]:
                elapsed = time.time() - start_time
                strategy = self._build_strategy()
                metrics = self._compute_metrics(strategy, hand_num)
                metrics['elapsed_seconds'] = elapsed
                self.convergence_data.append(metrics)
                checkpoint_idx += 1
                if self.verbose:
                    print(f"\r  Checkpoint {hand_num:>12,} | "
                          f"accuracy: {metrics['strategy_accuracy']:.1%} | "
                          f"elapsed: {elapsed:.1f}s")

        if self.verbose:
            total = time.time() - start_time
            print(f"  Done. {max_hands:,} hands in {total:.1f}s "
                  f"({max_hands / total:,.0f} hands/sec)")

        return self._build_strategy()

    def _simulate_hand(self, game, player, rng, bet):
        """Simulate one hand with exploring starts.

        Randomly picks the first action, then follows current best policy.
        Records only the first (state, action) -> reward pair.
        """
        if game.needs_new_deck:
            game.deck.reset()

        chips_before = player.chips
        game.start_round(player, bet=bet)

        # Skip natural blackjacks -- no decision to make
        if game.player_hand.is_blackjack():
            game.player_stand()
            return

        # Determine available actions for exploration
        hand = game.player_hand
        is_pair = hand.can_split()

        if is_pair:
            # 50% chance to explore split
            if rng.random() < 0.5:
                explore_action = 'split'
            else:
                explore_action = rng.choice(['hit', 'stand', 'double'])
        else:
            explore_action = rng.choice(['hit', 'stand', 'double'])

        # Record the state before the exploration action
        if explore_action == 'split':
            card_value = hand.cards[0].value
            dealer_uc = game.dealer_upcard.value
            state_key = ('pair', card_value, dealer_uc)
            recorded_action = 'split'
        else:
            state_key = game.get_state()
            recorded_action = explore_action
            # Also record for pair comparison if this is a pair hand
            if is_pair:
                pair_key = ('pair', hand.cards[0].value, game.dealer_upcard.value)
                # We'll update the pair no_split data after reward is known

        # Track state visit
        self.state_visits[state_key] = self.state_visits.get(state_key, 0) + 1

        # Execute the exploration action
        game.execute_action(explore_action)

        # Play remaining decisions with current best policy
        while not game.game_over:
            current_hand = game.player_hand
            if current_hand.can_split():
                pair_action = self._get_best_action(
                    ('pair', current_hand.cards[0].value, game.dealer_upcard.value)
                )
                if pair_action == 'split':
                    game.execute_action('split')
                    continue

            state = game.get_state()
            num_cards = len(game.player_hand.cards)
            action = self._get_best_action(state)
            # Can't double/split after initial 2 cards
            if action == 'double' and num_cards > 2:
                action = 'hit'
            elif action == 'split' and num_cards > 2:
                action = 'hit'
            game.execute_action(action)

        # Compute reward
        reward = (player.chips - chips_before) / bet

        # Update EV data with Welford's algorithm
        self._update_ev(state_key, recorded_action, reward)

        # For pair hands where we didn't split, also record under pair key as no_split
        if is_pair and explore_action != 'split':
            pair_key = ('pair', hand.cards[0].value, game.dealer_upcard.value)
            self._update_ev(pair_key, 'no_split', reward)

    def _update_ev(self, state_key, action, reward):
        """Update running mean and variance using Welford's online algorithm."""
        key = (state_key, action)
        count, mean, m2 = self.ev_data.get(key, (0, 0.0, 0.0))
        count += 1
        delta = reward - mean
        mean += delta / count
        delta2 = reward - mean
        m2 += delta * delta2
        self.ev_data[key] = (count, mean, m2)

    def _get_best_action(self, state_key):
        """Return action with highest mean EV for a state, or 'stand' as default."""
        if isinstance(state_key[0], str) and state_key[0] == 'pair':
            # For pair states, check if split is better
            split_data = self.ev_data.get((state_key, 'split'))
            nosplit_data = self.ev_data.get((state_key, 'no_split'))
            if split_data and nosplit_data:
                if split_data[1] > nosplit_data[1]:
                    return 'split'
            elif split_data and not nosplit_data:
                return 'split'
            return 'stand'

        best_action = 'stand'
        best_ev = float('-inf')
        for action in ['hit', 'stand', 'double']:
            data = self.ev_data.get((state_key, action))
            if data:
                _, mean, _ = data
                if mean > best_ev:
                    best_ev = mean
                    best_action = action
        return best_action

    def _build_strategy(self) -> dict:
        """Build complete strategy dict from current EV data."""
        strategy = {}

        # Regular states (360)
        for player_value in range(4, 22):
            for dealer_upcard in range(2, 12):
                for has_usable_ace in [True, False]:
                    state = (player_value, dealer_upcard, has_usable_ace)
                    best_action = 'stand'
                    best_ev = float('-inf')
                    for action in ['hit', 'stand', 'double']:
                        data = self.ev_data.get((state, action))
                        if data:
                            _, mean, _ = data
                            if mean > best_ev:
                                best_ev = mean
                                best_action = action
                    strategy[state] = best_action

        # Pair states
        for card_value in range(2, 12):
            for dealer_upcard in range(2, 12):
                pair_key = ('pair', card_value, dealer_upcard)
                split_data = self.ev_data.get((pair_key, 'split'))
                nosplit_data = self.ev_data.get((pair_key, 'no_split'))
                if split_data and nosplit_data:
                    split_mean = split_data[1]
                    nosplit_mean = nosplit_data[1]
                    if split_mean > nosplit_mean:
                        strategy[pair_key] = 'split'
                elif split_data and not nosplit_data:
                    # Only have split data, include it
                    strategy[pair_key] = 'split'

        return strategy

    def _compute_metrics(self, strategy, sim_count) -> dict:
        """Compute per-interval metrics for convergence analysis."""
        accuracy = EvaluationHarness.compute_accuracy(strategy, OPTIMAL_STRATEGY)

        # State visit counts (regular states only)
        visit_counts = {}
        for player_value in range(4, 22):
            for dealer_upcard in range(2, 12):
                for has_usable_ace in [True, False]:
                    state = (player_value, dealer_upcard, has_usable_ace)
                    visit_counts[state] = self.state_visits.get(state, 0)

        # EV variance per (state, action)
        ev_variance = {}
        for key, (count, mean, m2) in self.ev_data.items():
            if count > 1:
                variance = m2 / count
                ev_variance[key] = math.sqrt(max(0, variance))
            else:
                ev_variance[key] = 0.0

        return {
            'simulations': sim_count,
            'strategy_accuracy': accuracy,
            'state_visit_counts': visit_counts,
            'ev_variance_per_state': ev_variance,
            'strategy': dict(strategy),
        }
