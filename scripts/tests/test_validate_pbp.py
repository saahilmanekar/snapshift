import polars as pl

from scripts.validate_pbp import find_score_decreases, normalize_scores


def test_no_score_decreases_in_super_bowl_58():
    plays = pl.read_csv("data/samples/super_bowl_58.csv")
    real_plays = plays.filter(pl.col("play_type").is_not_null())
    normalized = normalize_scores(real_plays)

    violations = find_score_decreases(normalized)

    assert violations.shape[0] == 0
