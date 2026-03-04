# Algorithm Design & Data Collection

## Overview

This project implements four algorithmic approaches to derive an optimal blackjack
strategy, then compares them on both **strategy quality** and **computational cost**.
Each algorithm takes the same input — the blackjack state space — and produces a
strategy table mapping every game state to a recommended action (hit, stand, double,
split). The outputs are evaluated against the known mathematically optimal basic
strategy (Baldwin et al., 1956) and against each other.

### Game State Representation

Every algorithm operates on the same state tuple:

```
(player_hand_value, dealer_upcard_value, has_usable_ace)
```

- **player_hand_value**: 4–21 (hard hands), soft totals when ace counts as 11
- **dealer_upcard_value**: 2–11 (2–10 + Ace as 11)
- **has_usable_ace**: True/False (whether the hand has an ace counting as 11)

This produces roughly 300–400 unique states. Each algorithm maps every state to an
action: `hit`, `stand`, `double`, or `split`.

---

## Algorithm Descriptions

### 1. Brute-Force Enumeration

**Approach:** For each game state, recursively enumerate every possible sequence of
actions and every possible card draw. Compute the exact expected value of each action
by exhaustively exploring all outcomes.

**How it works:**
- For a given state, try each possible action (hit, stand, double)
- For "hit," branch over every possible next card (weighted by probability)
- Recurse until the hand is resolved (bust, stand, or 21)
- Compute the dealer's outcome distribution for each branch
- Sum weighted outcomes to get the exact expected value per action
- Select the action with the highest expected value

**What makes it different:** This is the only algorithm that guarantees an exact
solution by evaluating every possible path. It serves as the correctness baseline.
The tradeoff is exponential time complexity — the branching factor grows with each
hit decision, and every card remaining in the deck creates a new branch.

**Expected complexity:** Exponential in the depth of the decision tree. For a single
state, the number of paths can be very large, but the bounded hand values (bust at
22+) limit depth in practice.

---

### 2. Dynamic Programming with Memoization

**Approach:** Exploit the overlapping subproblem structure of blackjack. Many
different card sequences lead to the same hand value, so we compute the expected
value for each unique state once and cache it.

**How it works:**
- Precompute the dealer's outcome probability distribution for each possible upcard
  (dealer stands on 17+, so this is a fixed computation)
- For each player state, compute the expected value of standing (compare against
  dealer outcome distribution) and hitting (weighted sum over all possible next cards,
  recursing into the resulting state)
- Memoize results keyed by `(player_value, dealer_upcard, has_usable_ace)`
- Build the optimal strategy table by selecting the max-EV action per state

**What makes it different:** DP collapses the exponential brute-force tree into a
polynomial computation by recognizing that two hands with the same value, same dealer
upcard, and same soft/hard status are strategically identical regardless of which
specific cards produced them. This is the key insight — card composition doesn't
matter for basic strategy, only the total value.

**Expected complexity:** O(S x A x C) where S = number of states (~300-400),
A = number of actions, C = number of possible next cards (13 distinct values).
Effectively polynomial and fast.

---

### 3. Monte Carlo Simulation

**Approach:** Estimate expected values by simulating a large number of random
blackjack hands and observing outcomes. No explicit model of transition probabilities
is needed — the algorithm learns from experience.

**How it works:**
- For each simulation round, deal a random hand and observe the state
- Choose an action (exploring all actions across many simulations)
- Play the hand to completion using the game engine
- Record the outcome (win/loss/push) for the (state, action) pair
- After all simulations, compute the average return for each (state, action)
- Select the action with the highest average return per state

**Simulation intervals for convergence analysis:**

| Run | Hands Simulated |
|-----|----------------|
| 1   | 10,000         |
| 2   | 100,000        |
| 3   | 500,000        |
| 4   | 1,000,000      |
| 5   | 5,000,000      |
| 6   | 10,000,000     |

Each interval produces a full strategy table. Comparing tables across intervals
reveals how quickly Monte Carlo converges to the optimal strategy and where
diminishing returns set in.

**What makes it different:** Monte Carlo is the only algorithm that does not require
explicit knowledge of the game's transition probabilities. It discovers the strategy
empirically through random sampling. This makes it applicable to problems where the
rules are unknown or too complex to model analytically. The tradeoff is that results
are probabilistic — they converge to the true expected values but never reach them
exactly. Variance decreases with more simulations.

**Expected complexity:** O(N) where N = number of simulated hands. Linear in
simulation count, but convergence rate depends on how evenly states are visited.

---

### 4. Greedy Heuristic

**Approach:** Apply simple, fixed rules based on hand value thresholds. No
computation of expected values or simulation — just hardcoded decision logic.

**How it works:**
- Stand on 17 or higher
- Hit on 11 or below
- For 12–16, hit (simple aggressive variant) or stand (simple conservative variant)
- Never double or split (basic version), or double on 10-11 only (enhanced version)

**What makes it different:** This is the only algorithm that requires zero
computation. There is no learning, no recursion, no simulation. The strategy is
defined entirely by human intuition about "good enough" thresholds. It serves as the
lower bound on strategy quality — any algorithm that can't beat the greedy heuristic
is not worth its computational cost. It also demonstrates what you lose by ignoring
the full problem structure (dealer upcard, soft/hard distinction, exact probabilities).

**Expected complexity:** O(1) per decision. No precomputation needed.

---

## What We Are Measuring

### Performance Metrics (Computational Cost)

These measure how expensive each algorithm is to run:

| Metric | How Measured | Why It Matters |
|--------|-------------|----------------|
| **Wall-clock runtime** | `time.perf_counter()` before/after execution | Direct measure of how long you wait for results |
| **Peak memory usage** | `tracemalloc.get_traced_memory()` | Shows space complexity — DP caches states, brute-force builds deep call stacks |
| **States explored** | Counter incremented each time a new state is evaluated | Shows how much work the algorithm actually does vs. the theoretical state space |

### Quality Metrics (Strategy Effectiveness)

These measure how good the resulting strategy is:

| Metric | How Measured | Why It Matters |
|--------|-------------|----------------|
| **Strategy accuracy** | % of states where algorithm's action matches the published optimal basic strategy | Direct correctness measure — did the algorithm find the right answer? |
| **Win rate** | Wins / total hands over 1,000,000 simulated hands using the strategy | Practical outcome measure |
| **Average return per hand** | Total profit / total hands over 1,000,000 hands | Expected value measure — captures pushes and blackjack bonuses, not just win/loss |
| **House edge** | -(average return per hand) as a percentage of bet | Standard casino metric; optimal basic strategy yields ~0.5% house edge |

### Monte Carlo Convergence Data (Unique to MC)

Monte Carlo has an additional data collection layer that the other algorithms don't
need:

| Metric | How Measured | Why It Matters |
|--------|-------------|----------------|
| **Strategy accuracy at each interval** | Compare MC strategy table at 10K, 100K, ..., 10M against optimal | Shows convergence rate — how many simulations until MC matches optimal? |
| **Per-state visit count** | Count how many times each state was sampled | Reveals coverage gaps — rare states may have unreliable estimates |
| **EV estimate variance** | Standard deviation of returns per (state, action) | Shows confidence in the estimate — high variance = unreliable |

---

## Data Collected Per Algorithm

Each algorithm run produces the following output data:

### Strategy Table
A complete mapping of every game state to a recommended action:
```
(player_value, dealer_upcard, has_usable_ace) -> action
```
Stored as a dictionary or 2D grid. This is the primary output.

### Performance Record
```
{
    "algorithm": str,           # "brute_force", "dp", "monte_carlo", "greedy"
    "runtime_seconds": float,   # wall-clock time
    "peak_memory_bytes": int,   # from tracemalloc
    "states_explored": int,     # unique states evaluated
}
```

### Evaluation Record (from 1M-hand simulation using the strategy)
```
{
    "algorithm": str,
    "hands_played": int,        # 1,000,000
    "wins": int,
    "losses": int,
    "pushes": int,
    "blackjacks": int,
    "win_rate": float,          # wins / hands_played
    "average_return": float,    # total profit / hands_played
    "house_edge": float,        # -(average_return) as percentage
    "strategy_accuracy": float, # % agreement with optimal basic strategy
}
```

### Monte Carlo Additional Data (per interval)
```
{
    "simulations": int,             # 10K, 100K, 500K, 1M, 5M, 10M
    "strategy_accuracy": float,     # at this simulation count
    "state_visit_counts": dict,     # {state: count}
    "ev_variance_per_state": dict,  # {(state, action): std_dev}
}
```

---

## Key Differences in Processing

| Aspect | Brute-Force | DP | Monte Carlo | Greedy |
|--------|------------|-----|-------------|--------|
| **Uses game engine?** | No (mathematical model) | No (mathematical model) | Yes (runs hands through engine) | No (rule lookup) |
| **Needs transition probabilities?** | Yes (enumerates all cards) | Yes (precomputed dealer distributions) | No (learns from samples) | No |
| **Produces exact EV?** | Yes | Yes | No (approximation) | No (no EV computed) |
| **Multiple runs needed?** | No (deterministic) | No (deterministic) | Yes (6 intervals for convergence) | No (deterministic) |
| **Precomputation step?** | None | Dealer outcome distributions | None | None |
| **State space traversal** | Exhaustive + redundant | Exhaustive + cached | Random sampling | None (rules only) |
| **Can handle unknown rules?** | No | No | Yes | Partially (heuristics are rule-agnostic) |

### Why This Matters

Brute-force and DP both compute exact expected values but DP avoids redundant work.
Comparing their runtimes directly demonstrates the value of memoization.

Monte Carlo is the only algorithm that uses the game engine to play actual hands. The
others work from a mathematical model of the game. This means MC is the only approach
that validates the engine itself — if MC converges to the same strategy as DP, it
confirms both the engine and the mathematical model are correct.

Greedy establishes the floor. Any computation that doesn't beat greedy's win rate is
wasted effort.

The most telling comparison across all four is **strategy accuracy vs. runtime** — it
answers the question: "How much computation do you need to find the right strategy?"
