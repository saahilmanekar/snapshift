from datetime import date

import polars as pl

from model.src.evaluate import load_model
from model.src.predict import add_win_probability
from scripts.import_games import build_play_rows
from scripts.load_db import import_game_plays, load_games, load_plays, load_predictions


def test_load_games_inserts_one_row_per_game(db):
    games = pl.DataFrame(
        {
            "id": ["2023_01_DET_KC", "2023_22_SF_KC"],
            "season": [2023, 2023],
            "week": [1, 22],
            "season_type": ["REG", "POST"],
            "game_date": [date(2023, 9, 7), date(2024, 2, 11)],
            "home_team": ["KC", "KC"],
            "away_team": ["DET", "SF"],
            "home_final_score": [20, 25],
            "away_final_score": [21, 22],
            "is_valid": [True, True],
            "is_replayable": [True, False],
        }
    )

    load_games(db, games)

    rows = db.execute(
        "SELECT id, season_type, home_final_score, is_replayable FROM games ORDER BY id"
    ).fetchall()
    assert rows == [
        ("2023_01_DET_KC", "REG", 20, True),
        ("2023_22_SF_KC", "POST", 25, False),
    ]


def insert_game(db, game_id):
    load_games(
        db,
        pl.DataFrame(
            {
                "id": [game_id],
                "season": [2023],
                "week": [22],
                "season_type": ["POST"],
                "game_date": [date(2024, 2, 11)],
                "home_team": ["KC"],
                "away_team": ["SF"],
                "home_final_score": [25],
                "away_final_score": [22],
                "is_valid": [True],
                "is_replayable": [True],
            }
        ),
    )


def test_load_plays_inserts_one_row_per_play(db):
    insert_game(db, "2023_22_SF_KC")
    raw = pl.read_csv("data/samples/game_2023_22_SF_KC.csv").with_columns(
        pl.lit(3.0).alias("home_timeouts_remaining"),
        pl.lit(3.0).alias("away_timeouts_remaining"),
    )
    plays = build_play_rows(raw)

    load_plays(db, plays)

    count = db.execute(
        "SELECT count(*) FROM plays WHERE game_id = %s", ("2023_22_SF_KC",)
    ).fetchone()[0]
    assert count == 201

    last = db.execute(
        "SELECT home_score_post, away_score_post FROM plays "
        "WHERE game_id = %s ORDER BY sequence_number DESC LIMIT 1",
        ("2023_22_SF_KC",),
    ).fetchone()
    assert last == (25, 22)


def test_load_predictions_links_each_probability_to_its_play(db):
    insert_game(db, "2023_22_SF_KC")
    raw = pl.read_csv("data/samples/game_2023_22_SF_KC.csv").with_columns(
        pl.lit(3.0).alias("home_timeouts_remaining"),
        pl.lit(3.0).alias("away_timeouts_remaining"),
    )
    plays = build_play_rows(raw)
    load_plays(db, plays)
    with_probs = add_win_probability(plays, load_model())

    load_predictions(db, with_probs, "logreg-v1")

    count = db.execute(
        "SELECT count(*) FROM predictions "
        "JOIN plays ON predictions.play_id = plays.id "
        "WHERE plays.game_id = %s",
        ("2023_22_SF_KC",),
    ).fetchone()[0]
    assert count == 201

    kickoff_prob = db.execute(
        "SELECT win_prob_home FROM predictions "
        "JOIN plays ON predictions.play_id = plays.id "
        "WHERE plays.game_id = %s AND plays.sequence_number = 1",
        ("2023_22_SF_KC",),
    ).fetchone()[0]
    assert 0.5 < kickoff_prob < 0.65


def test_import_game_plays_only_loads_replayable_games(db):
    insert_game(db, "2023_22_SF_KC")
    raw = pl.concat(
        [
            pl.read_csv("data/samples/game_2023_22_SF_KC.csv"),
            pl.read_csv("data/samples/game_2022_01_IND_HOU.csv"),
        ]
    ).with_columns(
        pl.lit(3.0).alias("home_timeouts_remaining"),
        pl.lit(3.0).alias("away_timeouts_remaining"),
    )

    import_game_plays(db, raw, ["2023_22_SF_KC"], load_model(), "logreg-v1")

    per_game = db.execute(
        "SELECT game_id, count(*) FROM plays GROUP BY game_id"
    ).fetchall()
    assert per_game == [("2023_22_SF_KC", 201)]

    predictions = db.execute("SELECT count(*) FROM predictions").fetchone()[0]
    assert predictions == 201
