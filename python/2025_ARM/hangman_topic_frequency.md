# Hangman Extension: Topic Frequency Guesser

## Overview

Pick a topic, collect text about it, count the letters, and then write a Hangman
computer player that guesses letters from most common to least common.

You will build two guessers:

1. General frequency: learn from broad English text.
2. Topic frequency: learn from text close to your Hangman answers.

## Files

- `hangman_topics.py`: the runnable topic-frequency Hangman lab.
- `topic_hangman_data/general_text.txt`: starter general text.
- `topic_hangman_data/topic_text.txt`: starter topic text.
- `topic_hangman_data/topic_answers.txt`: starter answer list.

## How To Run

From the `python/2025_ARM` folder:

```bash
python hangman_topics.py
```

This opens a menu:

```text
1. Scrape a web page into a text file
2. Show letter probabilities
3. Watch the computer play
4. Compare general vs topic frequency
5. Quit
```

Quick commands:

```bash
python hangman_topics.py --summary
python hangman_topics.py --strategy general --answer "indian ocean"
python hangman_topics.py --strategy topic --answer "indian ocean"
python hangman_topics.py --compare --games 50 --seed 7
```

Scrape a page into a text file:

```bash
python hangman_topics.py \
  --scrape-url "https://en.wikipedia.org/wiki/Geography" \
  --out topic_hangman_data/topic_text.txt
```

Use public pages that are okay for classroom use. Avoid login pages and avoid
sending repeated requests. If a site blocks scraping, pick a simpler page or copy
the useful text into the `.txt` file by hand.

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

Then sort the letters to make a guess order:

```python
letters = sorted(counts, key=counts.get, reverse=True)
```

Then write the function Hangman will call instead of asking a human for input:

```python
guessed = []

def get_letter():
    for letter in letters:
        if letter not in guessed:
            guessed.append(letter)
            return letter
```

Your job is to plug `get_letter()` into the Hangman loop so the computer chooses
the next letter.

After it works, compare:

- Does general text guess `e`, `t`, and `a` first?
- Does topic text change the order?
- Does the topic order win more often on topic answers?
- Which topics change the frequency order the most?

## Topic Ideas

- Monster High character names
- Countries, capitals, rivers, mountains, or sports teams
- A favorite movie, book series, album, or video game
- Biology vocabulary, chemistry elements, or space terms
- Local neighborhood places or school event words

## Discussion Questions

- Why do both strategies still often guess `e` early?
- What kind of topic would make unusual letters more useful?
- When does more data help, and when can it hurt?
- Is letter probability enough, or should the computer use the visible board too?
