"""Brute-force enumeration algorithm for optimal blackjack strategy.

Recursively enumerates every possible action sequence and card draw to compute
exact expected values. No memoization — redundant subproblems are recomputed,
demonstrating exponential complexity. Uses infinite-deck card probabilities
(mathematical model, not the game engine).
"""

from .base import BaseAlgorithm

# Infinite deck probabilities: 1/13 for each of 2-9 and Ace(11), 4/13 for 10
CARD_PROBS = [(v, 1 / 13) for v in range(2, 10)] + [(10, 4 / 13)] + [(11, 1 / 13)]


class BruteForceAlgorithm(BaseAlgorithm):
    """Compute optimal strategy by exhaustive enumeration of all outcomes."""

    def __init__(self):
        self.states_explored = 0

    @property
    def name(self) -> str:
        return "brute_force"

    def compute_strategy(self) -> dict:
        """Compute strategy by brute-force EV calculation for all states.

        Produces 360 regular states + 100 pair states = 460 total.
        Pair states use key ('pair', card_value, dealer_upcard).
        """
        # Step 1: Compute dealer outcome distributions for each upcard
        print("Computing dealer outcome distributions...")
        dealer_probs = {}
        for upcard in range(2, 12):
            dealer_probs[upcard] = self._dealer_outcomes(upcard)
        print("Dealer distributions complete.")

        # Step 2: For each state, find the action with highest EV
        strategy = {}
        self.states_explored = 0
        total_states = 18 * 10 * 2 + 10 * 10  # 360 regular + 100 pair
        for player_value in range(4, 22):
            print(f"  Player value {player_value}/21 "
                  f"({self.states_explored}/{total_states} states)...")
            for dealer_upcard in range(2, 12):
                for has_usable_ace in [True, False]:
                    # Soft hands below 12 are impossible in blackjack
                    # (minimum soft hand is A+A = 12). Fill with 'hit'.
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
                # Hand value and softness for this pair played without splitting
                if card_value == 11:
                    pair_value, pair_soft = 12, True  # A+A = soft 12
                else:
                    pair_value, pair_soft = card_value * 2, False

                # Best EV without splitting (already computed in regular strategy)
                no_split_ev = max(
                    self._stand_ev(pair_value, dealer_out),
                    self._hit_ev(pair_value, dealer_upcard, pair_soft, dealer_out),
                    self._double_ev(pair_value, pair_soft, dealer_out),
                )
                split_ev = self._split_ev(card_value, dealer_upcard, dealer_out)

                if split_ev > no_split_ev:
                    strategy[('pair', card_value, dealer_upcard)] = 'split'
                self.states_explored += 1

        print(f"Brute-force complete. {self.states_explored} states explored.")
        return strategy

    def _dealer_outcomes(self, upcard):
        """Compute dealer final-value probability distribution for a given upcard.

        Returns dict mapping final values (17-21 and 'bust') to probabilities.
        """
        if upcard == 11:
            return self._dealer_recurse(11, True)
        return self._dealer_recurse(upcard, False)

    def _dealer_recurse(self, value, soft):
        """Recursively enumerate all dealer card sequences."""
        if value > 21:
            return {'bust': 1.0}
        if value >= 17:
            return {value: 1.0}

        outcomes = {}
        for card_value, prob in CARD_PROBS:
            new_value, new_soft = self._add_card(value, soft, card_value)
            sub = self._dealer_recurse(new_value, new_soft)
            for outcome, sub_prob in sub.items():
                outcomes[outcome] = outcomes.get(outcome, 0) + prob * sub_prob
        return outcomes

    @staticmethod
    def _stand_ev(player_value, dealer_outcomes):
        """EV of standing: compare player value against dealer distribution."""
        ev = 0.0
        for outcome, prob in dealer_outcomes.items():
            if outcome == 'bust':
                ev += prob  # player wins
            elif player_value > outcome:
                ev += prob
            elif player_value < outcome:
                ev -= prob
            # push: +0
        return ev

    def _hit_ev(self, player_value, dealer_upcard, soft, dealer_outcomes):
        """EV of hitting: branch over all cards, then play optimally (no memo)."""
        ev = 0.0
        for card_value, prob in CARD_PROBS:
            new_pv, new_soft = self._add_card(player_value, soft, card_value)
            if new_pv > 21:
                ev -= prob  # bust
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
                ev += prob * (-2)  # bust, lose double bet
            else:
                ev += prob * 2 * self._stand_ev(new_pv, dealer_outcomes)
        return ev

    def _split_ev(self, card_value, dealer_upcard, dealer_outcomes):
        """EV of splitting a pair. Each split hand starts with one card, draws another.

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
        """Return the maximum EV across available actions (no memoization)."""
        ev_stand = self._stand_ev(pv, dealer_outcomes)
        ev_hit = self._hit_ev(pv, dc, soft, dealer_outcomes)

        if can_double:
            ev_double = self._double_ev(pv, soft, dealer_outcomes)
            return max(ev_stand, ev_hit, ev_double)
        return max(ev_stand, ev_hit)

    @staticmethod
    def _add_card(player_value, soft, card_value):
        """Add a card to hand, properly tracking usable ace status.

        Handles edge cases like soft hand + ace draw correctly by tracking
        the count of usable aces (max 1 in practice after reduction).
        """
        is_ace = card_value == 11
        new_value = player_value + (11 if is_ace else card_value)
        usable_aces = (1 if soft else 0) + (1 if is_ace else 0)

        while new_value > 21 and usable_aces > 0:
            new_value -= 10
            usable_aces -= 1

        return new_value, usable_aces > 0
