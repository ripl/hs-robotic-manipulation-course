# Wordle Lite

## Introduction

In this project, you are required to finish three functions in an existing program to play `Wordle™-lite`, a word-guessing game designed for two human players. In the game, the first player (Player 1) will enter a secret code, and the second player (Player 2) will try to guess that code.

Player 2 starts with 100 points, and every wrong guess costs them 10 points, but they earn back the number of letters that match perfectly in the same place in both words (in Wordle™ this would be the green letters).

This back-and-forth will continue until Player 2 successfully guesses the secret code or the score is not positive, and the game ends.

```bash
Welcome to Wordle™-lite, a word guessing game.
Player 1, enter a secret word: robot
Player 2: Time to guess the secret word; you start with a score of 100.
Wrong guesses cost you 10 but each matched letter earns back 1.
The game ends when you guess the word or the score gets to 0.

What is your guess? (hint: it's a 5-letter word)
Player 2: roads
Player 2: your guess of 'roads' matched ro---; your score is now 92.

What is your guess? (hint: it's a 5-letter word)
Player 2: robot
Player 2: your guess of 'robot' matched robot; your score is now 87.
'robot' is correct, great job! Final score: 87

```

### Where to Begin:

In this folder, you will find a file called `wordle-lite.py`. This folder contains the starter files for the `Wordle™-lite` game.

- Please review the contents of this file and ensure you have an understanding of how it is structured.

## Part 1: Complete the `game_over` Function

First, you’ll complete the `game_over` function. This should report `True` if the guess equals the secret or if the score is not positive, and `False` otherwise.

Here are some examples:

- `game_over('bot', 'box', 15)` --> `False`
- `game_over('bot', 'bot', 15)` --> `True`
- `game_over('bot', 'joy', -2)` --> `True`
- `game_over('love', 'lost', 0)` --> `True`
- `game_over('bot', 'bot', 0)` --> `True`

## Part 2: Complete the `matching_slots` Function

Next, you’ll complete the `matching_slots` function. This function compares the guess with the secret word and returns a string showing which letters are correct (matched positions contain the letter, others are '-').

Here are some examples:

- `matching_slots('love', 'lose')` --> `'lo-e'`
- `matching_slots('game', 'gaze')` --> `'ga-e'`
- `matching_slots('word', 'ward')` --> `'w-rd'`
- `matching_slots('python', 'pytton')` --> `'pyt-on'`
- `matching_slots('robot', 'roast')` --> `'ro--t'`

## Part 3: Complete the `update_score` Function

Finally, you’ll complete the `update_score` function. This function takes the result of the matched slots and the old score and reports an updated score based on the old score minus 10 (cost for a guess) plus the number of slots that matched (were not '-').

Here are some examples:

- `update_score(100, 'lo--')` --> `92` (100 - 10 + 2)
- `update_score(90, 'ga-e')` --> `83` (90 - 10 + 3)
- `update_score(75, '---d')` --> `66` (75 - 10 + 1)
- `update_score(60, 'pyt-on')` --> `55` (60 - 10 + 5)
- `update_score(50, '----')` --> `40` (50 - 10 + 0)

## Acknowledgment

This assignment is from CS10: The Beauty and Joy of Code at the University of California, Berkeley.
