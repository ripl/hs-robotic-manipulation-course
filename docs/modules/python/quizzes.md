# Quiz Games

<div class="module-summary" markdown>
**Goal:** Students write data-driven quiz games using CSV files and dictionaries.

**Duration:** 1-2 class hours.

**Prerequisites:** Loops, conditionals, lists, dictionaries, and basic file reading.
</div>

## Overview

The new curriculum draft adds two quiz-game modules:

- Element Symbols.
- State Capitals.

Both programs load a CSV file into a dictionary, choose random entries, ask the user questions, and keep score.

## Learning Objectives

- Read lines from a file.
- Parse comma-separated data.
- Store lookup data in a dictionary.
- Choose random keys from a dictionary.
- Delete used questions to avoid repeats.
- Track and report a score.

## Element Symbols

Students quiz each other on chemical element symbols before coding. Then they write a program that loads `elements.csv` and asks for the symbol matching a chosen element.

```python
import random

lines = []

with open("elements.csv") as file:
    for line in file:
        lines.append(line.strip())

elements = {}

for line in lines:
    symbol, name = line.split(",")
    elements[symbol] = name

score = 0

for i in range(10):
    symbol = random.choice(list(elements.keys()))
    name = elements[symbol]
    del elements[symbol]

    answer = input(f"What is the symbol for {name}? ")

    if answer == symbol:
        score += 1
```

## State Capitals

The state capitals version follows the same structure with a different data file. That makes it useful for discussing abstraction: if two programs have the same shape, what would need to change to make one reusable quiz engine?

## Continuity

Quiz games bridge beginner control flow and data-driven programs. They prepare students for later modules where files contain letter frequencies, movie titles, robot positions, or board mappings.

## Repository Code

- Elements quiz: <https://github.com/ripl/hs-robotic-manipulation-course/blob/main/python/2025_ARM/elements_quiz.py>
- Elements data: <https://github.com/ripl/hs-robotic-manipulation-course/blob/main/python/2025_ARM/elements.csv>
- State capitals quiz: <https://github.com/ripl/hs-robotic-manipulation-course/blob/main/python/2025_ARM/state_capitals_quiz.py>
- State capitals data: <https://github.com/ripl/hs-robotic-manipulation-course/blob/main/python/2025_ARM/state_capitals.csv>
