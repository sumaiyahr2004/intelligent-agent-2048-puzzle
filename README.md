# AI agent plays 2048 puzzle

This project entails an adversarial search agent that plays the 2048 puzzle game using the expectiminimax algorithm with alpha-beta pruning. The AI agent consistently reaches the 1024 and 2048 tiles by evaluating board states through a set of heuristic functions.

[Play the original 2048 puzzle here!](https://play2048.co)

## how does it work? 
2048 is modeled as a two-player game. The Player AI tries to maximize the board score, while the Computer AI places tiles in positions that minimize the Player's outcome. Since the Computer AI places tiles randomly (90% chance of a 2, 10% chance of a 4), expectiminimax is used instead of pure minimax; it accounts for the probabilistic nature of the computer's moves by taking a weighted average over possible tile placements.

The core loop looks like this:
- Player chooses a direction (up, down, left, right) to maximize the board value
- Computer randomly places a 2 or 4 tile on an empty cell
- Repeat until no moves remain

## algorithm 
- Expectiminimax with Alpha-Beta Pruning
- The Player node maximizes over all possible moves
- The Chance node takes a weighted average of outcomes (0.9 for 2-tiles, 0.1 for 4-tiles)
- Alpha-beta pruning cuts off branches that cannot affect the final decision, allowing the search to go deeper within the 0.2 second time limit
- A depth cutoff is used since the full game tree is too large to search completely; thus heuristics estimate the value of non-terminal nodes

# heuristics
The board evaluation function combines several heuristics, each with a tuned weight:
- Monotonicity: rewards boards where tile values consistently increase or decrease along rows and columns. This encourages keeping large tiles in a corner.
- Smoothness: penalizes large differences between adjacent tiles. Boards where neighboring tiles have similar values are easier to merge.
- Free tiles: rewards having more empty cells on the board. Running out of space is the primary way the game ends.
- Merge potential: rewards having identical adjacent tiles that can be merged on the next move.

## project structure 
```
2048-ai/
    IntelligentAgent.py    # Expectiminimax logic, heuristics, alpha-beta pruning
    GameManager.py         # Drives the game loop (read-only)
    Grid.py                # Board representation and operations (read-only)
    BaseAI.py              # Base class for all AI agents (read-only)
    ComputerAI.py          # Random tile placement opponent (read-only)
    Displayer.py         # Prints board state to terminal (read-only)
```

## how to run 
`python3 GameManager.py` 

Note that the board state prints to the terminal after each move. The game ends when no legal moves remain and the highest tile value is displayed. The AI is evaluated over 10 games. The top 5 maximum tile values are averaged for the final score. Target performance is consistently reaching 1024 and 2048 tiles.

Requirements: Python 3, no external dependencies beyond the provided skeleton files

Notes
The 0.2 second move time limit is strict. The search depth is managed dynamically to ensure the agent always returns a move in time. If you run this on a less powerful machine, you may want to reduce the default search depth to stay within the limit.
