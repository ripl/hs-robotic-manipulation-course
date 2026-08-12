import argparse
import csv
import gzip
from pathlib import Path
from urllib.request import Request, urlopen


LETTERS = "abcdefghijklmnopqrstuvwxyz"
IMDB_TITLE_BASICS_URL = "https://datasets.imdbws.com/title.basics.tsv.gz"
IMDB_TITLE_RATINGS_URL = "https://datasets.imdbws.com/title.ratings.tsv.gz"
DEFAULT_OUTPUT = Path(__file__).parent / "movie_titles_large.txt"


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


def parse_year(value):
    if value == r"\N":
        return None

    try:
        return int(value)
    except ValueError:
        return None


def keep_row(row, min_year, max_year, include_adult):
    if row["titleType"] != "movie":
        return False
    if not include_adult and row["isAdult"] == "1":
        return False

    year = parse_year(row["startYear"])
    if year is None:
        return False
    if min_year is not None and year < min_year:
        return False
    if max_year is not None and year > max_year:
        return False

    return True


def download_vote_counts(min_votes):
    request = Request(
        IMDB_TITLE_RATINGS_URL,
        headers={"User-Agent": "HangmanMovieTitleBuilder/1.0"},
    )
    vote_counts = {}

    with urlopen(request) as response:
        with gzip.open(response, mode="rt", encoding="utf-8", newline="") as file:
            rows = csv.DictReader(file, delimiter="\t")

            for row in rows:
                votes = int(row["numVotes"])
                if votes >= min_votes:
                    vote_counts[row["tconst"]] = votes

    return vote_counts


def download_movie_titles(limit, min_year, max_year, include_adult, min_votes):
    vote_counts = download_vote_counts(min_votes)
    request = Request(
        IMDB_TITLE_BASICS_URL,
        headers={"User-Agent": "HangmanMovieTitleBuilder/1.0"},
    )
    candidates = []
    seen = set()

    with urlopen(request) as response:
        with gzip.open(response, mode="rt", encoding="utf-8", newline="") as file:
            rows = csv.DictReader(file, delimiter="\t")

            for row in rows:
                title_id = row["tconst"]
                if title_id not in vote_counts:
                    continue
                if not keep_row(row, min_year, max_year, include_adult):
                    continue

                title = clean_title(row["primaryTitle"])
                if not title or title in seen:
                    continue

                seen.add(title)
                candidates.append((vote_counts[title_id], title))

    candidates.sort(reverse=True)
    return [title for votes, title in candidates[:limit]]

def write_titles(path, titles, min_votes):
    path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, "w", encoding="utf-8") as file:
        file.write("# Built from IMDb Non-Commercial Datasets.\n")
        file.write("# See: https://developer.imdb.com/non-commercial-datasets/\n")
        file.write("# Use subject to IMDb non-commercial data terms.\n")
        file.write(f"# Sorted by IMDb numVotes, with at least {min_votes} votes.\n")
        for title in titles:
            file.write(title + "\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=5000)
    parser.add_argument("--min-year", type=int, default=1970)
    parser.add_argument("--max-year", type=int, default=None)
    parser.add_argument("--min-votes", type=int, default=10000)
    parser.add_argument("--include-adult", action="store_true")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    if args.limit < 1:
        raise SystemExit("--limit must be at least 1")

    titles = download_movie_titles(
        limit=args.limit,
        min_year=args.min_year,
        max_year=args.max_year,
        include_adult=args.include_adult,
        min_votes=args.min_votes,
    )
    write_titles(args.output, titles, args.min_votes)
    print(f"Wrote {len(titles)} movie titles to {args.output}")


if __name__ == "__main__":
    main()
