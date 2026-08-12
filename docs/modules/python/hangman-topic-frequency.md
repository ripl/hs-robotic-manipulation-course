# Hangman Topic Frequency

<div class="module-summary" markdown>
**Goal:** Students collect topic text, compute letter frequencies, then write a
Hangman computer guesser that uses those frequencies.

**Duration:** 1 class hour, with optional extension time.

**Prerequisites:** Strings, loops, dictionaries, files, and the base Hangman game.
</div>

## Overview

This one-day activity turns Hangman into a small data-driven program. Students
pick a topic, save related web text into a `.txt` file, count the letters, sort
the letters from most common to least common, and then write the Hangman code
that guesses letters in that order.

The included `hangman_topics.py` file is a runnable reference and demo. The main
student task is to build the frequency-based guesser themselves.

## Learning Objectives

- Read text from a file.
- Count letters with a dictionary.
- Sort letters by frequency.
- Write a `get_letter()` function that chooses the next computer guess.
- Compare a general-text guesser against a topic-text guesser.

## Lesson Flow

1. Play one quick Hangman round and discuss smart first letters.
2. Collect or paste text into `general_text.txt` and `topic_text.txt`.
3. Count letter frequencies with a dictionary.
4. Sort letters to create a guess order.
5. Add a `get_letter()` function to Hangman.
6. Run the computer guesser and compare general vs topic data.

## One-Day Plan

| Time | Activity |
| --- | --- |
| 5 min | Play Hangman and predict good letter guesses. |
| 10 min | Show the starter demo and letter-frequency output. |
| 15 min | Students write the dictionary-counting code. |
| 15 min | Students write `get_letter()` and plug it into Hangman. |
| 10 min | Students swap in topic text and compare results. |
| 5 min | Exit ticket and discussion. |

## Starter Run

From `python/2025_ARM`:

```bash
python hangman_topics.py --summary
python hangman_topics.py --compare --games 10 --seed 7
```

The included starter data uses a geography topic about continents and oceans.
It is there so students can see the full target behavior before writing their
own version.

## Student Build

First, count letters:

```python
counts = {}

with open("topic_hangman_data/topic_text.txt") as file:
    text = file.read().lower()

for char in text:
    if char in "abcdefghijklmnopqrstuvwxyz":
        if char not in counts:
            counts[char] = 0
        counts[char] += 1
```

Then make the guess order:

```python
letters = sorted(counts, key=counts.get, reverse=True)
```

Then write the function Hangman will call:

```python
guessed = []

def get_letter():
    for letter in letters:
        if letter not in guessed:
            guessed.append(letter)
            return letter
```

Students should plug this into their Hangman loop where the human player used to
type a guess.

## Data Collection

Use the menu for scraping or testing:

```bash
python hangman_topics.py
```

or run a direct scrape:

```bash
python hangman_topics.py \
  --scrape-url "https://en.wikipedia.org/wiki/Geography" \
  --out topic_hangman_data/topic_text.txt
```

If scraping is distracting, students can copy and paste useful page text into the
`.txt` files by hand.

## Checks For Understanding

- What are the keys and values in the `counts` dictionary?
- Where does the `letters` guess order come from?
- How does `get_letter()` avoid repeating a guess?
- Did topic text beat general text? Why or why not?

## Exit Ticket

Students submit their topic, their top five general letters, their top five topic
letters, and the `get_letter()` function they wrote.

## Materials

- Student writeup: <https://github.com/ripl/hs-robotic-manipulation-course/blob/main/python/2025_ARM/hangman_topic_frequency.md>
- Source code: <https://github.com/ripl/hs-robotic-manipulation-course/blob/main/python/2025_ARM/hangman_topics.py>

## Continuity

This is a simpler companion to the autocomplete Hangman extension. Here the
computer only learns a letter order from data; later, autocomplete also uses the
visible board to update possible answers.
