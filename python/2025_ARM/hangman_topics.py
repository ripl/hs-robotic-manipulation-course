import argparse
import html
import random
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


LETTERS = "abcdefghijklmnopqrstuvwxyz"
MAX_WRONG_GUESSES = 6
STRATEGIES = ["general", "topic"]

THIS_FOLDER = Path(__file__).parent
DATA_FOLDER = THIS_FOLDER / "topic_hangman_data"
GENERAL_TEXT_FILE = DATA_FOLDER / "general_text.txt"
TOPIC_TEXT_FILE = DATA_FOLDER / "topic_text.txt"
ANSWER_FILE = DATA_FOLDER / "topic_answers.txt"


class VisibleTextParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []
        self.skip_depth = 0

    def handle_starttag(self, tag, attrs):
        if tag in ["script", "style", "noscript", "svg"]:
            self.skip_depth += 1
        elif tag in ["p", "br", "li", "h1", "h2", "h3", "tr"]:
            self.parts.append("\n")

    def handle_endtag(self, tag):
        if tag in ["script", "style", "noscript", "svg"] and self.skip_depth > 0:
            self.skip_depth -= 1
        elif tag in ["p", "li", "h1", "h2", "h3", "tr"]:
            self.parts.append("\n")

    def handle_data(self, data):
        if self.skip_depth == 0:
            self.parts.append(data)

    def get_text(self):
        text = html.unescape("".join(self.parts))
        lines = []

        for line in text.splitlines():
            line = " ".join(line.split())
            if line:
                lines.append(line)

        return "\n".join(lines)


def print_header(title):
    print()
    print("=" * len(title))
    print(title)
    print("=" * len(title))


def clean_answer(text):
    text = text.strip().lower()
    cleaned = []
    last_was_space = False

    for char in text:
        if char in LETTERS:
            cleaned.append(char)
            last_was_space = False
        elif char == " " and cleaned and not last_was_space:
            cleaned.append(" ")
            last_was_space = True

    return "".join(cleaned).strip()


def load_answers(path=ANSWER_FILE):
    answers = []

    with open(path, encoding="utf-8") as file:
        for line in file:
            if line.strip().startswith("#"):
                continue

            answer = clean_answer(line)
            if answer:
                answers.append(answer)

    if not answers:
        raise ValueError(f"No answers found in {path}")

    return answers


def fetch_webpage_text(url):
    request = Request(
        url,
        headers={"User-Agent": "TopicHangmanClassroom/1.0"},
    )

    with urlopen(request, timeout=20) as response:
        charset = response.headers.get_content_charset() or "utf-8"
        page = response.read().decode(charset, errors="replace")

    parser = VisibleTextParser()
    parser.feed(page)
    return parser.get_text()


def scrape_to_file(url, output_path):
    output_path = Path(output_path)
    text = fetch_webpage_text(url)

    if not text:
        raise ValueError("The web page did not contain readable text.")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(text + "\n", encoding="utf-8")
    return output_path, text


def read_text(path):
    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(f"Could not find {path}")

    return path.read_text(encoding="utf-8")


def count_letters(text):
    counts = {}

    for char in text.lower():
        if char in LETTERS:
            if char not in counts:
                counts[char] = 0
            counts[char] += 1

    return counts


def make_frequency_order(counts):
    return sorted(LETTERS, key=lambda letter: (-counts.get(letter, 0), letter))


def load_frequency_model(path, label):
    text = read_text(path)
    counts = count_letters(text)
    total = sum(counts.values())

    if total == 0:
        raise ValueError(f"{path} does not contain any letters.")

    return {
        "label": label,
        "path": Path(path),
        "counts": counts,
        "total": total,
        "order": make_frequency_order(counts),
    }


def print_frequency_table(model, limit=10):
    print(f"{model['label']} text: {model['path']}")
    print(f"Letters counted: {model['total']}")
    print()
    print("Most common letters:")

    for letter in model["order"][:limit]:
        count = model["counts"].get(letter, 0)
        percent = count / model["total"]
        print(f"  {letter}: {count}/{model['total']} = {percent:.1%}")

    print()
    print("Guess order:")
    print(" ".join(model["order"]))


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


def first_available_letter(order, guessed_letters):
    for letter in order:
        if letter not in guessed_letters:
            return letter

    return ""


def letter_reason(letter, model):
    count = model["counts"].get(letter, 0)
    percent = count / model["total"]
    return (
        f"'{letter}' is the most common unguessed letter in "
        f"{model['label']} text: {count}/{model['total']} = {percent:.1%}"
    )


def print_board(pattern, wrong_guesses):
    wrong = " ".join(sorted(wrong_guesses)) if wrong_guesses else "none"
    print(f"Answer: {pattern}")
    print(f"Wrong guesses: {len(wrong_guesses)}/{MAX_WRONG_GUESSES} ({wrong})")


def play_game(answer, model, verbose=True):
    pattern = make_blank_pattern(answer)
    guessed_letters = set()
    wrong_guesses = set()
    guesses = []

    if verbose:
        print_header("Topic Hangman")
        print(f"Computer strategy: {model['label']} frequency")
        print(f"Training file: {model['path']}")
        print(f"Wrong guesses allowed: {MAX_WRONG_GUESSES}")

    while pattern != answer and len(wrong_guesses) < MAX_WRONG_GUESSES:
        letter = first_available_letter(model["order"], guessed_letters)

        if not letter:
            break

        guessed_letters.add(letter)
        guesses.append(letter)
        pattern, was_correct = update_pattern(answer, pattern, letter)

        if not was_correct:
            wrong_guesses.add(letter)

        if verbose:
            print()
            print_board(pattern, wrong_guesses)
            print(f"Computer guesses: {letter}")
            print(f"Reason: {letter_reason(letter, model)}")
            if was_correct:
                print("Result: correct")
            else:
                print("Result: wrong")

    won = pattern == answer

    if verbose:
        print()
        if won:
            print(f"The computer won. The answer was '{answer}'.")
        else:
            print(f"The computer lost. The answer was '{answer}'.")
        print(f"Guesses: {' '.join(guesses)}")

    return {
        "won": won,
        "answer": answer,
        "guess_count": len(guesses),
        "wrong_count": len(wrong_guesses),
    }


def summarize_results(strategy, results):
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
        f"{strategy:8} "
        f"wins {wins:3}/{games:<3} "
        f"win rate {win_rate:6.1%} "
        f"avg guesses {average_guesses:5.1f} "
        f"avg wrong {average_wrong:4.1f}"
    )


def compare_models(general_model, topic_model, answers, games, seed, answers_path=ANSWER_FILE):
    if games < 1:
        raise ValueError("games must be at least 1")

    rng = random.Random(seed)
    sampled_answers = [rng.choice(answers) for i in range(games)]

    print_header("General vs Topic Frequency")
    print(f"Games: {games}")
    print(f"Answers file: {answers_path}")
    print(f"General training file: {general_model['path']}")
    print(f"Topic training file: {topic_model['path']}")
    print()

    for strategy, model in [("general", general_model), ("topic", topic_model)]:
        results = []

        for answer in sampled_answers:
            results.append(play_game(answer, model, verbose=False))

        summarize_results(strategy, results)


def show_data_summary(general_model, topic_model, answers, answers_path=ANSWER_FILE, limit=10):
    print_header("Topic Hangman Data")
    print_frequency_table(general_model, limit)
    print()
    print_frequency_table(topic_model, limit)
    print()
    print(f"Answers: {len(answers)} from {answers_path}")
    print("Examples: " + ", ".join(answers[:5]))


def ask_path(prompt, default):
    text = input(f"{prompt} [{default}]: ").strip()

    if text:
        return Path(text)

    return Path(default)


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


def ask_strategy(default="topic"):
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


def choose_answer(answers):
    print()
    print("1. Random answer from topic_answers.txt")
    print("2. Type my own answer")

    while True:
        choice = input("Answer choice [1]: ").strip()

        if choice in ["", "1"]:
            return random.choice(answers)
        if choice == "2":
            answer = clean_answer(input("Secret answer: "))
            if answer:
                return answer
            print("Please type an answer with at least one letter.")
        else:
            print("Please choose 1 or 2.")


def load_default_models(general_text, topic_text, answers_path):
    general_model = load_frequency_model(general_text, "general")
    topic_model = load_frequency_model(topic_text, "topic")
    answers = load_answers(answers_path)
    return general_model, topic_model, answers


def menu_loop(general_text=GENERAL_TEXT_FILE, topic_text=TOPIC_TEXT_FILE, answers_path=ANSWER_FILE):
    while True:
        print_header("Topic Hangman Frequency Lab")
        print("1. Scrape a web page into a text file")
        print("2. Show letter probabilities")
        print("3. Watch the computer play")
        print("4. Compare general vs topic frequency")
        print("5. Quit")

        choice = input("Choose an option: ").strip()

        if choice == "1":
            url = input("Web page URL: ").strip()
            if not url:
                print("Please enter a URL.")
                continue

            output_path = ask_path("Save text file as", topic_text)

            try:
                path, text = scrape_to_file(url, output_path)
            except (HTTPError, URLError, TimeoutError, ValueError) as error:
                print(f"Could not scrape page: {error}")
                continue

            print(f"Saved {len(text)} characters to {path}")
        elif choice == "2":
            try:
                general_model, topic_model, answers = load_default_models(
                    general_text,
                    topic_text,
                    answers_path,
                )
            except (FileNotFoundError, ValueError) as error:
                print(error)
                continue

            show_data_summary(general_model, topic_model, answers, answers_path)
            input("\nPress Enter to return to the menu.")
        elif choice == "3":
            try:
                general_model, topic_model, answers = load_default_models(
                    general_text,
                    topic_text,
                    answers_path,
                )
            except (FileNotFoundError, ValueError) as error:
                print(error)
                continue

            strategy = ask_strategy()
            answer = choose_answer(answers)
            model = topic_model if strategy == "topic" else general_model
            play_game(answer, model, verbose=True)
            input("\nPress Enter to return to the menu.")
        elif choice == "4":
            try:
                general_model, topic_model, answers = load_default_models(
                    general_text,
                    topic_text,
                    answers_path,
                )
            except (FileNotFoundError, ValueError) as error:
                print(error)
                continue

            games = ask_int("How many games should each strategy play?", 20)
            seed = ask_optional_int("Random seed (Enter for random): ")
            compare_models(general_model, topic_model, answers, games, seed, answers_path)
            input("\nPress Enter to return to the menu.")
        elif choice in ["5", "q", "quit", "exit"]:
            print("Goodbye.")
            return
        else:
            print("Please choose a number from 1 to 5.")


def run_from_args(args):
    general_text = Path(args.general_text)
    topic_text = Path(args.topic_text)
    answers_path = Path(args.answers)

    if args.scrape_url:
        output_path = Path(args.out)

        try:
            path, text = scrape_to_file(args.scrape_url, output_path)
        except (HTTPError, URLError, TimeoutError, ValueError) as error:
            raise SystemExit(f"Could not scrape page: {error}")

        print(f"Saved {len(text)} characters to {path}")
        return

    general_model = load_frequency_model(general_text, "general")
    topic_model = load_frequency_model(topic_text, "topic")
    answers = load_answers(answers_path)

    if args.summary:
        show_data_summary(general_model, topic_model, answers, answers_path, args.top)
        return

    if args.compare:
        compare_models(general_model, topic_model, answers, args.games, args.seed, answers_path)
        return

    model = topic_model if args.strategy == "topic" else general_model

    if args.answer:
        answer = clean_answer(args.answer)
        if not answer:
            raise SystemExit("--answer must contain at least one letter")
    else:
        rng = random.Random(args.seed)
        answer = rng.choice(answers)

    play_game(answer, model, verbose=True)


def main():
    if len(sys.argv) == 1:
        menu_loop()
        return

    parser = argparse.ArgumentParser()
    parser.add_argument("--menu", action="store_true", help="open the classroom menu")
    parser.add_argument("--scrape-url", help="download visible text from a web page")
    parser.add_argument("--out", default=str(TOPIC_TEXT_FILE), help="where to save scraped text")
    parser.add_argument("--summary", action="store_true", help="show letter probabilities")
    parser.add_argument("--compare", action="store_true", help="compare general and topic frequency")
    parser.add_argument("--strategy", choices=STRATEGIES, default="topic")
    parser.add_argument("--answer", help="custom answer for the computer to guess")
    parser.add_argument("--games", type=int, default=20)
    parser.add_argument("--seed", type=int, default=None)
    parser.add_argument("--top", type=int, default=10)
    parser.add_argument("--general-text", default=str(GENERAL_TEXT_FILE))
    parser.add_argument("--topic-text", default=str(TOPIC_TEXT_FILE))
    parser.add_argument("--answers", default=str(ANSWER_FILE))
    args = parser.parse_args()

    if args.menu:
        menu_loop(
            general_text=Path(args.general_text),
            topic_text=Path(args.topic_text),
            answers_path=Path(args.answers),
        )
    else:
        run_from_args(args)


if __name__ == "__main__":
    main()
