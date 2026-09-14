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


if __name__ == "__main__":
    fetch_and_save_game(2023, "2023_22_SF_KC", "data/samples/super_bowl_58.csv")
    fetch_and_save_game(2022, "2022_01_IND_HOU", "data/samples/tied_game_2022.csv")
