import sys

import nflreadpy
import polars as pl
import psycopg

from model.src.evaluate import load_model
from scripts.import_games import build_game_rows, get_replayable_game_ids
from scripts.load_db import import_game_plays, load_games

ALL_SEASONS = list(range(1999, 2026))
MODEL_VERSION = "logreg-v1"
PBP_COLUMNS = [
    "game_id", "play_id", "desc", "play_type", "qtr",
    "quarter_seconds_remaining", "game_seconds_remaining",
    "total_home_score", "total_away_score",
    "home_timeouts_remaining", "away_timeouts_remaining",
    "posteam", "down", "ydstogo", "yardline_100",
]


def run_import(seasons: list[int]) -> None:
    validation = pl.read_csv("data/samples/full_validation_report.csv")
    schedules = nflreadpy.load_schedules(seasons=seasons)
    model = load_model()

    with psycopg.connect("dbname=snapshift") as connection:
        connection.execute("TRUNCATE games RESTART IDENTITY CASCADE")
        load_games(connection, build_game_rows(schedules, validation))

        for season in seasons:
            plays = nflreadpy.load_pbp(seasons=season).select(PBP_COLUMNS)
            game_ids = get_replayable_game_ids(validation, season)
            import_game_plays(connection, plays, game_ids, model, MODEL_VERSION)
            print(f"Loaded season {season} ({len(game_ids)} games)")


if __name__ == "__main__":
    seasons = [int(arg) for arg in sys.argv[1:]] or ALL_SEASONS
    run_import(seasons)
