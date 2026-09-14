import polars as pl


def normalize_scores(plays: pl.DataFrame) -> pl.DataFrame:
    plays = plays.sort("play_id")

    return plays.with_columns(
        pl.col("total_home_score").cum_max().alias("total_home_score"),
        pl.col("total_away_score").cum_max().alias("total_away_score"),
    )


def find_score_decreases(plays: pl.DataFrame) -> pl.DataFrame:
    plays = plays.sort("play_id")

    plays = plays.with_columns(
        pl.col("total_home_score").shift(1).alias("prev_home_score"),
        pl.col("total_away_score").shift(1).alias("prev_away_score"),
    )

    return plays.filter(
        (pl.col("total_home_score") < pl.col("prev_home_score"))
        | (pl.col("total_away_score") < pl.col("prev_away_score"))
    )
