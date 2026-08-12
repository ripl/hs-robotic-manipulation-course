# Pig

<div class="module-summary" markdown>
**Goal:** Students write the dice game Pig and test simple computer strategies.

**Duration:** 1-2 class hours.

**Prerequisites:** Basic Python syntax, conditionals, loops, and random numbers.
</div>

## Overview

Pig is a two-player game of chance and strategy. On a turn, a player rolls a die repeatedly until they either roll a `1` or choose to bank their points. If they roll a `1`, the turn ends and the turn total is lost. The first player to reach the target score wins.

## Learning Objectives

- Use nested loops to model rounds and turns.
- Track multiple scores.
- Use conditionals for turn outcomes.
- Ask for repeated user choices.
- Turn a strategy into a helper function.

## Lesson Flow

1. Students play Pig in pairs using physical dice.
2. Students discuss when it is smart to bank.
3. Students implement the two-player terminal version.
4. Students add a computer player.
5. Students test different computer banking strategies.

## Strategy Extension

The simplest computer strategy banks after either a high enough round total or enough rolls:

```python
def get_computer_choice(total_for_round, roll_number):
    if total_for_round >= 15 or roll_number >= 4:
        return "b"
    return "r"
```

Students can change the thresholds and compare win rates.

## Continuity

Pig is useful because students must keep track of local state and global state at the same time. The same idea appears later when the robot must track the current board, current move, and physical arm position.
