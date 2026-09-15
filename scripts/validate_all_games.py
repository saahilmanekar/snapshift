import nflreadpy
import polars as pl

from scripts.validate_pbp import validate_game

SEASONS = list(range(1999, 2026))


def validate_all_games() -> pl.DataFrame:
    results = []

    for season in SEASONS:
        pbp = nflreadpy.load_pbp(seasons=season)
        schedules = nflreadpy.load_schedules(seasons=season)
        game_ids = schedules["game_id"].unique().to_list()

        for game_id in game_ids:
            game_plays = pbp.filter(pl.col("game_id") == game_id)
            results.append(validate_game(game_plays, schedules, game_id))

        print(f"Finished season {season} ({len(game_ids)} games)")

    return pl.DataFrame(results)


if __name__ == "__main__":
    report = validate_all_games()
    report.write_csv("data/samples/full_validation_report.csv")

    print(f"\nTotal games checked: {report.shape[0]}")
    print(f"Valid: {report['is_valid'].sum()}")
    print(f"Replayable: {report['is_replayable'].sum()}")
    print(f"Tied: {report['is_tied'].sum()}")
    print(f"Score never decreases failures: {(~report['score_never_decreases']).sum()}")
    print(f"Final score mismatches: {(~report['final_score_matches']).sum()}")
    print(f"Duplicate play_id failures: {(~report['no_duplicate_play_ids']).sum()}")
