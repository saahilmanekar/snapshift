import polars as pl

from scripts.fetch_sample_game import GAMES
from scripts.validate_pbp import validate_game


def main():
    schedules = pl.read_csv("data/samples/schedules_sample.csv")

    results = []
    for season, game_id in GAMES:
        plays = pl.read_csv(f"data/samples/game_{game_id}.csv")
        results.append(validate_game(plays, schedules, game_id))

    report = pl.DataFrame(results)
    print(report)


if __name__ == "__main__":
    main()
