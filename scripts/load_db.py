import polars as pl


def load_games(connection, games: pl.DataFrame) -> None:
    sql = """
        INSERT INTO games (
            id, season, week, season_type, game_date, home_team, away_team,
            home_final_score, away_final_score, is_valid, is_replayable
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    with connection.cursor() as cursor:
        cursor.executemany(sql, games.rows())


def load_plays(connection, plays: pl.DataFrame) -> None:
    sql = """
        INSERT INTO plays (
            game_id, sequence_number, source_play_id, quarter,
            quarter_seconds_remaining, game_seconds_remaining, elapsed_replay_seconds,
            description, play_type,
            home_score_pre, away_score_pre, home_score_post, away_score_post,
            home_timeouts_remaining, away_timeouts_remaining,
            possession_team, down, yards_to_go, yardline_100
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    with connection.cursor() as cursor:
        cursor.executemany(sql, plays.rows())


def load_predictions(connection, plays_with_probs: pl.DataFrame, model_version: str) -> None:
    sql = """
        INSERT INTO predictions (play_id, model_version, win_prob_home)
        VALUES (
            (SELECT id FROM plays WHERE game_id = %s AND sequence_number = %s),
            %s,
            %s
        )
    """
    rows = [
        (game_id, sequence_number, model_version, win_prob)
        for game_id, sequence_number, win_prob in plays_with_probs.select(
            "game_id", "sequence_number", "win_prob_home"
        ).rows()
    ]
    with connection.cursor() as cursor:
        cursor.executemany(sql, rows)
