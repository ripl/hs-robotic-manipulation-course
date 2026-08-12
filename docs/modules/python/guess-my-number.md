# Guess My Number

<div class="module-summary" markdown>
**Goal:** Students write a number guessing game, compare random guessing with binary search, and optionally express binary search recursively.

**Duration:** 1-3 class hours depending on extensions.

**Prerequisites:** Python syntax, variables, input, and whitespace.
</div>

## Overview

The program chooses a random number between 1 and 100. The user guesses the number, and the program responds with `higher`, `lower`, or `you got it`. The loop continues until the guess is correct.

The extension flips the roles: the computer guesses the number using either random guesses or binary search.

## Learning Objectives

- Use `random.randint`.
- Read user input and convert it to an integer.
- Compare values with conditionals.
- Use a `while` loop when the number of turns is unknown.
- Count rounds or guesses.
- Compare algorithms by measuring performance.
- Use recursion to express repeated binary-search narrowing.

## Lesson Flow

1. Students play Guess My Number in pairs without computers.
2. The class discusses useful guessing strategies.
3. Students write a player-guessing version.
4. Students write a computer-guessing version.
5. Students compare random guessing against binary search.

## Starter Shape

```python
import random

round_number = 0
playing = True
number = random.randint(1, 100)

print("Guess my number between 1 and 100, inclusive.")

while playing:
    round_number += 1
    guess = int(input("Guess: "))

    if guess > number:
        print("Lower")
    elif guess < number:
        print("Higher")
    else:
        print("You got it!")
        playing = False

print(f"You got it in {round_number} rounds.")
```

## Extension

Students run several trials and store the guesses for each run. The first computer strategy chooses randomly inside the current bounds. The second strategy chooses the midpoint, which gives binary search.

Discussion prompts:

- Why does binary search usually need fewer guesses?
- What changes if the range is 1 to 1,024?
- How could students graph the number of guesses across many trials?

## Recursion Extension

In the recursion extension, the user chooses a number and the computer finds it by recursively applying binary search.

```python
number = int(input("Choose a number between 1 and 100: "))

def get_response(guess):
    if guess > number:
        return "Lower"
    if guess < number:
        return "Higher"
    return "You got it!"

def find_number(lowest, highest):
    guess = (lowest + highest) // 2
    response = get_response(guess)

    if response == "You got it!":
        return guess
    if response == "Higher":
        return find_number(guess + 1, highest)
    return find_number(lowest, guess - 1)

answer = find_number(1, 100)
print(f"Answer is {answer}, and number was {number}.")
```

This extension is a good fit after students have seen functions and are ready to discuss base cases and recursive calls.

## Materials

- [Guess My Number slides](../../assets/downloads/guess-my-number.pptx)
- Source code folder: <https://github.com/ripl/hs-robotic-manipulation-course/tree/main/python/2025_ARM>
