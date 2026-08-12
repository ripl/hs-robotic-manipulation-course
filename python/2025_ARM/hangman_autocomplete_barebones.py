from collections import Counter


LETTERS = "abcdefghijklmnopqrstuvwxyz"


def clean_title(title):
    title = title.strip().lower()
    cleaned = []
    last_was_space = False

    for char in title:
        if char in LETTERS:
            cleaned.append(char)
            last_was_space = False
        elif char == " " and cleaned and not last_was_space:
            cleaned.append(" ")
            last_was_space = True

    return "".join(cleaned).strip()


def load_titles(path):
    titles = []

    with open(path) as file:
        for line in file:
            title = clean_title(line)
            if title and not line.strip().startswith("#"):
                titles.append(title)

    return titles


def matches_pattern(title, pattern, guessed_letters, wrong_guesses):
    if len(title) != len(pattern):
        return False

    for wrong in wrong_guesses:
        if wrong in title:
            return False

    for i in range(len(pattern)):
        pattern_char = pattern[i]
        title_char = title[i]

        if pattern_char == " ":
            if title_char != " ":
                return False
        elif pattern_char == "_":
            if title_char == " ":
                return False
            if title_char in guessed_letters:
                return False
        elif title_char != pattern_char:
            return False

    return True


def find_possible_titles(titles, pattern, guessed_letters, wrong_guesses):
    possible_titles = []

    for title in titles:
        if matches_pattern(title, pattern, guessed_letters, wrong_guesses):
            possible_titles.append(title)

    return possible_titles


def rank_letters(possible_titles, pattern, guessed_letters):
    counts = Counter()

    for title in possible_titles:
        letters_in_title = set()

        for i in range(len(title)):
            if pattern[i] == "_" and title[i] in LETTERS and title[i] not in guessed_letters:
                letters_in_title.add(title[i])

        for letter in letters_in_title:
            counts[letter] += 1

    return sorted(counts.items(), key=lambda item: (-item[1], item[0]))


def guess_letter(titles, pattern, guessed_letters, wrong_guesses):
    possible_titles = find_possible_titles(
        titles,
        pattern,
        guessed_letters,
        wrong_guesses,
    )
    letter_counts = rank_letters(possible_titles, pattern, guessed_letters)

    if not letter_counts:
        return None, possible_titles, []

    best_letter, count = letter_counts[0]
    choices = []

    for letter, count in letter_counts:
        choices.append((letter, count, count / len(possible_titles)))

    return best_letter, possible_titles, choices
