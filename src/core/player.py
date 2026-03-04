from .deck import Card


class Hand:
    def __init__(self):
        self.cards = []
        self.stood = False
        self.busted = False
        self.doubled = False
        self.bet = 0

    def add_card(self, card):
        self.cards.append(card)
        if self.get_value() > 21:
            self.busted = True

    def get_value(self):
        value = 0
        aces = 0
        for card in self.cards:
            if card.rank == 'A':
                aces += 1
                value += 11
            else:
                value += card.value
        while value > 21 and aces:
            value -= 10
            aces -= 1
        return value

    def is_blackjack(self):
        return len(self.cards) == 2 and self.get_value() == 21

    def can_split(self):
        """Return True if hand has exactly 2 cards of the same rank."""
        return len(self.cards) == 2 and self.cards[0].rank == self.cards[1].rank

    def is_soft(self):
        """Return True if the hand has an ace counting as 11."""
        value = 0
        aces = 0
        for card in self.cards:
            if card.rank == 'A':
                aces += 1
                value += 11
            else:
                value += card.value
        reduced = 0
        while value > 21 and reduced < aces:
            value -= 10
            reduced += 1
        return reduced < aces


class Player:
    def __init__(self, name, starting_chips=1000):
        self.name = name
        self.chips = starting_chips
        self.current_bet = 0
        self.hands = [Hand()]  # list for future split support
        self.is_sitting = True

    def place_bet(self, amount):
        self.chips -= amount
        self.current_bet = amount
        if self.hands:
            self.hands[0].bet = amount

    def win(self, multiplier=2):
        self.chips += self.current_bet * multiplier
        self.current_bet = 0

    def lose(self):
        self.current_bet = 0

    def push(self):
        self.chips += self.current_bet
        self.current_bet = 0

    def win_hand(self, hand, multiplier=2):
        """Settle a winning hand using the hand's own bet."""
        self.chips += hand.bet * multiplier
        hand.bet = 0

    def lose_hand(self, hand):
        """Settle a losing hand (chips already deducted)."""
        hand.bet = 0

    def push_hand(self, hand):
        """Return the hand's bet to the player."""
        self.chips += hand.bet
        hand.bet = 0

    def reset_hands(self):
        self.hands = [Hand()]
        self.current_bet = 0