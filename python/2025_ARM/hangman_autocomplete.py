import argparse
import random
import sys
from collections import Counter
from pathlib import Path


LETTERS = "abcdefghijklmnopqrstuvwxyz"
MAX_WRONG_GUESSES = 6
STRATEGIES = ["random", "frequency", "movie-frequency", "autocomplete"]

THIS_FOLDER = Path(__file__).parent
MOVIE_FILE = THIS_FOLDER / "movie_titles.txt"
ANSWER_FILE = THIS_FOLDER / "hangman_answers.txt"
ANSWER_FOLDER = THIS_FOLDER / "answers"
FREQUENCY_FILE = THIS_FOLDER / "letter_frequency.csv"
DEFAULT_ANSWER_PACK = "easy"
ANSWER_PACKS = {
    "easy": ("Easy movies", ANSWER_FOLDER / "easy_movies.txt"),
    "medium": ("Medium movies", ANSWER_FOLDER / "medium_movies.txt"),
    "hard": ("Hard movies", ANSWER_FOLDER / "hard_movies.txt"),
    "student": ("Student titles", ANSWER_FOLDER / "student_movies.txt"),
    "movies": ("All movie_titles.txt titles", MOVIE_FILE),
}


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
            if line.strip().startswith("#"):
                continue
            title = clean_title(line)
            if title:
                titles.append(title)

    return titles


def load_movie_titles(path=MOVIE_FILE):
    return load_titles(path)


def load_answer_titles(path=ANSWER_FILE):
    return load_titles(path)


def answer_pack_label(pack_name):
    label, path = ANSWER_PACKS[pack_name]
    return f"{label} ({path.name})"


def load_answer_pack(pack_name):
    label, path = ANSWER_PACKS[pack_name]
    titles = load_titles(path)

    if not titles:
        raise ValueError(f"No titles found in {path}")

    return titles


def load_letter_frequency(path=FREQUENCY_FILE):
    order = []

    with open(path) as file:
        for line_number, line in enumerate(file):
            if line_number == 0:
                continue

            pair = line.strip().split(",")
            if pair and pair[0]:
                letter = pair[0].lower()
                if letter in LETTERS:
                    order.append(letter)

    return order


def make_movie_frequency(titles):
    counts = Counter()

    for title in titles:
        for char in title:
            if char in LETTERS:
                counts[char] += 1

    return [letter for letter, count in counts.most_common()]


def make_blank_pattern(answer):
    pattern = ""

    for char in answer:
        if char == " ":
            pattern += " "
        else:
            pattern += "_"

    return pattern


def update_pattern(answer, old_pattern, guess):
    new_pattern = ""
    was_correct = False

    for i in range(len(answer)):
        if answer[i] == guess:
            new_pattern += guess
            was_correct = True
        else:
            new_pattern += old_pattern[i]

    return new_pattern, was_correct


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


def first_available_letter(order, guessed_letters):
    for letter in order:
        if letter not in guessed_letters:
            return letter

    for letter in LETTERS:
        if letter not in guessed_letters:
            return letter

    return ""


def random_letter(guessed_letters, rng):
    choices = []

    for letter in LETTERS:
        if letter not in guessed_letters:
            choices.append(letter)

    return rng.choice(choices)


def top_letter_choices(possible_titles, pattern, guessed_letters, fallback_order):
    hits = Counter()

    for title in possible_titles:
        letters_in_unknown_slots = set()

        for i in range(len(title)):
            if pattern[i] == "_" and title[i] in LETTERS and title[i] not in guessed_letters:
                letters_in_unknown_slots.add(title[i])

        for letter in letters_in_unknown_slots:
            hits[letter] += 1

    rank = {}
    for i in range(len(fallback_order)):
        rank[fallback_order[i]] = i

    ranked_letters = sorted(
        hits,
        key=lambda letter: (-hits[letter], rank.get(letter, 100), letter),
    )

    choices = []
    total = len(possible_titles)
    for letter in ranked_letters:
        choices.append((letter, hits[letter], total, hits[letter] / total))

    return choices


def autocomplete_letter(titles, pattern, guessed_letters, wrong_guesses, fallback_order):
    possible_titles = find_possible_titles(
        titles,
        pattern,
        guessed_letters,
        wrong_guesses,
    )
    choices = top_letter_choices(possible_titles, pattern, guessed_letters, fallback_order)

    if not choices:
        letter = first_available_letter(fallback_order, guessed_letters)
        reason = "no matching titles, so I used the movie-frequency list"
        return letter, reason, possible_titles, choices

    letter, hits, total, chance = choices[0]
    reason = (
        f"{hits}/{total} possible titles contain "
        f"'{letter}' in an unknown spot ({chance:.0%})"
    )

    return letter, reason, possible_titles, choices


def get_letter(
    strategy,
    titles,
    pattern,
    guessed_letters,
    wrong_guesses,
    english_frequency,
    movie_frequency,
    rng,
):
    if strategy == "random":
        letter = random_letter(guessed_letters, rng)
        return letter, "random unguessed letter", [], []

    if strategy == "frequency":
        letter = first_available_letter(english_frequency, guessed_letters)
        return letter, "highest remaining letter from English frequency", [], []

    if strategy == "movie-frequency":
        letter = first_available_letter(movie_frequency, guessed_letters)
        return letter, "highest remaining letter from the movie-title file", [], []

    return autocomplete_letter(
        titles,
        pattern,
        guessed_letters,
        wrong_guesses,
        movie_frequency,
    )


def print_header(title):
    print()
    print("=" * len(title))
    print(title)
    print("=" * len(title))


def print_board(pattern, wrong_guesses):
    wrong = " ".join(sorted(wrong_guesses)) if wrong_guesses else "none"
    print(f"Movie: {pattern}")
    print(f"Wrong guesses: {len(wrong_guesses)}/{MAX_WRONG_GUESSES} ({wrong})")


def print_brain(possible_titles, choices, limit=5):
    print(f"Possible titles left: {len(possible_titles)}")

    if possible_titles:
        preview = ", ".join(possible_titles[:5])
        if len(possible_titles) > 5:
            preview += ", ..."
        print(f"Examples: {preview}")

    if not choices:
        print("Best next letters: no matching titles left")
        return

    print("Best next letters:")
    for letter, hits, total, chance in choices[:limit]:
        print(f"  {letter}: {hits}/{total} = {chance:.0%}")


def ask_for_letter(prompt, guessed_letters=None, allow_blank=False):
    while True:
        text = input(prompt).strip().lower()

        if not text and allow_blank:
            return ""
        if len(text) != 1 or text not in LETTERS:
            print("Please type one letter.")
            continue
        if guessed_letters is not None and text in guessed_letters:
            print("That letter was already guessed.")
            continue

        return text


def ask_yes_no(prompt, default=True):
    default_text = "Y/n" if default else "y/N"

    while True:
        text = input(f"{prompt} ({default_text}): ").strip().lower()
        if not text:
            return default
        if text in ["y", "yes"]:
            return True
        if text in ["n", "no"]:
            return False
        print("Please type y or n.")


def ask_int(prompt, default, minimum=1):
    while True:
        text = input(f"{prompt} [{default}]: ").strip()
        if not text:
            return default

        try:
            value = int(text)
        except ValueError:
            print("Please type a whole number.")
            continue

        if value < minimum:
            print(f"Please type a number at least {minimum}.")
            continue

        return value


def ask_optional_int(prompt):
    while True:
        text = input(prompt).strip()
        if not text:
            return None

        try:
            return int(text)
        except ValueError:
            print("Please type a whole number, or press Enter for random.")


def ask_strategy(default="autocomplete"):
    print()
    print("Choose a computer strategy:")
    for i in range(len(STRATEGIES)):
        strategy = STRATEGIES[i]
        marker = " (default)" if strategy == default else ""
        print(f"{i + 1}. {strategy}{marker}")

    while True:
        text = input("Strategy number: ").strip()
        if not text:
            return default
        if text.isdigit():
            index = int(text) - 1
            if 0 <= index < len(STRATEGIES):
                return STRATEGIES[index]
        print("Please choose one of the listed numbers.")


def ask_answer_pack(default=DEFAULT_ANSWER_PACK):
    pack_names = list(ANSWER_PACKS)

    print()
    print("Choose an answer pack:")
    for i in range(len(pack_names)):
        pack_name = pack_names[i]
        label, path = ANSWER_PACKS[pack_name]
        count = len(load_titles(path))
        marker = " (default)" if pack_name == default else ""
        print(f"{i + 1}. {label} - {count} titles{marker}")

    while True:
        text = input("Answer pack number: ").strip()
        if not text:
            pack_name = default
        elif text.isdigit():
            index = int(text) - 1
            if 0 <= index < len(pack_names):
                pack_name = pack_names[index]
            else:
                print("Please choose one of the listed numbers.")
                continue
        else:
            print("Please choose one of the listed numbers.")
            continue

        try:
            return pack_name, load_answer_pack(pack_name)
        except ValueError as error:
            print(error)


def play_game(answer, strategy, titles, rng, verbose=True, ask_prediction=False):
    english_frequency = load_letter_frequency()
    movie_frequency = make_movie_frequency(titles)
    pattern = make_blank_pattern(answer)
    guessed_letters = set()
    wrong_guesses = set()
    guesses = []

    if verbose:
        print_header("Computer Hangman")
        print(f"Strategy: {strategy}")
        print(f"Wrong guesses allowed: {MAX_WRONG_GUESSES}")

    while pattern != answer and len(wrong_guesses) < MAX_WRONG_GUESSES:
        prediction = ""

        if verbose:
            print()
            print_board(pattern, wrong_guesses)

        if ask_prediction:
            prediction = ask_for_letter(
                "What letter do you think the computer will guess? (Enter to skip) ",
                guessed_letters,
                allow_blank=True,
            )

        letter, reason, possible_titles, choices = get_letter(
            strategy,
            titles,
            pattern,
            guessed_letters,
            wrong_guesses,
            english_frequency,
            movie_frequency,
            rng,
        )

        if verbose and strategy == "autocomplete":
            print()
            print_brain(possible_titles, choices)
            if prediction:
                if prediction == letter:
                    print("Your prediction matched the computer.")
                else:
                    print(f"Your prediction was '{prediction}'.")

        guessed_letters.add(letter)
        guesses.append(letter)
        pattern, was_correct = update_pattern(answer, pattern, letter)

        if not was_correct:
            wrong_guesses.add(letter)

        if verbose:
            print()
            print(f"Computer guesses: {letter}")
            print(f"Reason: {reason}")
            if was_correct:
                print("Result: correct")
            else:
                print("Result: wrong")

    won = pattern == answer

    if verbose:
        print()
        print_board(pattern, wrong_guesses)
        if won:
            print(f"The computer won. The title was '{answer}'.")
        else:
            print(f"The computer lost. The title was '{answer}'.")
        print(f"Guesses: {' '.join(guesses)}")

    return {
        "won": won,
        "answer": answer,
        "guess_count": len(guesses),
        "wrong_count": len(wrong_guesses),
    }


def human_vs_computer(answer, strategy, titles, rng):
    english_frequency = load_letter_frequency()
    movie_frequency = make_movie_frequency(titles)

    human_pattern = make_blank_pattern(answer)
    human_guessed = set()
    human_wrong = set()

    computer_pattern = make_blank_pattern(answer)
    computer_guessed = set()
    computer_wrong = set()

    print_header("You vs the Computer")
    print("You and the computer are guessing the same hidden movie title.")
    print("You may use the computer's feedback to improve your own guesses.")
    print(f"Computer strategy: {strategy}")

    while True:
        print()
        print("Your board:")
        print_board(human_pattern, human_wrong)
        print()
        print("Computer board:")
        print_board(computer_pattern, computer_wrong)

        if human_pattern == answer or computer_pattern == answer:
            break
        if len(human_wrong) >= MAX_WRONG_GUESSES or len(computer_wrong) >= MAX_WRONG_GUESSES:
            break

        letter = ask_for_letter("Your guess: ", human_guessed)
        human_guessed.add(letter)
        human_pattern, was_correct = update_pattern(answer, human_pattern, letter)
        if not was_correct:
            human_wrong.add(letter)

        if human_pattern == answer or len(human_wrong) >= MAX_WRONG_GUESSES:
            continue

        letter, reason, possible_titles, choices = get_letter(
            strategy,
            titles,
            computer_pattern,
            computer_guessed,
            computer_wrong,
            english_frequency,
            movie_frequency,
            rng,
        )

        if strategy == "autocomplete":
            print()
            print("Computer brain:")
            print_brain(possible_titles, choices)

        computer_guessed.add(letter)
        computer_pattern, was_correct = update_pattern(answer, computer_pattern, letter)
        if not was_correct:
            computer_wrong.add(letter)

        print()
        print(f"Computer guesses: {letter}")
        print(f"Reason: {reason}")
        if was_correct:
            print("Result: correct")
        else:
            print("Result: wrong")

    print()
    print(f"The title was '{answer}'.")

    human_won = human_pattern == answer
    computer_won = computer_pattern == answer

    if human_won and computer_won:
        print("Tie. You both solved it.")
    elif human_won:
        print("You beat the computer.")
    elif computer_won:
        print("The computer solved it first.")
    elif len(human_wrong) >= MAX_WRONG_GUESSES and len(computer_wrong) >= MAX_WRONG_GUESSES:
        print("Nobody solved it.")
    elif len(human_wrong) >= MAX_WRONG_GUESSES:
        print("You ran out of guesses.")
    else:
        print("The computer ran out of guesses.")


def summarize_results(strategy, results, show_examples=False, max_examples=8):
    wins = 0
    total_guesses = 0
    total_wrong = 0

    for result in results:
        if result["won"]:
            wins += 1
        total_guesses += result["guess_count"]
        total_wrong += result["wrong_count"]

    games = len(results)
    win_rate = wins / games
    average_guesses = total_guesses / games
    average_wrong = total_wrong / games

    print(
        f"{strategy:15} "
        f"wins {wins:3}/{games:<3} "
        f"win rate {win_rate:6.1%} "
        f"avg guesses {average_guesses:5.1f} "
        f"avg wrong {average_wrong:4.1f}"
    )

    if not show_examples:
        return

    losses = []
    solved_examples = []
    for result in results:
        if result["won"]:
            if len(solved_examples) < max_examples:
                solved_examples.append(result)
        elif len(losses) < max_examples:
            losses.append(result)

    if solved_examples:
        print("  Solved examples:")
        for result in solved_examples:
            print(
                f"    {result['answer']} "
                f"({result['guess_count']} guesses, {result['wrong_count']} wrong)"
            )

    if losses:
        print("  Losses:")
        for result in losses:
            print(
                f"    {result['answer']} "
                f"({result['guess_count']} guesses, {result['wrong_count']} wrong)"
            )
    else:
        print("  Losses: none")


def run_many_games(strategy, titles, answers, seed):
    rng = random.Random(seed)
    results = []

    for answer in answers:
        result = play_game(answer, strategy, titles, rng, verbose=False)
        results.append(result)

    return results


def compare_strategies(
    titles,
    answers,
    games,
    seed,
    answer_source,
    training_source=MOVIE_FILE.name,
    use_all_answers=False,
):
    rng = random.Random(seed)

    if use_all_answers:
        sampled_answers = list(answers)
        games = len(sampled_answers)
        sampling = "using every possible answer exactly once"
    else:
        sampled_answers = [rng.choice(answers) for i in range(games)]
        sampling = "random sample with replacement"

    training_set = set(titles)
    answers_in_training = 0
    missing_answers = []
    for answer in answers:
        if answer in training_set:
            answers_in_training += 1
        elif len(missing_answers) < 8:
            missing_answers.append(answer)

    print_header("Hangman Strategy Comparison")
    print(f"Training titles: {len(titles)} from {training_source}")
    print(f"Possible secret answers: {len(answers)} from {answer_source}")
    print(f"Evaluation games: {games} ({sampling})")
    print(f"Wrong guesses allowed per game: {MAX_WRONG_GUESSES}")
    print(
        "Answers present exactly in training data: "
        f"{answers_in_training}/{len(answers)}"
    )
    if missing_answers:
        print("Examples missing from training data:")
        for answer in missing_answers:
            print(f"  {answer}")
    print()

    for strategy in STRATEGIES:
        print(f"Strategy: {strategy}")
        results = run_many_games(strategy, titles, sampled_answers, seed)
        summarize_results(strategy, results, show_examples=True)
        print()


def show_data_summary(titles, training_source=MOVIE_FILE.name):
    print_header("Data Summary")
    print(f"Training titles: {len(titles)} from {training_source}")
    print()
    print("Answer packs:")
    for pack_name in ANSWER_PACKS:
        label, path = ANSWER_PACKS[pack_name]
        answers = load_titles(path)
        print(f"  {label}: {len(answers)} titles from answers/{path.name}")
    print()
    print(f"Original Hangman answers: {len(load_answer_titles())} from {ANSWER_FILE.name}")
    print("The autocomplete strategy filters the training titles after each guess.")
    print("If the secret title is missing from the training data, it falls back to frequency.")


def menu_loop(training_file=MOVIE_FILE):
    titles = load_movie_titles(training_file)
    training_source = Path(training_file).name
    rng = random.Random()

    while True:
        print_header("Hangman Autocomplete Lab")
        print("1. Watch the computer play")
        print("2. Compare strategies")
        print("3. You vs the computer")
        print("4. Test a custom movie title")
        print("5. Show data summary")
        print("6. Quit")

        choice = input("Choose an option: ").strip()

        if choice == "1":
            pack_name, answers = ask_answer_pack()
            strategy = ask_strategy()
            answer = rng.choice(answers)
            print(f"Answer pack: {answer_pack_label(pack_name)}")
            ask_prediction = ask_yes_no("Predict the computer's guesses before it moves", True)
            play_game(answer, strategy, titles, rng, verbose=True, ask_prediction=ask_prediction)
            input("\nPress Enter to return to the menu.")
        elif choice == "2":
            pack_name, answers = ask_answer_pack()
            use_all_answers = pack_name == "movies"
            if use_all_answers:
                games = len(answers)
                print(f"Using all {games} titles from movie_titles.txt.")
            else:
                games = ask_int("How many games should each strategy play?", 20)
            seed = ask_optional_int("Random seed (Enter for random): ")
            compare_strategies(
                titles,
                answers,
                games,
                seed,
                answer_pack_label(pack_name),
                training_source,
                use_all_answers=use_all_answers,
            )
            input("\nPress Enter to return to the menu.")
        elif choice == "3":
            pack_name, answers = ask_answer_pack()
            strategy = ask_strategy()
            answer = rng.choice(answers)
            print(f"Answer pack: {answer_pack_label(pack_name)}")
            human_vs_computer(answer, strategy, titles, rng)
            input("\nPress Enter to return to the menu.")
        elif choice == "4":
            answer = clean_title(input("Movie title for the computer to guess: "))
            if not answer:
                print("Please type a title with at least one letter.")
                continue
            strategy = ask_strategy()
            play_game(answer, strategy, titles, rng, verbose=True, ask_prediction=True)
            input("\nPress Enter to return to the menu.")
        elif choice == "5":
            show_data_summary(titles, training_source)
            input("\nPress Enter to return to the menu.")
        elif choice in ["6", "q", "quit", "exit"]:
            print("Goodbye.")
            return
        else:
            print("Please choose a number from 1 to 6.")


def run_from_args(args):
    if args.games < 1:
        raise SystemExit("--games must be at least 1")

    training_file = Path(args.training_file)
    titles = load_movie_titles(training_file)
    answer_titles = load_answer_pack(args.pack)
    rng = random.Random(args.seed)

    if args.answer:
        answer = clean_title(args.answer)
        if not answer:
            raise SystemExit("--answer must contain at least one letter")
        answers = [answer for i in range(args.games)]
    elif args.all_answers:
        answers = list(answer_titles)
    else:
        answers = [rng.choice(answer_titles) for i in range(args.games)]

    if args.compare:
        use_all_answers = args.all_answers or args.pack == "movies"

        if args.answer:
            compare_strategies(
                titles,
                [answer],
                args.games,
                args.seed,
                "custom --answer",
                str(training_file),
                use_all_answers=args.all_answers,
            )
        else:
            compare_strategies(
                titles,
                answer_titles,
                args.games,
                args.seed,
                answer_pack_label(args.pack),
                str(training_file),
                use_all_answers=use_all_answers,
            )
        return

    if len(answers) == 1:
        play_game(
            answers[0],
            args.strategy,
            titles,
            rng,
            verbose=True,
            ask_prediction=args.predict,
        )
    else:
        results = run_many_games(args.strategy, titles, answers, args.seed)
        summarize_results(args.strategy, results)


def main():
    if len(sys.argv) == 1:
        menu_loop()
        return

    parser = argparse.ArgumentParser()
    parser.add_argument("--menu", action="store_true", help="open the classroom menu")
    parser.add_argument("--strategy", choices=STRATEGIES, default="autocomplete")
    parser.add_argument("--pack", choices=list(ANSWER_PACKS), default=DEFAULT_ANSWER_PACK)
    parser.add_argument("--games", type=int, default=1)
    parser.add_argument("--seed", type=int, default=None)
    parser.add_argument("--answer", type=str, default=None)
    parser.add_argument("--compare", action="store_true")
    parser.add_argument("--predict", action="store_true")
    parser.add_argument("--training-file", type=str, default=str(MOVIE_FILE))
    parser.add_argument(
        "--all-answers",
        action="store_true",
        help="use every answer from the selected answer pack instead of sampling",
    )
    args = parser.parse_args()

    if args.menu:
        menu_loop(Path(args.training_file))
    else:
        run_from_args(args)


if __name__ == "__main__":
    main()
