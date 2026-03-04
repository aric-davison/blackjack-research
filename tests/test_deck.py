import pytest
from src.core.deck import Card, Deck, SUIT_SYMBOLS


def test_card_creation():
    card = Card('A', 'Spades', 11)
    assert card.rank == 'A'
    assert card.suit == 'Spades'
    assert card.value == 11


def test_card_suit_symbol():
    card = Card('K', 'Hearts', 10)
    assert card.suit_symbol == '♥'


def test_suit_symbols_complete():
    for suit in ['Hearts', 'Diamonds', 'Clubs', 'Spades']:
        assert suit in SUIT_SYMBOLS


def test_deck_creation():
    deck = Deck()
    assert len(deck.cards) == 52


def test_deck_remaining():
    deck = Deck()
    assert deck.remaining == 52


def test_deck_cards_are_card_objects():
    deck = Deck()
    card = deck.deal()
    assert isinstance(card, Card)
    assert hasattr(card, 'rank')
    assert hasattr(card, 'suit')
    assert hasattr(card, 'value')


def test_deck_deal_reduces_count():
    deck = Deck()
    deck.deal()
    assert deck.remaining == 51


def test_multi_deck():
    deck = Deck(num_of_decks=6)
    assert deck.remaining == 312


def test_deck_deal_card_alias():
    deck = Deck()
    card = deck.deal_card()
    assert isinstance(card, Card)
    assert deck.remaining == 51


def test_deck_reset_restores_count():
    deck = Deck()
    deck.deal()
    deck.deal()
    assert deck.remaining == 50
    deck.reset()
    assert deck.remaining == 52


def test_deck_reset_multi_deck():
    deck = Deck(num_of_decks=6)
    for _ in range(100):
        deck.deal()
    assert deck.remaining == 212
    deck.reset()
    assert deck.remaining == 312
