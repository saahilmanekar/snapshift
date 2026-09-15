import polars as pl

from model.src.features import (
    compute_pre_play_scores,
    compute_is_overtime,
    compute_score_diff,
    compute_score_time_interaction,
    compute_home_team_won,
    build_features,
)


def test_first_play_has_zero_pre_play_score():
    plays = pl.read_csv("data/samples/game_2023_22_SF_KC.csv")
    real_plays = plays.filter(pl.col("play_type").is_not_null())

    with_pre_scores = compute_pre_play_scores(real_plays)

    first_play = with_pre_scores.sort("play_id")[0]
    assert first_play["home_score_pre"].item() == 0
    assert first_play["away_score_pre"].item() == 0


def test_pre_play_score_reflects_prior_scoring_play():
    plays = pl.read_csv("data/samples/game_2023_22_SF_KC.csv")
    real_plays = plays.filter(pl.col("play_type").is_not_null())

    with_pre_scores = compute_pre_play_scores(real_plays)

    next_play = with_pre_scores.filter(pl.col("play_id") == 916.0)
    assert next_play["home_score_pre"].item() == 0
    assert next_play["away_score_pre"].item() == 3


def test_is_overtime_flag():
    plays = pl.read_csv("data/samples/game_2023_22_SF_KC.csv")
    real_plays = plays.filter(pl.col("play_type").is_not_null())

    with_ot_flag = compute_is_overtime(real_plays)

    q4_play = with_ot_flag.filter(pl.col("play_id") == 3064.0)
    assert q4_play["is_overtime"].item() == 0

    ot_play = with_ot_flag.filter(pl.col("play_id") == 4121.0)
    assert ot_play["is_overtime"].item() == 1


def test_home_score_diff():
    plays = pl.read_csv("data/samples/game_2023_22_SF_KC.csv")
    real_plays = plays.filter(pl.col("play_type").is_not_null())

    with_pre_scores = compute_pre_play_scores(real_plays)
    with_diff = compute_score_diff(with_pre_scores)

    play = with_diff.filter(pl.col("play_id") == 916.0)
    assert play["home_score_diff"].item() == -3


def test_score_time_interaction():
    plays = pl.read_csv("data/samples/game_2023_22_SF_KC.csv")
    real_plays = plays.filter(pl.col("play_type").is_not_null())

    with_pre_scores = compute_pre_play_scores(real_plays)
    with_diff = compute_score_diff(with_pre_scores)
    with_interaction = compute_score_time_interaction(with_diff)

    play = with_interaction.filter(pl.col("play_id") == 916.0)
    assert play["score_time_interaction"].item() == -8064


def test_home_team_won_label():
    plays = pl.read_csv("data/samples/game_2023_22_SF_KC.csv")
    real_plays = plays.filter(pl.col("play_type").is_not_null())
    schedules = pl.read_csv("data/samples/schedules_sample.csv")

    with_label = compute_home_team_won(real_plays, schedules, "2023_22_SF_KC")

    assert (with_label["home_team_won"] == 1).all()


def test_build_features_produces_all_columns():
    plays = pl.read_csv("data/samples/game_2023_22_SF_KC.csv")
    schedules = pl.read_csv("data/samples/schedules_sample.csv")

    features = build_features(plays, schedules, "2023_22_SF_KC")

    assert features.shape[0] == 201
    expected_columns = [
        "home_score_pre",
        "away_score_pre",
        "home_score_diff",
        "score_time_interaction",
        "is_overtime",
        "home_team_won",
    ]
    for col in expected_columns:
        assert col in features.columns
