import numpy as np
import pytest

from model.src.evaluate import predict_home_win_prob
from model.src.train import FEATURE_COLS


def make_model(intercept: float, **coefficients: float) -> dict:
    return {
        "intercept": intercept,
        "coefficients": {name: coefficients.get(name, 0.0) for name in FEATURE_COLS},
    }


def test_zero_inputs_and_zero_intercept_give_fifty_fifty():
    model = make_model(0.0)

    probs = predict_home_win_prob(model, np.zeros((1, 4)))

    assert probs[0] == 0.5


def test_sigmoid_matches_a_hand_computed_value():
    model = make_model(0.0, home_score_diff=1.0)
    X = np.array([[np.log(3), 0.0, 0.0, 0.0]])

    probs = predict_home_win_prob(model, X)

    assert probs[0] == pytest.approx(0.75)
