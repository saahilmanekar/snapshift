import polars as pl


def normalize_scores(plays: pl.DataFrame) -> pl.DataFrame:
    plays = plays.sort("play_id")

    return plays.with_columns(
        pl.col("total_home_score").cum_max().alias("total_home_score"),
        pl.col("total_away_score").cum_max().alias("total_away_score"),
    )


def final_score_matches(
    plays: pl.DataFrame, expected_home_score: float, expected_away_score: float
) -> bool:
    plays = plays.sort("play_id")
    final_play = plays[-1]

    home_score = final_play["total_home_score"].item()
    away_score = final_play["total_away_score"].item()

    return home_score == expected_home_score and away_score == expected_away_score


def is_tied_game(plays: pl.DataFrame) -> bool:
    plays = plays.sort("play_id")
    final_play = plays[-1]

    home_score = final_play["total_home_score"].item()
    away_score = final_play["total_away_score"].item()

    return home_score == away_score


def get_official_final_score(schedules: pl.DataFrame, game_id: str) -> tuple[float, float]:
    game_row = schedules.filter(pl.col("game_id") == game_id)
    home_score = game_row["home_score"].item()
    away_score = game_row["away_score"].item()
    return home_score, away_score


def validate_game(plays: pl.DataFrame, schedules: pl.DataFrame, game_id: str) -> dict:
    real_plays = plays.filter(pl.col("play_type").is_not_null())
    normalized = normalize_scores(real_plays)

    score_never_decreases = find_score_decreases(normalized).shape[0] == 0
    no_duplicate_play_ids = find_duplicate_play_ids(real_plays).shape[0] == 0
    tied = is_tied_game(normalized)

    expected_home_score, expected_away_score = get_official_final_score(schedules, game_id)
    score_matches = final_score_matches(normalized, expected_home_score, expected_away_score)

    is_valid = score_never_decreases and score_matches and no_duplicate_play_ids

    return {
        "game_id": game_id,
        "score_never_decreases": score_never_decreases,
        "final_score_matches": score_matches,
        "no_duplicate_play_ids": no_duplicate_play_ids,
        "is_tied": tied,
        "is_valid": is_valid,
        "is_replayable": is_valid and not tied,
    }


def find_duplicate_play_ids(plays: pl.DataFrame) -> pl.DataFrame:
    return plays.filter(pl.col("play_id").is_duplicated())


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
