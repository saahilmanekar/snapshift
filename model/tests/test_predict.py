import polars as pl
import pytest

from model.src.evaluate import load_model
from model.src.predict import add_win_probability


def test_win_probability_is_half_when_tied_and_high_when_home_leads_by_seven():
    model = {
        "intercept": 0.0,
        "coefficients": {
            "home_score_diff": 0.5,
            "game_seconds_remaining": 0.0,
            "is_overtime": 0.0,
            "score_time_interaction": 0.0,
        },
    }
    rows = pl.DataFrame(
        {
            "quarter": [1, 1],
            "game_seconds_remaining": [3600, 3000],
            "home_score_pre": [0, 7],
            "away_score_pre": [0, 0],
        }
    )

    result = add_win_probability(rows, model)

    assert result["win_prob_home"][0] == pytest.approx(0.5)
    assert result["win_prob_home"][1] == pytest.approx(0.9707, abs=1e-4)
    assert result["home_score_pre"].to_list() == [0, 7]


def test_the_real_model_gives_sensible_probabilities():
    model = load_model()
    rows = pl.DataFrame(
        {
            "quarter": [1, 4, 4],
            "game_seconds_remaining": [3600, 60, 60],
            "home_score_pre": [0, 28, 7],
            "away_score_pre": [0, 7, 28],
        }
    )

    result = add_win_probability(rows, model)
    kickoff, home_far_ahead, home_far_behind = result["win_prob_home"].to_list()

    assert 0.5 < kickoff < 0.65
    assert home_far_ahead > 0.95
    assert home_far_behind < 0.05
