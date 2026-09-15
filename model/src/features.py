import polars as pl


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
