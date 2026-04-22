"""Export strategy dictionaries to CSV for visualization."""

import csv


STRATEGY_CSV_FIELDS = [
    'algorithm', 'player_value', 'dealer_upcard', 'is_soft', 'is_pair', 'action',
]


def export_strategies_csv(path, strategies):
    """Write one or more strategy dicts to a CSV file.

    Args:
        path: output file path
        strategies: dict mapping algorithm name -> strategy dict
    """
    with open(path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=STRATEGY_CSV_FIELDS)
        writer.writeheader()

        for algo_name, strategy in strategies.items():
            for key, action in sorted(strategy.items(), key=_sort_key):
                if key[0] == 'pair':
                    # ('pair', card_value, dealer_upcard)
                    row = {
                        'algorithm': algo_name,
                        'player_value': key[1],
                        'dealer_upcard': key[2],
                        'is_soft': False,
                        'is_pair': True,
                        'action': action,
                    }
                else:
                    # (player_value, dealer_upcard, has_usable_ace)
                    row = {
                        'algorithm': algo_name,
                        'player_value': key[0],
                        'dealer_upcard': key[1],
                        'is_soft': key[2],
                        'is_pair': False,
                        'action': action,
                    }
                writer.writerow(row)


def _sort_key(item):
    """Sort strategy entries: regular states first, then pairs."""
    key = item[0]
    if key[0] == 'pair':
        return (1, key[1], key[2])
    return (0, key[0], key[1], int(key[2]))
