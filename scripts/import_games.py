import polars as pl


def drop_plays_without_clock(plays: pl.DataFrame) -> pl.DataFrame:
    return plays.drop_nulls(subset=["quarter_seconds_remaining", "game_seconds_remaining"])


def add_sequence_numbers(plays: pl.DataFrame) -> pl.DataFrame:
    return plays.with_row_index("sequence_number", offset=1)


def add_elapsed_replay_seconds(plays: pl.DataFrame) -> pl.DataFrame:
    qtr = pl.col("qtr")
    seconds_left = pl.col("quarter_seconds_remaining")
    overtime_length = seconds_left.filter(qtr >= 5).max()

    regulation = (qtr - 1) * 900 + (900 - seconds_left)
    overtime = 3600 + (qtr - 5) * overtime_length + (overtime_length - seconds_left)

    return plays.with_columns(
        pl.when(qtr <= 4)
        .then(regulation)
        .otherwise(overtime)
        .cast(pl.Int64)
        .alias("elapsed_replay_seconds")
    )
