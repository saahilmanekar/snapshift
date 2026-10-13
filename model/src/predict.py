import polars as pl

from model.src.evaluate import predict_home_win_prob
from model.src.features import (
    compute_is_overtime,
    compute_score_diff,
    compute_score_time_interaction,
)
from model.src.train import FEATURE_COLS


def add_win_probability(rows: pl.DataFrame, model: dict) -> pl.DataFrame:
    features = rows.rename({"quarter": "qtr"})
    features = compute_score_diff(features)
    features = compute_score_time_interaction(features)
    features = compute_is_overtime(features)

    probabilities = predict_home_win_prob(model, features.select(FEATURE_COLS).to_numpy())

    return rows.with_columns(pl.Series("win_prob_home", probabilities))
