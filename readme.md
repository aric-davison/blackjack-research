# Blackjack Research

Course project for CPT S 350 (Design & Analysis of Algorithms) comparing different algorithm approaches to computing optimal blackjack strategy.

## Algorithms

- **Brute force** — recursive enumeration of all states
- **Dynamic programming** — memoized EV computation
- **Greedy** — rule-based heuristic
- **Monte Carlo** — exploring-starts simulation with a convergence schedule

Each is evaluated on compute cost, strategy accuracy vs. published optimal strategy, and simulated win rate.

## Setup

```bash
conda env create -f environment.yml
conda activate bjresearch
```

## Usage

```bash
# Run the full simulation comparing all algorithms (1M hands each)
python run_simulation.py

# Run batched simulations for averaged results
python run_batch_simulation.py

# Run the Monte Carlo experiment
python run_mc_simulation.py

# Run tests
pytest
```

## Layout

- `src/core/` — game primitives (cards, deck, hand, player)
- `src/engine/` — round orchestration and dealer logic
- `src/algorithms/` — strategy computation
- `src/evaluation/` — simulation harness and optimal-strategy baseline
- `tests/` — pytest suite
- `docs/` — algorithm write-ups
