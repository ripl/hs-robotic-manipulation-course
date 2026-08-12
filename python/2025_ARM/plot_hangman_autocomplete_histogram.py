from collections import Counter
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator

from hangman_autocomplete import MAX_WRONG_GUESSES, load_movie_titles, play_game


THIS_FOLDER = Path(__file__).parent
MOVIE_FILE = THIS_FOLDER / "movie_titles.txt"
OUTPUT_FILE = THIS_FOLDER / "hangman_autocomplete_histogram.png"


def main():
    titles = load_movie_titles(MOVIE_FILE)
    mistake_counts = []

    for title in titles:
        result = play_game(
            answer=title,
            strategy="autocomplete",
            titles=titles,
            rng=None,
            verbose=False,
        )
        mistake_counts.append(result["wrong_count"])

    counts = Counter(mistake_counts)
    max_mistakes = max(26, max(mistake_counts) + 1)
    x_values = list(range(max_mistakes + 1))
    y_values = [counts.get(x, 0) for x in x_values]

    wins = sum(count for mistakes, count in counts.items() if mistakes < MAX_WRONG_GUESSES)
    losses = len(mistake_counts) - wins

    fig = plt.figure(figsize=(16, 9), facecolor="white")
    ax = fig.add_axes([0.10, 0.18, 0.84, 0.64])

    ax.bar(
        x_values,
        y_values,
        width=0.78,
        color="#4285F4",
        edgecolor="#4285F4",
        linewidth=0,
        zorder=3,
    )

    ax.axvline(
        MAX_WRONG_GUESSES,
        color="red",
        linewidth=3.5,
        zorder=4,
    )

    y_top = 115
    ax.text(
        1.3,
        y_top * 0.70,
        "Wins",
        color="red",
        fontsize=32,
        fontweight="bold",
    )
    ax.text(
        7.6,
        y_top * 0.70,
        "Losses",
        color="red",
        fontsize=32,
        fontweight="bold",
    )

    fig.text(
        0.06,
        0.88,
        "Histogram of Autocomplete",
        fontsize=34,
        color="#777777",
        ha="left",
        va="center",
    )
    ax.set_xlabel("Number of Mistakes", fontsize=22, labelpad=28)
    ax.set_xlim(0, max_mistakes)
    ax.set_ylim(0, y_top)
    ax.set_xticks(x_values)
    ax.tick_params(axis="x", labelsize=20, length=0, pad=8)
    ax.tick_params(axis="y", labelsize=20, length=0, pad=8)

    ax.yaxis.set_major_locator(MultipleLocator(10))
    ax.yaxis.set_minor_locator(MultipleLocator(5))
    ax.grid(axis="y", which="major", color="#cfcfcf", linewidth=1.6)
    ax.grid(axis="y", which="minor", color="#e6e6e6", linewidth=1.2)
    ax.set_axisbelow(True)

    for side in ["top", "right"]:
        ax.spines[side].set_visible(False)
    ax.spines["left"].set_visible(False)
    ax.spines["bottom"].set_color("#333333")
    ax.spines["bottom"].set_linewidth(1.5)

    fig.savefig(OUTPUT_FILE, dpi=200)
    print(f"Wrote {OUTPUT_FILE}")
    print(f"{wins}/{len(mistake_counts)} wins, {losses} losses")
    print(f"Histogram counts: {dict(sorted(counts.items()))}")


if __name__ == "__main__":
    main()
