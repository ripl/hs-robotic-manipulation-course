# Tic-Tac-Toe

<div class="module-summary" markdown>
**Goal:** Students write Tic-Tac-Toe, add a computer player, and prepare for the robotic-arm version.

**Duration:** 2-5 class hours depending on extensions.

**Prerequisites:** Lists, loops, conditionals, helper functions.
</div>

## Overview

Students build a terminal Tic-Tac-Toe game where players take turns placing `X` or `O` on a 3-by-3 board. The game ends when one player has three in a row or when the board is full.

This is the most important continuity module in the course because the final robot arm project uses Tic-Tac-Toe as its game environment.

## Learning Objectives

- Represent a board as a list.
- Validate user input.
- Use helper functions to print the board, get a move, and find a winner.
- Detect rows, columns, and diagonals.
- Add a computer player that can win, block, or play randomly.

## Suggested Function Breakdown

```python
def print_board():
    ...

def get_play():
    ...

def find_winner():
    ...

def get_computer_play():
    ...
```

## Computer Player Extension

The first computer player can choose randomly from empty squares.

The second computer player should:

1. Play a winning move if one exists.
2. Block the opponent's winning move if one exists.
3. Otherwise choose randomly.

## Connection to the Robot

The robot arm version adds three systems to the same game logic:

- A camera system that reads the board.
- A decision system that chooses a legal move.
- A motion system that places a piece on the board.

The Python game makes those later systems easier to understand because students already know the game state and rules.

## Repository Code

- Game logic: <https://github.com/ripl/hs-robotic-manipulation-course/tree/main/robotics/game>
- Advanced Tic-Tac-Toe examples: <https://github.com/ripl/hs-robotic-manipulation-course/tree/main/python/advanced/oop/ttt>
