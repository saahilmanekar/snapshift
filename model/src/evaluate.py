import json

import nflreadpy
import numpy as np
import polars as pl
from sklearn.metrics import brier_score_loss, log_loss

from model.src.build_dataset import TEST_SEASONS
from model.src.train import FEATURE_COLS


def load_model(path: str = "model/artifacts/model.json") -> dict:
    with open(path) as f:
        return json.load(f)


def predict_home_win_prob(model: dict, X: np.ndarray) -> np.ndarray:
    weights = np.array([model["coefficients"][name] for name in FEATURE_COLS])
    z = X @ weights + model["intercept"]
    return 1 / (1 + np.exp(-z))


def load_eval_data() -> pl.DataFrame:
    test = pl.read_parquet("data/processed/test.parquet")
    reference = pl.concat(
        [
            nflreadpy.load_pbp(seasons=s).select(
                ["game_id", "play_id", "qtr", "home_wp", "vegas_home_wp"]
            )
            for s in TEST_SEASONS
        ]
    )
    joined = test.join(reference, on=["game_id", "play_id"])
    return joined.with_columns(pl.col("game_id").str.slice(0, 4).cast(pl.Int64).alias("season"))


def score(y: np.ndarray, p: np.ndarray) -> str:
    return f"Brier {brier_score_loss(y, p):.4f}   Log loss {log_loss(y, p):.4f}"


def main() -> None:
    model = load_model()
    data = load_eval_data()

    our_prob = predict_home_win_prob(model, data.select(FEATURE_COLS).to_numpy())
    data = data.with_columns(pl.Series("our_prob", our_prob))

    regulation = data.filter(pl.col("qtr") <= 4)
    overtime = data.filter(pl.col("qtr") >= 5)

    print(f"Test seasons: {TEST_SEASONS}")

    print(f"\n== All test plays, regulation + OT ({data.shape[0]} plays) ==")
    print("ours:", score(data["home_team_won"], data["our_prob"]))

    print("\n== Reliability, all test plays ==")
    reliability = (
        data.with_columns((pl.col("our_prob") * 10).floor().clip(0, 9).cast(pl.Int64).alias("bucket"))
        .group_by("bucket")
        .agg(
            pl.col("our_prob").mean().alias("avg_predicted"),
            pl.col("home_team_won").mean().alias("actual_win_rate"),
            pl.len().alias("count"),
        )
        .sort("bucket")
    )
    print(reliability)

    print(f"\n== Regulation only, vs nflfastR ({regulation.shape[0]} plays) ==")
    y = regulation["home_team_won"]
    print("ours         :", score(y, regulation["our_prob"]))
    print("home_wp      :", score(y, regulation["home_wp"]))
    print("vegas_home_wp:", score(y, regulation["vegas_home_wp"]))

    print(f"\n== Overtime only, self-evaluation ({overtime.shape[0]} plays) ==")
    print("ours:", score(overtime["home_team_won"], overtime["our_prob"]))

    print("\n== Regulation Brier by season, ours vs home_wp ==")
    for season in sorted(regulation["season"].unique().to_list()):
        part = regulation.filter(pl.col("season") == season)
        ours = brier_score_loss(part["home_team_won"], part["our_prob"])
        theirs = brier_score_loss(part["home_team_won"], part["home_wp"])
        print(f"{season}: ours {ours:.4f}   nflfastR {theirs:.4f}   gap {ours - theirs:.4f}")


if __name__ == "__main__":
    main()
