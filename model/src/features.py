import polars as pl

from scripts.validate_pbp import get_official_final_score


def compute_pre_play_scores(plays: pl.DataFrame) -> pl.DataFrame:
    plays = plays.sort("play_id")

    return plays.with_columns(
        pl.col("total_home_score").shift(1, fill_value=0).alias("home_score_pre"),
        pl.col("total_away_score").shift(1, fill_value=0).alias("away_score_pre"),
    )


def compute_is_overtime(plays: pl.DataFrame) -> pl.DataFrame:
    return plays.with_columns(
        (pl.col("qtr") >= 5).cast(pl.Int64).alias("is_overtime")
    )


def compute_score_diff(plays: pl.DataFrame) -> pl.DataFrame:
    return plays.with_columns(
        (pl.col("home_score_pre") - pl.col("away_score_pre")).alias("home_score_diff")
    )


def compute_score_time_interaction(plays: pl.DataFrame) -> pl.DataFrame:
    return plays.with_columns(
        (pl.col("home_score_diff") * pl.col("game_seconds_remaining")).alias(
            "score_time_interaction"
        )
    )


def compute_home_team_won(
    plays: pl.DataFrame, schedules: pl.DataFrame, game_id: str
) -> pl.DataFrame:
    home_score, away_score = get_official_final_score(schedules, game_id)
    home_team_won = 1 if home_score > away_score else 0

    return plays.with_columns(pl.lit(home_team_won).alias("home_team_won"))
