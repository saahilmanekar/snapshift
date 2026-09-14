import nflreadpy
import polars as pl

COLUMNS_TO_KEEP = [
    "game_id", "play_id", "desc", "play_type",
    "qtr", "quarter_seconds_remaining", "game_seconds_remaining",
    "total_home_score", "total_away_score",
    "home_team", "away_team", "season", "week", "season_type",
    "down", "ydstogo", "yardline_100", "posteam",
    "home_wp", "vegas_home_wp", "home_wp_post",
]


def fetch_and_save_game(season: int, game_id: str, output_path: str) -> None:
    pbp = nflreadpy.load_pbp(seasons=season)
    game = pbp.filter(pl.col("game_id") == game_id)
    game_slim = game.select(COLUMNS_TO_KEEP)
    game_slim.write_csv(output_path)


def fetch_and_save_schedules(seasons: list[int], game_ids: list[str], output_path: str) -> None:
    schedules = nflreadpy.load_schedules(seasons=seasons)
    schedules_slim = schedules.filter(pl.col("game_id").is_in(game_ids)).select(
        ["game_id", "home_team", "away_team", "home_score", "away_score"]
    )
    schedules_slim.write_csv(output_path)


if __name__ == "__main__":
    fetch_and_save_game(2023, "2023_22_SF_KC", "data/samples/super_bowl_58.csv")
    fetch_and_save_game(2022, "2022_01_IND_HOU", "data/samples/tied_game_2022.csv")

    fetch_and_save_schedules(
        seasons=[2023, 2022],
        game_ids=["2023_22_SF_KC", "2022_01_IND_HOU"],
        output_path="data/samples/schedules_sample.csv",
    )
