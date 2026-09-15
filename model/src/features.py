import polars as pl


def compute_pre_play_scores(plays: pl.DataFrame) -> pl.DataFrame:
    plays = plays.sort("play_id")

    return plays.with_columns(
        pl.col("total_home_score").shift(1, fill_value=0).alias("home_score_pre"),
        pl.col("total_away_score").shift(1, fill_value=0).alias("away_score_pre"),
    )
