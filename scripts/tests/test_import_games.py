import polars as pl

from scripts.import_games import (
    add_elapsed_replay_seconds,
    add_pre_and_post_scores,
    add_sequence_numbers,
    build_play_rows,
    cast_to_integers,
    drop_plays_without_clock,
    rename_to_table_columns,
)


def load_real_plays() -> pl.DataFrame:
    plays = pl.read_csv("data/samples/game_2023_22_SF_KC.csv")
    return plays.filter(pl.col("play_type").is_not_null())


def test_sequence_numbers_count_up_from_one_in_row_order():
    numbered = add_sequence_numbers(load_real_plays())

    assert numbered["sequence_number"].to_list() == list(range(1, 202))
    assert numbered["play_id"].to_list() == load_real_plays()["play_id"].to_list()


def test_a_timeout_comes_before_the_snap_even_though_its_play_id_is_bigger():
    numbered = add_sequence_numbers(load_real_plays())

    sequence = dict(zip(numbered["play_id"], numbered["sequence_number"]))

    assert sequence[1838.0] < sequence[1826.0]


def test_elapsed_seconds_count_up_from_kickoff_across_quarters():
    plays = pl.DataFrame(
        {
            "qtr": [1.0, 1.0, 2.0],
            "quarter_seconds_remaining": [900.0, 600.0, 900.0],
        }
    )

    result = add_elapsed_replay_seconds(plays)

    assert result["elapsed_replay_seconds"].to_list() == [0, 300, 900]


def test_a_600_second_overtime_starts_at_3600_seconds():
    plays = pl.DataFrame(
        {
            "qtr": [4.0, 5.0, 5.0],
            "quarter_seconds_remaining": [0.0, 600.0, 300.0],
        }
    )

    result = add_elapsed_replay_seconds(plays)

    assert result["elapsed_replay_seconds"].to_list() == [3600, 3600, 3900]


def test_a_play_with_no_game_clock_is_dropped():
    plays = pl.DataFrame(
        {
            "play_id": [1.0, 2.0, 3.0],
            "quarter_seconds_remaining": [900.0, None, 600.0],
            "game_seconds_remaining": [3600.0, None, 3300.0],
        }
    )

    result = drop_plays_without_clock(plays)

    assert result["play_id"].to_list() == [1.0, 3.0]


def test_nflverse_columns_are_renamed_to_our_table_columns():
    plays = pl.DataFrame(
        {
            "qtr": [2],
            "play_id": [1211],
            "desc": ["Timeout #1"],
            "posteam": ["CHI"],
            "ydstogo": [10],
        }
    )

    result = rename_to_table_columns(plays)

    assert result.columns == [
        "quarter",
        "source_play_id",
        "description",
        "possession_team",
        "yards_to_go",
    ]
    assert result["source_play_id"].to_list() == [1211]


def test_pre_score_is_the_previous_plays_post_score():
    plays = pl.DataFrame(
        {
            "total_home_score": [0, 0, 7],
            "total_away_score": [0, 3, 3],
        }
    )

    result = add_pre_and_post_scores(plays)

    assert result["home_score_pre"].to_list() == [0, 0, 0]
    assert result["home_score_post"].to_list() == [0, 0, 7]
    assert result["away_score_pre"].to_list() == [0, 0, 3]
    assert result["away_score_post"].to_list() == [0, 3, 3]


def test_decimal_number_columns_become_whole_numbers_and_empty_stays_empty():
    plays = pl.DataFrame(
        {
            "quarter": [2.0, 3.0],
            "down": [3.0, None],
            "description": ["a pass", "a kickoff"],
        }
    )

    result = cast_to_integers(plays)

    assert result["quarter"].dtype == pl.Int64
    assert result["quarter"].to_list() == [2, 3]
    assert result["down"].to_list() == [3, None]
    assert result["description"].to_list() == ["a pass", "a kickoff"]


def test_build_play_rows_turns_a_raw_game_into_table_shaped_rows():
    raw = load_real_plays().with_columns(
        pl.lit(3.0).alias("home_timeouts_remaining"),
        pl.lit(3.0).alias("away_timeouts_remaining"),
    )

    rows = build_play_rows(raw)

    assert rows.columns == [
        "game_id",
        "sequence_number",
        "source_play_id",
        "quarter",
        "quarter_seconds_remaining",
        "game_seconds_remaining",
        "elapsed_replay_seconds",
        "description",
        "play_type",
        "home_score_pre",
        "away_score_pre",
        "home_score_post",
        "away_score_post",
        "home_timeouts_remaining",
        "away_timeouts_remaining",
        "possession_team",
        "down",
        "yards_to_go",
        "yardline_100",
    ]
    assert rows.height == 201
    assert rows["sequence_number"].to_list() == list(range(1, 202))
    assert rows["home_score_post"][-1] == 25
    assert rows["away_score_post"][-1] == 22
