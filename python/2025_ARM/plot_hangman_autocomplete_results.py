from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt

from hangman_autocomplete import load_movie_titles, play_game


THIS_FOLDER = Path(__file__).parent
MOVIE_FILE = THIS_FOLDER / "movie_titles.txt"
OUTPUT_FILE = THIS_FOLDER / "hangman_autocomplete_tries.png"


def main():
    titles = load_movie_titles(MOVIE_FILE)
    results = []

    for title in titles:
        result = play_game(
            answer=title,
            strategy="autocomplete",
            titles=titles,
            rng=None,
            verbose=False,
        )
        results.append(result)

    results.sort(key=lambda result: (result["guess_count"], result["wrong_count"], result["answer"]))

    answers = [result["answer"] for result in results]
    guess_counts = [result["guess_count"] for result in results]
    wrong_counts = [result["wrong_count"] for result in results]

    won = sum(1 for result in results if result["won"])
    average_guesses = sum(guess_counts) / len(guess_counts)
    max_guesses = max(guess_counts)

    figure_height = max(10, len(results) * 0.18)
    fig, ax = plt.subplots(figsize=(12, figure_height))

    y_positions = range(len(results))
    ax.barh(y_positions, guess_counts, color="#4C78A8", label="total letter guesses")
    ax.barh(y_positions, wrong_counts, color="#F58518", label="wrong guesses")

    ax.set_yticks(y_positions)
    ax.set_yticklabels(answers, fontsize=7)
    ax.invert_yaxis()
    ax.set_xlabel("Letter guesses needed to solve")
    ax.grid(axis="x", color="#dddddd", linewidth=0.8)
    ax.set_axisbelow(True)
    ax.legend(loc="lower right")

    subtitle = (
        f"{won}/{len(results)} solved within 6 wrong guesses | "
        f"average guesses: {average_guesses:.1f} | max guesses: {max_guesses}"
    )
    fig.suptitle(
        "Autocomplete Hangman: Guesses Needed for Each Movie",
        fontsize=14,
        y=0.995,
    )
    fig.text(
        0.5,
        0.982,
        subtitle,
        ha="center",
        fontsize=10,
        color="#555555",
    )

    fig.tight_layout(rect=[0, 0, 1, 0.965])
    fig.savefig(OUTPUT_FILE, dpi=200)
    print(f"Wrote {OUTPUT_FILE}")
    print(subtitle)


if __name__ == "__main__":
    main()
