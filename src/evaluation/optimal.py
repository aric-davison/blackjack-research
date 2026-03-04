"""Published 6-deck basic strategy (dealer stands on soft 17).

The strategy is represented as a dict mapping:
    (player_value, dealer_upcard, has_usable_ace) -> action

where action is one of 'hit', 'stand', 'double', 'split'.

Dealer upcard values: 2-11 (11 = Ace)
Player values: 4-21
has_usable_ace: True (soft hand) or False (hard hand)

Total: 360 entries (18 player values x 10 dealer upcards x 2 soft/hard)
"""


def _build_optimal_strategy():
    strategy = {}

    # --- Hard hands (has_usable_ace = False) ---
    for player_value in range(4, 22):
        for dealer_upcard in range(2, 12):
            if player_value <= 8:
                action = 'hit'
            elif player_value == 9:
                if 3 <= dealer_upcard <= 6:
                    action = 'double'
                else:
                    action = 'hit'
            elif player_value == 10:
                if 2 <= dealer_upcard <= 9:
                    action = 'double'
                else:
                    action = 'hit'
            elif player_value == 11:
                if 2 <= dealer_upcard <= 10:
                    action = 'double'
                else:
                    action = 'hit'
            elif player_value == 12:
                if 4 <= dealer_upcard <= 6:
                    action = 'stand'
                else:
                    action = 'hit'
            elif 13 <= player_value <= 16:
                if 2 <= dealer_upcard <= 6:
                    action = 'stand'
                else:
                    action = 'hit'
            else:  # 17-21
                action = 'stand'
            strategy[(player_value, dealer_upcard, False)] = action

    # --- Soft hands (has_usable_ace = True) ---
    for player_value in range(4, 22):
        for dealer_upcard in range(2, 12):
            # Soft hands only meaningfully exist for values 12-21
            # (ace counting as 11 means minimum soft hand is A+A = 12)
            # For impossible soft states (4-11), fill with 'hit'
            if player_value <= 11:
                action = 'hit'
            elif player_value in (13, 14):
                # Soft 13-14: double vs 5-6, else hit
                if 5 <= dealer_upcard <= 6:
                    action = 'double'
                else:
                    action = 'hit'
            elif player_value in (15, 16):
                # Soft 15-16: double vs 4-6, else hit
                if 4 <= dealer_upcard <= 6:
                    action = 'double'
                else:
                    action = 'hit'
            elif player_value == 17:
                # Soft 17: double vs 3-6, else hit
                if 3 <= dealer_upcard <= 6:
                    action = 'double'
                else:
                    action = 'hit'
            elif player_value == 18:
                # Soft 18: double vs 3-6, stand vs 2,7,8, hit vs 9-11
                if 3 <= dealer_upcard <= 6:
                    action = 'double'
                elif dealer_upcard in (2, 7, 8):
                    action = 'stand'
                else:
                    action = 'hit'
            elif player_value == 19:
                action = 'stand'
            elif player_value == 20:
                action = 'stand'
            elif player_value == 21:
                action = 'stand'
            else:
                # Soft 12 (pair of aces) - hit
                action = 'hit'
            strategy[(player_value, dealer_upcard, True)] = action

    return strategy


OPTIMAL_STRATEGY = _build_optimal_strategy()
