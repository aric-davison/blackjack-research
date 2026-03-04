import pytest
from src.core.deck import Card
from src.core.player import Hand, Player


def test_hand_add_card():
    hand = Hand()
    hand.add_card(Card('5', 'Hearts', 5))
    assert len(hand.cards) == 1
    assert hand.get_value() == 5


def test_hand_ace_adjustment():
    hand = Hand()
    hand.add_card(Card('A', 'Spades', 11))
    hand.add_card(Card('K', 'Hearts', 10))
    assert hand.get_value() == 21
    hand.add_card(Card('5', 'Clubs', 5))
    assert hand.get_value() == 16  # Ace counts as 1


def test_hand_is_blackjack():
    hand = Hand()
    hand.add_card(Card('A', 'Spades', 11))
    hand.add_card(Card('K', 'Hearts', 10))
    assert hand.is_blackjack()


def test_hand_not_blackjack_three_cards():
    hand = Hand()
    hand.add_card(Card('7', 'Spades', 7))
    hand.add_card(Card('7', 'Hearts', 7))
    hand.add_card(Card('7', 'Clubs', 7))
    assert not hand.is_blackjack()


def test_hand_is_soft():
    hand = Hand()
    hand.add_card(Card('A', 'Spades', 11))
    hand.add_card(Card('6', 'Hearts', 6))
    assert hand.is_soft()  # Soft 17


def test_hand_not_soft():
    hand = Hand()
    hand.add_card(Card('K', 'Spades', 10))
    hand.add_card(Card('7', 'Hearts', 7))
    assert not hand.is_soft()  # Hard 17


def test_hand_bust_flag():
    hand = Hand()
    hand.add_card(Card('K', 'Spades', 10))
    hand.add_card(Card('Q', 'Hearts', 10))
    hand.add_card(Card('5', 'Clubs', 5))
    assert hand.busted


def test_player_place_bet():
    player = Player("Test", starting_chips=1000)
    player.place_bet(100)
    assert player.chips == 900
    assert player.current_bet == 100


def test_player_win():
    player = Player("Test", starting_chips=1000)
    player.place_bet(100)
    player.win()  # default 2x multiplier
    assert player.chips == 1100  # 900 + 200


def test_player_lose():
    player = Player("Test", starting_chips=1000)
    player.place_bet(100)
    player.lose()
    assert player.chips == 900


def test_player_push():
    player = Player("Test", starting_chips=1000)
    player.place_bet(100)
    player.push()
    assert player.chips == 1000  # bet returned


def test_player_reset_hands():
    player = Player("Test")
    player.place_bet(50)
    player.hands[0].add_card(Card('K', 'Hearts', 10))
    player.reset_hands()
    assert len(player.hands) == 1
    assert len(player.hands[0].cards) == 0
    assert player.current_bet == 0


def test_hand_doubled_flag_default():
    hand = Hand()
    assert hand.doubled is False


def test_hand_can_split_same_rank():
    hand = Hand()
    hand.add_card(Card('8', 'Hearts', 8))
    hand.add_card(Card('8', 'Spades', 8))
    assert hand.can_split()


def test_hand_can_split_different_rank():
    hand = Hand()
    hand.add_card(Card('8', 'Hearts', 8))
    hand.add_card(Card('9', 'Spades', 9))
    assert not hand.can_split()


def test_hand_cannot_split_three_cards():
    hand = Hand()
    hand.add_card(Card('8', 'Hearts', 8))
    hand.add_card(Card('8', 'Spades', 8))
    hand.add_card(Card('8', 'Clubs', 8))
    assert not hand.can_split()
