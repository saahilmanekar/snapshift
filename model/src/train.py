import json

import polars as pl
from sklearn.linear_model import LogisticRegression

FEATURE_COLS = ["home_score_diff", "game_seconds_remaining", "is_overtime", "score_time_interaction"]


def train_model() -> LogisticRegression:
    train = pl.read_parquet("data/processed/train.parquet")
    X = train.select(FEATURE_COLS).to_numpy()
    y = train["home_team_won"].to_numpy()

    model = LogisticRegression()
    model.fit(X, y)
    return model


def export_model(model: LogisticRegression, path: str) -> None:
    coefficients = dict(zip(FEATURE_COLS, model.coef_[0]))

    export = {
        "intercept": float(model.intercept_[0]),
        "coefficients": {name: float(value) for name, value in coefficients.items()},
    }

    with open(path, "w") as f:
        json.dump(export, f, indent=2)


if __name__ == "__main__":
    model = train_model()
    export_model(model, "model/artifacts/model.json")
    print("Model exported to model/artifacts/model.json")
