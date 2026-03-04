import random
from dataclasses import dataclass

SUIT_SYMBOLS = {
    "Hearts": "♥",
    "Diamonds": "♦",
    "Clubs": "♣",
    "Spades": "♠",
}


@dataclass
class Card:
    rank: str
    suit: str
    value: int

    @property
    def suit_symbol(self) -> str:
        return SUIT_SYMBOLS[self.suit]


class Deck:
    def __init__(self, num_of_decks=1):
        self.num_of_decks = num_of_decks
        self.cards = self._create_deck(num_of_decks)
        self.shuffle()

    def _create_deck(self, num_of_decks=1):
        suits = ['Hearts', 'Diamonds', 'Clubs', 'Spades']
        ranks = {
            '2': 2, '3': 3, '4': 4, '5': 5, '6': 6,
            '7': 7, '8': 8, '9': 9, '10': 10,
            'J': 10, 'Q': 10, 'K': 10, 'A': 11
        }
        single = [Card(rank, suit, value) for suit in suits for rank, value in ranks.items()]
        return single * num_of_decks

    def shuffle(self):
        random.shuffle(self.cards)

    def deal(self):
        return self.cards.pop()

    def deal_card(self):
        return self.deal()

    def reset(self):
        """Recreate and reshuffle the deck."""
        self.cards = self._create_deck(self.num_of_decks)
        self.shuffle()

    @property
    def remaining(self) -> int:
        return len(self.cards)
