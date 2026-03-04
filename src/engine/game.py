from src.core.deck import Deck
from src.core.player import Hand, Player


class BlackjackGame:
    """Manages the state and rules for a single blackjack round."""

    def __init__(self, num_decks=6):
        self.deck = Deck(num_decks)
        self.player = None
        self.player_hand = None
        self.dealer_hand = Hand()
        self.game_over = False
        self.result = ""
        self.active_hand_index = 0

    def start_round(self, player, bet=10):
        """Deal initial cards for a new round."""
        self.player = player
        self.player.reset_hands()
        self.player.place_bet(bet)
        self.player_hand = player.hands[0]
        self.dealer_hand = Hand()
        self.active_hand_index = 0

        # Deal 2 cards each, alternating
        self.player_hand.add_card(self.deck.deal())
        self.dealer_hand.add_card(self.deck.deal())
        self.player_hand.add_card(self.deck.deal())
        self.dealer_hand.add_card(self.deck.deal())

        self.game_over = False
        self.result = ""

    @property
    def dealer_upcard(self):
        """Return the dealer's face-up card (first card dealt)."""
        if self.dealer_hand.cards:
            return self.dealer_hand.cards[0]
        return None

    def get_state(self):
        """Return game state tuple for algorithm state spaces.
        Returns: (player_value, dealer_upcard_value, has_usable_ace)
        """
        player_value = self.player_hand.get_value()
        dealer_upcard_value = self.dealer_upcard.value if self.dealer_upcard else 0
        has_usable_ace = self.player_hand.is_soft()
        return (player_value, dealer_upcard_value, has_usable_ace)

    def player_hit(self):
        """Player draws one card. Returns True if player busted."""
        self.player_hand.add_card(self.deck.deal())
        if self.player_hand.busted:
            if self.active_hand_index < len(self.player.hands) - 1:
                self._advance_hand()
            else:
                self.game_over = True
                self.result = self._determine_winner()
            return True
        return False

    def player_stand(self):
        """Player stands on current hand."""
        self.player_hand.stood = True
        if self.active_hand_index < len(self.player.hands) - 1:
            self._advance_hand()
        else:
            self._dealer_play()
            self.game_over = True
            self.result = self._determine_winner()

    def player_double(self):
        """Player doubles down: double bet, one card, auto-stand.
        Returns True if player busted."""
        self.player.chips -= self.player_hand.bet
        self.player_hand.bet *= 2
        self.player.current_bet *= 2
        self.player_hand.doubled = True

        self.player_hand.add_card(self.deck.deal())
        self.player_hand.stood = True

        if self.player_hand.busted:
            if self.active_hand_index < len(self.player.hands) - 1:
                self._advance_hand()
            else:
                self.game_over = True
                self.result = self._determine_winner()
            return True

        if self.active_hand_index < len(self.player.hands) - 1:
            self._advance_hand()
        else:
            self._dealer_play()
            self.game_over = True
            self.result = self._determine_winner()
        return False

    def player_split(self):
        """Split current hand into two hands."""
        hand = self.player_hand
        if not hand.can_split():
            raise ValueError("Cannot split: hand does not have two cards of the same rank")

        second_hand = Hand()
        second_card = hand.cards.pop()
        # Reset bust flag since we removed a card
        hand.busted = False

        second_hand.cards.append(second_card)
        second_hand.bet = hand.bet
        self.player.chips -= hand.bet

        hand.add_card(self.deck.deal())
        second_hand.add_card(self.deck.deal())

        self.player.hands.append(second_hand)

    def execute_action(self, action):
        """Execute a player action and return the resulting game state.

        Args:
            action: One of 'hit', 'stand', 'double', 'split'

        Returns:
            dict with state, done, result, player_busted
        """
        if action == 'hit':
            busted = self.player_hit()
        elif action == 'stand':
            self.player_stand()
            busted = False
        elif action == 'double':
            busted = self.player_double()
        elif action == 'split':
            self.player_split()
            busted = False
        else:
            raise ValueError(f"Unknown action: {action}. Valid actions: hit, stand, double, split")

        return {
            'state': self.get_state(),
            'done': self.game_over,
            'result': self.result,
            'player_busted': busted,
        }

    def _advance_hand(self):
        """Move to the next split hand."""
        self.active_hand_index += 1
        if self.active_hand_index < len(self.player.hands):
            self.player_hand = self.player.hands[self.active_hand_index]
        else:
            self._dealer_play()
            self.game_over = True
            self.result = self._determine_winner()

    def _dealer_play(self):
        """Dealer hits while hand value < 17."""
        while self.dealer_hand.get_value() < 17:
            self.dealer_hand.add_card(self.deck.deal())

    def _determine_winner(self):
        """Check winner for each player hand and settle bets."""
        dealer_value = self.dealer_hand.get_value()
        results = []

        for i, hand in enumerate(self.player.hands):
            player_value = hand.get_value()
            hand_label = f"Hand {i+1}: " if len(self.player.hands) > 1 else ""

            if hand.busted:
                self.player.lose_hand(hand)
                results.append(f"{hand_label}Dealer wins! Player busts.")
            elif self.dealer_hand.busted:
                self.player.win_hand(hand)
                results.append(f"{hand_label}Player wins! Dealer busts.")
            elif hand.is_blackjack() and len(self.player.hands) == 1 and not self.dealer_hand.is_blackjack():
                self.player.win_hand(hand, multiplier=2.5)
                results.append(f"{hand_label}Blackjack! Player wins!")
            elif player_value > dealer_value:
                self.player.win_hand(hand)
                results.append(f"{hand_label}Player wins!")
            elif dealer_value > player_value:
                self.player.lose_hand(hand)
                results.append(f"{hand_label}Dealer wins!")
            else:
                self.player.push_hand(hand)
                results.append(f"{hand_label}It's a tie! Push.")

        self.player.current_bet = 0
        return " | ".join(results)

    @property
    def needs_new_deck(self):
        """Check if deck is running low."""
        return self.deck.remaining < 10
