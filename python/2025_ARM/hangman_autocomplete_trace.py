import argparse
from pathlib import Path

from hangman_autocomplete import (
    LETTERS,
    MAX_WRONG_GUESSES,
    clean_title,
    find_possible_titles,
    first_available_letter,
    load_movie_titles,
    make_blank_pattern,
    make_movie_frequency,
    top_letter_choices,
    update_pattern,
)


THIS_FOLDER = Path(__file__).parent
DEFAULT_TRAINING_FILE = THIS_FOLDER / "movie_titles.txt"


def format_letters(letters):
    if not letters:
        return "none"

    return " ".join(sorted(letters))


def same_spaces(title, pattern):
    if len(title) != len(pattern):
        return False

    for i in range(len(pattern)):
        if (title[i] == " ") != (pattern[i] == " "):
            return False

    return True


def known_letters_match(title, pattern):
    for i in range(len(pattern)):
        if pattern[i] in LETTERS and title[i] != pattern[i]:
            return False

    return True


def wrong_letters_absent(title, wrong_guesses):
    for wrong in wrong_guesses:
        if wrong in title:
            return False

    return True


def no_hidden_guessed_letters(title, pattern, guessed_letters):
    for i in range(len(pattern)):
        if pattern[i] == "_" and title[i] in guessed_letters:
            return False

    return True


def filter_trace(titles, pattern, guessed_letters, wrong_guesses):
    same_length = []
    for title in titles:
        if len(title) == len(pattern):
            same_length.append(title)

    same_space_pattern = []
    for title in same_length:
        if same_spaces(title, pattern):
            same_space_pattern.append(title)

    matching_known_letters = []
    for title in same_space_pattern:
        if known_letters_match(title, pattern):
            matching_known_letters.append(title)

    without_wrong_letters = []
    for title in matching_known_letters:
        if wrong_letters_absent(title, wrong_guesses):
            without_wrong_letters.append(title)

    without_hidden_guessed = []
    for title in without_wrong_letters:
        if no_hidden_guessed_letters(title, pattern, guessed_letters):
            without_hidden_guessed.append(title)

    return [
        ("all training titles", titles),
        ("same length", same_length),
        ("same spaces", same_space_pattern),
        ("known letters match", matching_known_letters),
        ("wrong letters removed", without_wrong_letters),
        ("already-guessed letters not hidden", without_hidden_guessed),
    ]


def print_filter_trace(stages):
    previous_count = None

    print("Filtering candidates:")
    for label, candidates in stages:
        count = len(candidates)
        if previous_count is None:
            print(f"  {label:34} {count:4}")
        else:
            removed = previous_count - count
            print(f"  {label:34} {count:4}  removed {removed:4}")
        previous_count = count


def print_examples(possible_titles, limit):
    if not possible_titles:
        print("Remaining candidates: none")
        return

    examples = ", ".join(possible_titles[:limit])
    if len(possible_titles) > limit:
        examples += ", ..."

    print(f"Remaining candidates: {examples}")


def print_conditional_frequencies(choices, possible_count, limit):
    print("Conditional letter frequencies:")
    print("  Meaning: among the remaining candidate movies,")
    print("  how many contain this letter in at least one hidden slot?")

    if not choices:
        print("  none")
        return

    for letter, hits, total, chance in choices[:limit]:
        print(f"  {letter}: {hits}/{possible_count} = {chance:.0%}")


def choose_autocomplete_letter(titles, pattern, guessed_letters, wrong_guesses, fallback_order):
    possible_titles = find_possible_titles(
        titles,
        pattern,
        guessed_letters,
        wrong_guesses,
    )
    choices = top_letter_choices(
        possible_titles,
        pattern,
        guessed_letters,
        fallback_order,
    )

    if choices:
        letter, hits, total, chance = choices[0]
        reason = f"{hits}/{total} candidates contain '{letter}' in a hidden slot"
        return letter, reason, possible_titles, choices

    letter = first_available_letter(fallback_order, guessed_letters)
    reason = "no candidates remain, so fall back to overall movie frequency"
    return letter, reason, possible_titles, choices


def run_trace(answer, titles, training_file, top):
    fallback_order = make_movie_frequency(titles)
    pattern = make_blank_pattern(answer)
    guessed_letters = set()
    wrong_guesses = set()
    step = 1

    print()
    print("Autocomplete Hangman Trace")
    print("==========================")
    print(f"Hidden answer: {answer}")
    print(f"Training file: {training_file}")
    print(f"Training titles: {len(titles)}")
    print(f"Wrong guesses allowed: {MAX_WRONG_GUESSES}")
    print()
    print("The computer does not see the answer. It sees only the board,")
    print("the letters already guessed, and the letters known to be wrong.")

    while pattern != answer and len(wrong_guesses) < MAX_WRONG_GUESSES:
        print()
        print(f"Step {step}")
        print("-" * 40)
        print(f"Board: {pattern}")
        print(f"Guessed letters: {format_letters(guessed_letters)}")
        print(f"Wrong guesses: {format_letters(wrong_guesses)}")
        print()

        stages = filter_trace(titles, pattern, guessed_letters, wrong_guesses)
        print_filter_trace(stages)

        letter, reason, possible_titles, choices = choose_autocomplete_letter(
            titles,
            pattern,
            guessed_letters,
            wrong_guesses,
            fallback_order,
        )

        print()
        print_examples(possible_titles, top)
        print()
        print_conditional_frequencies(choices, len(possible_titles), top)
        print()
        print(f"Chosen guess: {letter}")
        print(f"Reason: {reason}")

        guessed_letters.add(letter)
        pattern, was_correct = update_pattern(answer, pattern, letter)

        if was_correct:
            print(f"Feedback: correct, reveal every '{letter}'")
        else:
            wrong_guesses.add(letter)
            print(f"Feedback: wrong, add '{letter}' to wrong guesses")

        step += 1

    print()
    print("Final result")
    print("------------")
    print(f"Board: {pattern}")
    print(f"Wrong guesses: {len(wrong_guesses)}/{MAX_WRONG_GUESSES}")
    print(f"Guesses: {format_letters(guessed_letters)}")
    if pattern == answer:
        print("Solved.")
    else:
        print("Not solved.")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--answer", default="black panther")
    parser.add_argument("--training-file", type=Path, default=DEFAULT_TRAINING_FILE)
    parser.add_argument("--top", type=int, default=8)
    args = parser.parse_args()

    answer = clean_title(args.answer)
    if not answer:
        raise SystemExit("--answer must contain at least one letter")
    if args.top < 1:
        raise SystemExit("--top must be at least 1")

    titles = load_movie_titles(args.training_file)
    run_trace(answer, titles, args.training_file, args.top)


if __name__ == "__main__":
    main()
