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


GAMES = [
    (2023, "2023_22_SF_KC"),   # Super Bowl LVIII, went to OT
    (2022, "2022_01_IND_HOU"),  # real tie, 20-20
    (2023, "2023_01_DET_KC"),
    (2023, "2023_03_TEN_CLE"),
    (2023, "2023_05_TEN_IND"),
    (2023, "2023_07_GB_DEN"),
    (2023, "2023_10_CAR_CHI"),
    (2023, "2023_12_JAX_HOU"),
    (2023, "2023_14_DEN_LAC"),
    (2023, "2023_16_NYG_PHI"),
]

if __name__ == "__main__":
    for season, game_id in GAMES:
        fetch_and_save_game(season, game_id, f"data/samples/game_{game_id}.csv")

    fetch_and_save_schedules(
        seasons=sorted({season for season, _ in GAMES}),
        game_ids=[game_id for _, game_id in GAMES],
        output_path="data/samples/schedules_sample.csv",
    )
