import polars as pl

from scripts.validate_pbp import (
    find_score_decreases,
    normalize_scores,
    final_score_matches,
    find_duplicate_play_ids,
    is_tied_game,
    get_official_final_score,
    validate_game,
)


def test_no_score_decreases_in_super_bowl_58():
    plays = pl.read_csv("data/samples/game_2023_22_SF_KC.csv")
    real_plays = plays.filter(pl.col("play_type").is_not_null())
    normalized = normalize_scores(real_plays)

    violations = find_score_decreases(normalized)

    assert violations.shape[0] == 0


def test_final_score_matches_super_bowl_58():
    plays = pl.read_csv("data/samples/game_2023_22_SF_KC.csv")
    real_plays = plays.filter(pl.col("play_type").is_not_null())
    normalized = normalize_scores(real_plays)

    schedules = pl.read_csv("data/samples/schedules_sample.csv")
    expected_home_score, expected_away_score = get_official_final_score(schedules, "2023_22_SF_KC")

    assert final_score_matches(normalized, expected_home_score, expected_away_score)


def test_no_duplicate_play_ids_in_super_bowl_58():
    plays = pl.read_csv("data/samples/game_2023_22_SF_KC.csv")
    real_plays = plays.filter(pl.col("play_type").is_not_null())

    duplicates = find_duplicate_play_ids(real_plays)

    assert duplicates.shape[0] == 0


def test_is_tied_game_false_for_super_bowl_58():
    plays = pl.read_csv("data/samples/game_2023_22_SF_KC.csv")
    real_plays = plays.filter(pl.col("play_type").is_not_null())
    normalized = normalize_scores(real_plays)

    assert is_tied_game(normalized) is False


def test_is_tied_game_true_for_2022_tie():
    plays = pl.read_csv("data/samples/game_2022_01_IND_HOU.csv")
    real_plays = plays.filter(pl.col("play_type").is_not_null())
    normalized = normalize_scores(real_plays)

    assert is_tied_game(normalized) is True


def test_get_official_final_score_for_super_bowl_58():
    schedules = pl.read_csv("data/samples/schedules_sample.csv")

    home_score, away_score = get_official_final_score(schedules, "2023_22_SF_KC")

    assert home_score == 25
    assert away_score == 22


def test_validate_game_super_bowl_58():
    plays = pl.read_csv("data/samples/game_2023_22_SF_KC.csv")
    schedules = pl.read_csv("data/samples/schedules_sample.csv")

    result = validate_game(plays, schedules, "2023_22_SF_KC")

    assert result["score_never_decreases"] is True
    assert result["final_score_matches"] is True
    assert result["no_duplicate_play_ids"] is True
    assert result["is_tied"] is False
    assert result["is_valid"] is True
    assert result["is_replayable"] is True


def test_validate_game_tied_2022():
    plays = pl.read_csv("data/samples/game_2022_01_IND_HOU.csv")
    schedules = pl.read_csv("data/samples/schedules_sample.csv")

    result = validate_game(plays, schedules, "2022_01_IND_HOU")

    assert result["is_tied"] is True
    assert result["is_valid"] is True
    assert result["is_replayable"] is False
