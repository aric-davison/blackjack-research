# CPT S 350 – Final Project

# Milestone 1 Proposal

Course: CPT S 350 – Design and Analysis of Algorithms
Instructor: Dr. Jodeiri Akbarfam
**Project Title:** Algorithmic Approaches to Optimal
Blackjack Strategy
**Team Member Names:** Aric Davison
**Project Category:** Empirical / Experimental
**Proposed Topic:** Comparing DP, Monte Carlo,
Greedy, and Brute Force for
Blackjack Decision Optimization


## 1. Introduction & Motivation

Blackjack is one of the most extensively studied casino card games from a mathematical
perspective, and it provides a compelling testbed for comparing algorithmic strategies. The core
decision problem—whether to hit, stand, double down, or split given a player’s hand and the
dealer’s visible card—can be modeled as an optimization problem over a well-defined state
space.
What makes this problem interesting from an algorithms standpoint is that multiple
computational approaches can be used to derive an optimal (or near-optimal) strategy, each with
fundamentally different time and space tradeoffs. A brute-force enumeration of all possible
action sequences is exponential. Dynamic programming with memoization can collapse the state
space dramatically by exploiting overlapping subproblems. Monte Carlo simulation offers a
probabilistic alternative that converges over many trials. Greedy heuristics provide fast but
potentially suboptimal solutions.
This project will implement all four approaches, compare the quality of the strategies they
produce, and analyze their computational complexity both theoretically and empirically. The
goal is to demonstrate how algorithm design choices directly impact both the quality of the
solution and the resources required to compute it.

## 2. Project Scope & Objectives

The main objectives of this project are:

1. **Model the blackjack decision problem formally.** Define the state space (player hand
    value, dealer upcard, usable ace), action space (hit, stand, double, split), and transition
    probabilities based on standard rules.
2. **Implement four algorithmic approaches.** Brute-force enumeration, dynamic
    programming with memoization, Monte Carlo simulation, and a greedy heuristic
    baseline.
3. **Compare strategy quality.** Evaluate whether each approach converges to the known
    mathematically optimal basic strategy, and measure any deviations.
4. **Analyze computational complexity.** Measure and compare wall-clock runtime, memory
    usage, and number of states explored for each algorithm. Compare empirical results to
    theoretical complexity bounds.
5. **Produce a strategy comparison table.** Generate visual strategy tables
    (hit/stand/double/split grids) for each approach and compare them against the known
    optimal basic strategy.

## 3. Approach / Initial Plan

The project will be implemented in Python, building on an existing blackjack simulation
codebase (https://github.com/aric-davison/blackjack). The four algorithmic approaches will each
produce a strategy table mapping every possible game state to a recommended action.
**Brute-Force Enumeration**


For each possible game state, recursively evaluate every sequence of actions (hit/stand/double)
and compute the expected value of each path by enumerating all possible card draws. This
establishes a correctness baseline but is expected to be computationally expensive due to the
exponential branching factor.
**Dynamic Programming with Memoization**
Precompute the dealer’s outcome probability distribution for each possible upcard, then use
bottom-up or top-down DP to compute optimal expected values for each player state. The key
insight is that many player states share the same dealer outcome subproblem, allowing
significant computation reuse. The state space is bounded: roughly 300–400 unique player states
multiplied by 10 dealer upcards.
**Monte Carlo Simulation**
Simulate a large number of blackjack hands (ranging from 10,000 to 10,000,000) using
randomized play, then estimate the expected value of each action in each state based on observed
outcomes. This approach does not require explicit knowledge of transition probabilities. The
convergence rate and accuracy as a function of the number of simulations will be a key metric.
**Greedy Heuristic**
Implement simple rule-based heuristics such as “always stand on 17 or higher” and “always hit
below 12.” These require negligible computation but produce suboptimal strategies. They serve
as a lower bound on strategy quality and demonstrate the cost of ignoring the full problem
structure.
**Evaluation Methodology**
Each algorithm’s output strategy will be evaluated by simulating 1,000,000 hands against a
standard dealer and recording the win rate and average return. Runtime and memory will be
measured using Python’s time and tracemalloc modules. Results will be compared against the
known mathematically optimal basic strategy.

## 4. Expected Outcomes

The expected outcomes of this project include:

- Both the brute-force and DP approaches should converge to the known optimal basic
    strategy, with DP achieving this in significantly less time due to memoization.
- Monte Carlo simulation should approximate the optimal strategy with increasing
    accuracy as the number of simulations grows, but with diminishing returns past a certain
    threshold.
- Greedy heuristics will produce measurably worse strategies (higher house edge) but with
    near-zero computation time.
- Empirical complexity measurements should align with theoretical predictions:
    exponential for brute force, polynomial for DP, and linear in the number of simulations
    for Monte Carlo.


- A set of visual strategy comparison tables and performance graphs showing runtime vs.
    strategy quality tradeoffs.

## 5. Timeline

```
Timeframe Tasks
Feb 19 – Mar 12(Weeks
6–9)
Formalize the blackjack state space and decision model. Extend
existing simulation engine to support all four algorithmic
approaches. Implement brute-force enumeration and greedy
heuristic as baselines.
Spring Break Buffer time / continued implementation if needed.
Mar 24 – Apr 7(Weeks
10–12)
Implement dynamic programming with memoization and Monte
Carlo simulation. Prepare Milestone 2 presentation slides (due
Mar 24). Run initial experiments. Submit Milestone 2 written
report (due Apr 7).
Apr 7 – Apr 23(Weeks
12–14)
Complete all experiments and collect final performance data.
Generate strategy comparison tables and complexity graphs.
Write final report. Submit Milestone 3 / final written deliverable
(due Apr 23).
Apr 28 – Apr 30(Week
15)
Final project presentations. Submit final project files (due Apr
30).
```
## 6. References

Thorp, E. O. (1966). Beat the Dealer: A Winning Strategy for the Game of Twenty-One. Vintage
Books.
Baldwin, R., Cantey, W., Maisel, H., & McDermott, J. (1956). “The Optimum Strategy in
Blackjack.” Journal of the American Statistical Association, 51(275), 429–439.
Cormen, T. H., Leiserson, C. E., Rivest, R. L., & Stein, C. (2022). Introduction to Algorithms
(4th ed.). MIT Press.
Sutton, R. S., & Barto, A. G. (2018). Reinforcement Learning: An Introduction (2nd ed.). MIT
Press.


