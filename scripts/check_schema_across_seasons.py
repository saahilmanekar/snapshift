import nflreadpy
import polars as pl

REQUIRED_COLUMNS = {
    "game_id", "play_id", "desc", "play_type", "down", "ydstogo", "yardline_100",
    "posteam", "home_team", "away_team", "season", "week", "season_type",
    "qtr", "quarter_seconds_remaining", "game_seconds_remaining",
    "total_home_score", "total_away_score", "home_wp", "vegas_home_wp", "home_wp_post",
}


def check_season(season: int) -> dict:
    pbp = nflreadpy.load_pbp(seasons=season)
    missing_columns = sorted(REQUIRED_COLUMNS - set(pbp.columns))

    def null_pct(column: str) -> float | None:
        if column in missing_columns:
            return None
        return pbp[column].null_count() / pbp.shape[0] * 100

    return {
        "season": season,
        "rows": pbp.shape[0],
        "missing_columns": ", ".join(missing_columns),
        "total_home_score_null_pct": null_pct("total_home_score"),
        "home_wp_null_pct": null_pct("home_wp"),
        "vegas_home_wp_null_pct": null_pct("vegas_home_wp"),
    }


if __name__ == "__main__":
    results = [check_season(season) for season in range(1999, 2026)]
    report = pl.DataFrame(results)
    report.write_csv("data/samples/schema_check_all_seasons.csv")
    print(report)
