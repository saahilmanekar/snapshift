import polars as pl

from model.src.features import compute_pre_play_scores


def test_first_play_has_zero_pre_play_score():
    plays = pl.read_csv("data/samples/game_2023_22_SF_KC.csv")
    real_plays = plays.filter(pl.col("play_type").is_not_null())

    with_pre_scores = compute_pre_play_scores(real_plays)

    first_play = with_pre_scores.sort("play_id")[0]
    assert first_play["home_score_pre"].item() == 0
    assert first_play["away_score_pre"].item() == 0
