"""Dynamic programming algorithm for optimal blackjack strategy.

Exploits overlapping subproblem structure: many card sequences lead to the
same hand value, so we compute expected values per unique state once and
cache them. Uses the same infinite-deck mathematical model as brute force
but achieves polynomial time via memoization.
"""

from .base import BaseAlgorithm

# Infinite deck probabilities: 1/13 for each of 2-9 and Ace(11), 4/13 for 10
CARD_PROBS = [(v, 1 / 13) for v in range(2, 10)] + [(10, 4 / 13)] + [(11, 1 / 13)]


class DynamicProgrammingAlgorithm(BaseAlgorithm):
    """Compute optimal strategy using DP with memoization."""

    def __init__(self):
        self.states_explored = 0
        self._memo_best_ev = {}
        self._memo_dealer = {}

    @property
    def name(self) -> str:
        return "dynamic_programming"

    def compute_strategy(self) -> dict:
        """Compute strategy by memoized EV calculation for all states.

        Produces 360 regular states + 100 pair states = 460 total.
        Pair states use key ('pair', card_value, dealer_upcard).
        """
        self._memo_best_ev = {}
        self._memo_dealer = {}
        self.states_explored = 0

        # Step 1: Precompute dealer outcome distributions for each upcard
        print("Computing dealer outcome distributions...")
        dealer_probs = {}
        for upcard in range(2, 12):
            dealer_probs[upcard] = self._dealer_outcomes(upcard)
        print("Dealer distributions complete.")

        # Step 2: For each state, find the action with highest EV
        strategy = {}
        total_states = 18 * 10 * 2 + 10 * 10  # 360 regular + 100 pair
        for player_value in range(4, 22):
            print(f"  Player value {player_value}/21 "
                  f"({self.states_explored}/{total_states} states)...")
            for dealer_upcard in range(2, 12):
                for has_usable_ace in [True, False]:
                    if has_usable_ace and player_value < 12:
                        strategy[(player_value, dealer_upcard, has_usable_ace)] = 'hit'
                        self.states_explored += 1
                        continue

                    dealer_out = dealer_probs[dealer_upcard]
                    evs = {
                        'stand': self._stand_ev(player_value, dealer_out),
                        'hit': self._hit_ev(player_value, dealer_upcard, has_usable_ace, dealer_out),
                        'double': self._double_ev(player_value, has_usable_ace, dealer_out),
                    }
                    strategy[(player_value, dealer_upcard, has_usable_ace)] = max(evs, key=lambda k: evs[k])
                    self.states_explored += 1

        # Step 3: Compute pair split decisions
        for card_value in range(2, 12):  # 2-10, 11=Ace
            card_label = 'A' if card_value == 11 else str(card_value)
            print(f"  Pair {card_label}-{card_label} "
                  f"({self.states_explored}/{total_states} states)...")
            for dealer_upcard in range(2, 12):
                dealer_out = dealer_probs[dealer_upcard]
                if card_value == 11:
                    pair_value, pair_soft = 12, True
                else:
                    pair_value, pair_soft = card_value * 2, False

                no_split_ev = max(
                    self._stand_ev(pair_value, dealer_out),
                    self._hit_ev(pair_value, dealer_upcard, pair_soft, dealer_out),
                    self._double_ev(pair_value, pair_soft, dealer_out),
                )
                split_ev = self._split_ev(card_value, dealer_upcard, dealer_out)

                if split_ev > no_split_ev:
                    strategy[('pair', card_value, dealer_upcard)] = 'split'
                self.states_explored += 1

        print(f"DP complete. {self.states_explored} states explored. "
              f"Memo cache size: {len(self._memo_best_ev)} entries.")
        return strategy

    def _dealer_outcomes(self, upcard):
        """Compute dealer final-value probability distribution for a given upcard."""
        if upcard == 11:
            return self._dealer_recurse(11, True)
        return self._dealer_recurse(upcard, False)

    def _dealer_recurse(self, value, soft):
        """Recursively enumerate dealer card sequences with memoization."""
        key = (value, soft)
        if key in self._memo_dealer:
            return self._memo_dealer[key]

        if value > 21:
            result = {'bust': 1.0}
        elif value >= 17:
            result = {value: 1.0}
        else:
            result = {}
            for card_value, prob in CARD_PROBS:
                new_value, new_soft = self._add_card(value, soft, card_value)
                sub = self._dealer_recurse(new_value, new_soft)
                for outcome, sub_prob in sub.items():
                    result[outcome] = result.get(outcome, 0) + prob * sub_prob

        self._memo_dealer[key] = result
        return result

    @staticmethod
    def _stand_ev(player_value, dealer_outcomes):
        """EV of standing: compare player value against dealer distribution."""
        ev = 0.0
        for outcome, prob in dealer_outcomes.items():
            if outcome == 'bust':
                ev += prob
            elif player_value > outcome:
                ev += prob
            elif player_value < outcome:
                ev -= prob
        return ev

    def _hit_ev(self, player_value, dealer_upcard, soft, dealer_outcomes):
        """EV of hitting: branch over all cards, then play optimally (memoized)."""
        ev = 0.0
        for card_value, prob in CARD_PROBS:
            new_pv, new_soft = self._add_card(player_value, soft, card_value)
            if new_pv > 21:
                ev -= prob
            else:
                ev += prob * self._best_ev(new_pv, dealer_upcard, new_soft,
                                           dealer_outcomes, can_double=False)
        return ev

    def _double_ev(self, player_value, soft, dealer_outcomes):
        """EV of doubling: one card then auto-stand, double the stakes."""
        ev = 0.0
        for card_value, prob in CARD_PROBS:
            new_pv, new_soft = self._add_card(player_value, soft, card_value)
            if new_pv > 21:
                ev += prob * (-2)
            else:
                ev += prob * 2 * self._stand_ev(new_pv, dealer_outcomes)
        return ev

    def _split_ev(self, card_value, dealer_upcard, dealer_outcomes):
        """EV of splitting a pair.

        For aces: one card only, auto-stand (standard casino rule).
        For non-aces: play optimally, can double but no re-split.
        Returns total EV across both hands (each costs 1 unit).
        """
        if card_value == 11:  # Aces
            single_hand_ev = 0.0
            for next_card, prob in CARD_PROBS:
                new_pv, new_soft = self._add_card(11, True, next_card)
                single_hand_ev += prob * self._stand_ev(new_pv, dealer_outcomes)
            return 2 * single_hand_ev

        is_soft = False
        single_hand_ev = 0.0
        for next_card, prob in CARD_PROBS:
            new_pv, new_soft = self._add_card(card_value, is_soft, next_card)
            single_hand_ev += prob * self._best_ev(
                new_pv, dealer_upcard, new_soft, dealer_outcomes, can_double=True
            )
        return 2 * single_hand_ev

    def _best_ev(self, pv, dc, soft, dealer_outcomes, can_double=True):
        """Return the maximum EV across available actions (memoized)."""
        key = (pv, dc, soft, can_double)
        if key in self._memo_best_ev:
            return self._memo_best_ev[key]

        dealer_out = dealer_outcomes
        ev_stand = self._stand_ev(pv, dealer_out)
        ev_hit = self._hit_ev(pv, dc, soft, dealer_out)

        if can_double:
            ev_double = self._double_ev(pv, soft, dealer_out)
            result = max(ev_stand, ev_hit, ev_double)
        else:
            result = max(ev_stand, ev_hit)

        self._memo_best_ev[key] = result
        return result

    @staticmethod
    def _add_card(player_value, soft, card_value):
        """Add a card to hand, properly tracking usable ace status."""
        is_ace = card_value == 11
        new_value = player_value + (11 if is_ace else card_value)
        usable_aces = (1 if soft else 0) + (1 if is_ace else 0)

        while new_value > 21 and usable_aces > 0:
            new_value -= 10
            usable_aces -= 1

        return new_value, usable_aces > 0
