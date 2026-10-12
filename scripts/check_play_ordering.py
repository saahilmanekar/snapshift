import nflreadpy
import polars as pl


def check_season(season: int) -> dict:
    plays = (
        nflreadpy.load_pbp(seasons=season)
        .filter(pl.col("play_type").is_not_null())
        .with_row_index("raw_position")
    )

    ranked = plays.with_columns(
        pl.col("raw_position").rank("ordinal").over("game_id").alias("raw_rank"),
        pl.col("play_id").rank("ordinal").over("game_id").alias("play_id_rank"),
        pl.col("order_sequence").rank("ordinal").over("game_id").alias("order_sequence_rank"),
    )

    duplicated = pl.col("order_sequence").is_not_null() & pl.col("order_sequence").is_duplicated().over("game_id")

    return {
        "season": season,
        "rows": ranked.shape[0],
        "null_order_sequence": ranked["order_sequence"].null_count(),
        "duplicate_order_sequence": ranked.filter(duplicated).shape[0],
        "play_id_vs_order_sequence": ranked.filter(pl.col("play_id_rank") != pl.col("order_sequence_rank")).shape[0],
        "raw_vs_order_sequence": ranked.filter(pl.col("raw_rank") != pl.col("order_sequence_rank")).shape[0],
    }


if __name__ == "__main__":
    results = []
    for season in range(1999, 2026):
        results.append(check_season(season))
        print(f"Checked {season}")

    report = pl.DataFrame(results)
    report.write_csv("data/samples/play_ordering_check.csv")
    with pl.Config(tbl_rows=-1, tbl_cols=-1):
        print(report)
