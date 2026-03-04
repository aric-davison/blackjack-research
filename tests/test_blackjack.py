import pytest
from src.core.deck import Card
from src.core.player import Player
from src.engine.game import BlackjackGame


def test_start_round_deals_four_cards():
    game = BlackjackGame()
    player = Player("Test")
    game.start_round(player)
    assert len(game.player_hand.cards) == 2
    assert len(game.dealer_hand.cards) == 2


def test_player_hit_adds_card():
    game = BlackjackGame()
    player = Player("Test")
    game.start_round(player)
    game.player_hit()
    assert len(game.player_hand.cards) == 3


def test_player_stand_triggers_dealer():
    game = BlackjackGame()
    player = Player("Test")
    game.start_round(player)
    game.player_stand()
    assert game.game_over
    assert game.dealer_hand.get_value() >= 17 or game.dealer_hand.busted


def test_game_result_not_empty_after_stand():
    game = BlackjackGame()
    player = Player("Test")
    game.start_round(player)
    game.player_stand()
    assert game.result != ""


def test_chips_change_after_round():
    game = BlackjackGame()
    player = Player("Test", starting_chips=1000)
    game.start_round(player, bet=100)
    assert player.chips == 900  # bet deducted
    game.player_stand()
    # Chips should have changed (win, lose, or push)
    assert player.current_bet == 0


def test_needs_new_deck():
    game = BlackjackGame(num_decks=1)
    # Deal down to exactly 10 remaining
    for _ in range(42):
        game.deck.deal()
    assert not game.needs_new_deck  # 10 remaining
    game.deck.deal()
    assert game.needs_new_deck  # 9 remaining (< 10)


# --- Dealer upcard ---

def test_dealer_upcard():
    game = BlackjackGame()
    player = Player("Test")
    game.start_round(player)
    assert game.dealer_upcard == game.dealer_hand.cards[0]


def test_dealer_upcard_before_deal():
    game = BlackjackGame()
    # Fresh game, dealer_hand has no cards from __init__
    game.dealer_hand.cards.clear()
    assert game.dealer_upcard is None


# --- Game state ---

def test_get_state_returns_tuple():
    game = BlackjackGame()
    player = Player("Test")
    game.start_round(player)
    state = game.get_state()
    assert isinstance(state, tuple)
    assert len(state) == 3


def test_get_state_values():
    game = BlackjackGame()
    player = Player("Test")
    game.start_round(player)
    player_val, dealer_val, is_soft = game.get_state()
    assert player_val == game.player_hand.get_value()
    assert dealer_val == game.dealer_upcard.value
    assert is_soft == game.player_hand.is_soft()


# --- Double down ---

def test_player_double_adds_one_card():
    game = BlackjackGame()
    player = Player("Test", starting_chips=1000)
    game.start_round(player, bet=100)
    game.player_double()
    assert len(game.player_hand.cards) == 3
    assert game.player_hand.doubled is True
    assert game.player_hand.stood is True


def test_player_double_doubles_bet():
    game = BlackjackGame()
    player = Player("Test", starting_chips=1000)
    game.start_round(player, bet=100)
    # After start_round: chips=900
    game.player_double()
    # After double: chips=800 (additional 100 deducted), game settles
    assert player.chips != 900  # chips changed from double + settlement
    assert game.game_over is True


# --- Split ---

def test_player_split_creates_two_hands():
    game = BlackjackGame()
    player = Player("Test", starting_chips=1000)
    game.start_round(player, bet=100)
    # Force a splittable hand
    game.player_hand.cards = [Card('8', 'Hearts', 8), Card('8', 'Spades', 8)]
    game.player_hand.busted = False
    game.player_split()
    assert len(player.hands) == 2
    assert len(player.hands[0].cards) == 2
    assert len(player.hands[1].cards) == 2


def test_player_split_deducts_additional_bet():
    game = BlackjackGame()
    player = Player("Test", starting_chips=1000)
    game.start_round(player, bet=100)
    # chips = 900 after bet
    game.player_hand.cards = [Card('8', 'Hearts', 8), Card('8', 'Spades', 8)]
    game.player_hand.busted = False
    game.player_split()
    assert player.chips == 800  # 900 - 100 additional bet


# --- execute_action ---

def test_execute_action_hit():
    game = BlackjackGame()
    player = Player("Test")
    game.start_round(player)
    result = game.execute_action('hit')
    assert 'state' in result
    assert 'done' in result
    assert 'result' in result
    assert 'player_busted' in result
    assert len(game.player_hand.cards) == 3


def test_execute_action_invalid():
    game = BlackjackGame()
    player = Player("Test")
    game.start_round(player)
    with pytest.raises(ValueError):
        game.execute_action('fold')
