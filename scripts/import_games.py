import polars as pl


def add_sequence_numbers(plays: pl.DataFrame) -> pl.DataFrame:
    return plays.with_row_index("sequence_number", offset=1)


def add_elapsed_replay_seconds(plays: pl.DataFrame) -> pl.DataFrame:
    return plays.with_columns(
        ((pl.col("qtr") - 1) * 900 + (900 - pl.col("quarter_seconds_remaining")))
        .cast(pl.Int64)
        .alias("elapsed_replay_seconds")
    )
