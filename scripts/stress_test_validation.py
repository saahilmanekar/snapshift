import nflreadpy
import polars as pl

from scripts.validate_pbp import validate_game

NEW_GAMES = [
    (2003, "2003_02_CAR_TB"),
    (2010, "2010_01_ATL_PIT"),
    (2015, "2015_01_SEA_STL"),
    (2008, "2008_11_PHI_CIN"),
    (2019, "2019_01_IND_LAC"),
    (1999, "1999_21_STL_TEN"),
    (2000, "2000_21_BAL_NYG"),
    (2003, "2003_21_CAR_NE"),
    (2010, "2010_21_PIT_GB"),
    (2015, "2015_21_CAR_DEN"),
    (2019, "2019_21_SF_KC"),
]


def check_games(games: list[tuple[int, str]]) -> pl.DataFrame:
    seasons = sorted({season for season, _ in games})

    pbp = nflreadpy.load_pbp(seasons=seasons)
    schedules = nflreadpy.load_schedules(seasons=seasons)

    results = []
    for season, game_id in games:
        game_plays = pbp.filter(pl.col("game_id") == game_id)
        results.append(validate_game(game_plays, schedules, game_id))

    return pl.DataFrame(results)


if __name__ == "__main__":
    report = check_games(NEW_GAMES)
    report.write_csv("data/samples/stress_test_report.csv")
    print(report)
