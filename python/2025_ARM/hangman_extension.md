# Hangman Extension: Autocomplete Guesser

## Overview

The original Hangman program asks a human to guess a hidden movie title. In this
extension, the computer guesses the letters. Students can watch the computer
play, race against it, test custom movie titles, choose answer packs, and
compare four strategies:

1. Random: guess any unused letter.
2. English frequency: guess `E`, then `T`, then `A`, and so on.
3. Movie frequency: learn letter percentages from the movie-title file.
4. Autocomplete: filter the movie-title file to possible answers, then guess the
   letter with the highest conditional probability.

This is not heavy machine learning. It is a small prediction system: the program
uses data, updates its belief after feedback, and chooses the next action.

## Learning Objectives

- Read data from text and CSV files.
- Store game state with strings, sets, and lists.
- Compare algorithms by running many trials.
- Use conditional probability to make a better guess.
- Connect hidden-state guessing to robotics: action, feedback, belief update,
  next action.

## Files

- `hangman.py`: original human-player version.
- `hangman_autocomplete.py`: interactive computer-player extension.
- `answers/easy_movies.txt`: easier, familiar answers.
- `answers/medium_movies.txt`: medium-length answers.
- `answers/hard_movies.txt`: longer and harder answers.
- `answers/student_movies.txt`: class-editable answer pack.
- `hangman_answers.txt`: the five original Hangman answers, kept for reference.
- `letter_frequency.csv`: English letter-frequency table.
- `movie_titles.txt`: training data used by the autocomplete guesser.

The secret answers and the training data are separate on purpose. The computer
uses `movie_titles.txt` to make predictions, but the hidden answer comes from
one of the files in `answers/`.

## How To Run

From the `python/2025_ARM` folder:

```bash
python hangman_autocomplete.py
```

This opens a menu:

```text
1. Watch the computer play
2. Compare strategies
3. You vs the computer
4. Test a custom movie title
5. Show data summary
6. Quit
```

## Quick Commands

Run a specific strategy without the menu:

```bash
python hangman_autocomplete.py --strategy random
python hangman_autocomplete.py --strategy frequency
python hangman_autocomplete.py --strategy movie-frequency
python hangman_autocomplete.py --strategy autocomplete
```

Choose a specific answer pack:

```bash
python hangman_autocomplete.py --pack easy
python hangman_autocomplete.py --pack medium
python hangman_autocomplete.py --pack hard
python hangman_autocomplete.py --pack student
```

Ask students to predict each autocomplete guess:

```bash
python hangman_autocomplete.py --pack easy --strategy autocomplete --predict
```

Compare the strategies on the same hidden-answer pool:

```bash
python hangman_autocomplete.py --pack hard --compare --games 100 --seed 7
```

Test a custom answer. This is useful because the answer might not be in the
training data:

```bash
python hangman_autocomplete.py --answer "robot dreams" --strategy autocomplete --predict
```

## Answer Packs

Students can choose a difficulty level before playing:

```text
1. Easy movies
2. Medium movies
3. Hard movies
4. Student titles
```

To make the activity more personal, add class titles to
`answers/student_movies.txt`, one title per line. If students add titles that are
not in `movie_titles.txt`, the autocomplete strategy may start strong but then
fall back to movie-frequency guessing. That is a useful discussion point: the
model can only use the data it has.

## Lesson Flow

### Part 1: Frequency List

Start with the original idea:

```python
def get_letter():
    return elements.pop(0)
```

This guesses the most common English letter that has not already been tried.
It usually beats random guessing, but it ignores the current board.

### Part 2: Learn From Movie Titles

Instead of using a general English table, count letters in `movie_titles.txt`.
This makes the computer learn percentages from the actual data source.

Question for students:

If the hidden answers are movie titles, why might movie-title frequency beat
general English frequency?

### Part 3: Autocomplete With Conditional Probability

Suppose the board is:

```text
_ _ a _ _   _ a _ _ _ e _
```

and the wrong guesses are:

```text
s, t
```

The smarter computer does this:

1. Keep only movie titles with the same length and spaces.
2. Keep only titles with `a` and `e` in the known positions.
3. Remove titles containing wrong letters.
4. Remove titles that put already-guessed letters in hidden slots.
5. Count which unused letter appears in the remaining possible titles.
6. Guess the letter with the highest probability.

The program prints the computer's "brain" like this:

```text
Possible titles left: 5
Examples: moana, mulan, shrek, rocky, creed
Best next letters:
  r: 3/5 = 60%
  e: 2/5 = 40%
  a: 2/5 = 40%
```

This is like autocomplete:

```text
Given what I can see, what completions are still possible?
Given those completions, which next letter is most likely?
```

## Robotics Connection

In manipulation, a robot often does not know the true hidden state. For example,
it may not know an object's exact pose or identity. It takes an action, receives
feedback from sensors, updates the possible states, and chooses another action.

Hangman is a simple version of the same loop:

```text
hidden title -> guess a letter -> observe feedback -> update candidates -> act
```

The six-wrong-guesses limit represents a limited action budget.

## Discussion Questions

- Which strategy wins most often?
- Why does random guessing perform badly?
- When does movie-title frequency beat English frequency?
- What happens if the correct movie is not in `movie_titles.txt`?
- Why can autocomplete become very strong when the answer is in its training data?
- What robotics task has a similar "limited guesses" structure?
