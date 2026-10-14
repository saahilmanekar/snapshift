import polars as pl

from model.src.features import compute_pre_play_scores

INTEGER_COLUMNS = [
    "quarter",
    "source_play_id",
    "quarter_seconds_remaining",
    "game_seconds_remaining",
    "home_score_pre",
    "away_score_pre",
    "home_score_post",
    "away_score_post",
    "home_timeouts_remaining",
    "away_timeouts_remaining",
    "down",
    "yards_to_go",
    "yardline_100",
]

TABLE_COLUMNS = [
    "game_id",
    "sequence_number",
    "source_play_id",
    "quarter",
    "quarter_seconds_remaining",
    "game_seconds_remaining",
    "elapsed_replay_seconds",
    "description",
    "play_type",
    "home_score_pre",
    "away_score_pre",
    "home_score_post",
    "away_score_post",
    "home_timeouts_remaining",
    "away_timeouts_remaining",
    "possession_team",
    "down",
    "yards_to_go",
    "yardline_100",
]


def drop_plays_without_clock(plays: pl.DataFrame) -> pl.DataFrame:
    return plays.drop_nulls(subset=["quarter_seconds_remaining", "game_seconds_remaining"])


def rename_to_table_columns(plays: pl.DataFrame) -> pl.DataFrame:
    return plays.rename(
        {
            "qtr": "quarter",
            "play_id": "source_play_id",
            "desc": "description",
            "posteam": "possession_team",
            "ydstogo": "yards_to_go",
        }
    )


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


def add_pre_and_post_scores(plays: pl.DataFrame) -> pl.DataFrame:
    with_pre_scores = compute_pre_play_scores(plays)
    return with_pre_scores.rename(
        {
            "total_home_score": "home_score_post",
            "total_away_score": "away_score_post",
        }
    )


def cast_to_integers(plays: pl.DataFrame) -> pl.DataFrame:
    columns_to_cast = [name for name in INTEGER_COLUMNS if name in plays.columns]
    return plays.with_columns(pl.col(columns_to_cast).cast(pl.Int64))


def build_play_rows(raw_plays: pl.DataFrame) -> pl.DataFrame:
    plays = raw_plays.filter(pl.col("play_type").is_not_null())
    plays = drop_plays_without_clock(plays)
    plays = add_sequence_numbers(plays)
    plays = add_elapsed_replay_seconds(plays)
    plays = add_pre_and_post_scores(plays)
    plays = rename_to_table_columns(plays)
    plays = cast_to_integers(plays)
    return plays.select(TABLE_COLUMNS)


def build_game_rows(schedules: pl.DataFrame, validation: pl.DataFrame) -> pl.DataFrame:
    flags = validation.select("game_id", "is_valid", "is_replayable")
    games = schedules.join(flags, on="game_id", how="inner")

    return games.select(
        pl.col("game_id").alias("id"),
        "season",
        "week",
        pl.when(pl.col("game_type") == "REG")
        .then(pl.lit("REG"))
        .otherwise(pl.lit("POST"))
        .alias("season_type"),
        pl.col("gameday").cast(pl.String).str.to_date().alias("game_date"),
        "home_team",
        "away_team",
        pl.col("home_score").alias("home_final_score"),
        pl.col("away_score").alias("away_final_score"),
        "is_valid",
        "is_replayable",
    ).sort("id")
