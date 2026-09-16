import nflreadpy
import polars as pl

from model.src.features import build_features

TEST_SEASONS = [2003, 2011, 2014, 2019, 2024]
TRAIN_SEASONS = [s for s in range(1999, 2026) if s not in TEST_SEASONS]


def build_dataset(seasons: list[int], replayable_ids: set[str]) -> pl.DataFrame:
    feature_tables = []

    for season in seasons:
        pbp = nflreadpy.load_pbp(seasons=season)
        schedules = nflreadpy.load_schedules(seasons=season)
        game_ids = [g for g in schedules["game_id"].unique().to_list() if g in replayable_ids]

        for game_id in game_ids:
            game_plays = pbp.filter(pl.col("game_id") == game_id)
            features = build_features(game_plays, schedules, game_id)
            slim = features.select(
                [
                    "game_id",
                    "play_id",
                    "home_score_diff",
                    "game_seconds_remaining",
                    "is_overtime",
                    "score_time_interaction",
                    "home_team_won",
                ]
            )
            feature_tables.append(slim)

        print(f"Finished season {season} ({len(game_ids)} replayable games)")

    combined = pl.concat(feature_tables)
    return combined.drop_nulls(subset=["game_seconds_remaining"])


if __name__ == "__main__":
    report = pl.read_csv("data/samples/full_validation_report.csv")
    replayable_ids = set(report.filter(pl.col("is_replayable"))["game_id"].to_list())

    train_data = build_dataset(TRAIN_SEASONS, replayable_ids)
    train_data.write_parquet("data/processed/train.parquet")
    print(f"\nTrain set: {train_data.shape[0]} rows")

    test_data = build_dataset(TEST_SEASONS, replayable_ids)
    test_data.write_parquet("data/processed/test.parquet")
    print(f"Test set: {test_data.shape[0]} rows")
