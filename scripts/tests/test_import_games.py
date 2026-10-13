import polars as pl

from scripts.import_games import add_elapsed_replay_seconds, add_sequence_numbers


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
