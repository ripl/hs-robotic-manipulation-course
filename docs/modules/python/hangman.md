# Hangman

<div class="module-summary" markdown>
**Goal:** Students write Hangman, then build a computer guesser using letter frequency and movie-title data.

**Duration:** 1-3 class hours depending on extension depth.

**Prerequisites:** Strings, loops, lists, and file reading.
</div>

## Overview

The base program chooses a random movie title. The player guesses letters and loses after six wrong guesses.

The extension makes the computer guess letters. Students compare random guessing, English letter frequency, movie-title frequency, and autocomplete-style filtering.

A second extension lets students choose their own topic, scrape a related web
page into a text file, learn topic-specific letter probabilities, and compare
that guess order against a general-English guess order.

## Learning Objectives

- Slice and rebuild strings.
- Track correct and incorrect guesses.
- Read data from text or CSV files.
- Compare algorithms empirically.
- Use feedback to update the set of possible answers.

## Lesson Flow

1. Students play Hangman in pairs.
2. Students discuss strong letter-guessing strategies.
3. Students implement the human-player version.
4. Students read a letter-frequency file.
5. Students implement computer guessers and compare them.

## Data-Driven Extension

Students can start with a frequency table:

```python
lines = []

with open("letter_frequency.csv") as file:
    for line in file:
        lines.append(line.strip())

letters = []

for line in lines:
    pair = line.split(",")
    letters.append(pair[0])

def get_letter():
    return letters.pop(0)
```

The autocomplete extension filters the movie-title list to titles still compatible with the visible board and wrong guesses. That turns Hangman into a small prediction system.

## Materials

- Student extension writeup: <https://github.com/ripl/hs-robotic-manipulation-course/blob/main/python/2025_ARM/hangman_extension.md>
- Topic frequency writeup: <https://github.com/ripl/hs-robotic-manipulation-course/blob/main/python/2025_ARM/hangman_topic_frequency.md>
- Source code and answer packs: <https://github.com/ripl/hs-robotic-manipulation-course/tree/main/python/2025_ARM>

## Continuity

Hangman introduces action, feedback, belief update, and next action. This is the same loop used in robotics when a camera observes the world and the robot chooses what to do next.
