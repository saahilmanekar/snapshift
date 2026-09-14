import nflreadpy
import polars as pl

pbp = nflreadpy.load_pbp(seasons=2023)
game = pbp.filter(pl.col("game_id") == "2023_22_SF_KC")

columns_to_keep = [
    "game_id", "play_id", "desc", "play_type",
    "qtr", "quarter_seconds_remaining", "game_seconds_remaining",
    "total_home_score", "total_away_score",
    "home_team", "away_team", "season", "week", "season_type",
    "down", "ydstogo", "yardline_100", "posteam",
    "home_wp", "vegas_home_wp", "home_wp_post",
]
game_slim = game.select(columns_to_keep)

game_slim.write_csv("data/samples/super_bowl_58.csv")
