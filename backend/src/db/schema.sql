CREATE TABLE IF NOT EXISTS games (
    id               TEXT PRIMARY KEY,
    season           SMALLINT NOT NULL,
    week             SMALLINT NOT NULL,
    season_type      TEXT NOT NULL,
    game_date        DATE NOT NULL,
    home_team        TEXT NOT NULL,
    away_team        TEXT NOT NULL,
    home_final_score SMALLINT NOT NULL,
    away_final_score SMALLINT NOT NULL,
    is_valid         BOOLEAN NOT NULL,
    is_replayable    BOOLEAN NOT NULL
);

CREATE TABLE IF NOT EXISTS plays (
    id                        BIGSERIAL PRIMARY KEY,
    game_id                   TEXT NOT NULL REFERENCES games(id),
    sequence_number           INTEGER NOT NULL,
    source_play_id            INTEGER NOT NULL,
    quarter                   SMALLINT NOT NULL,
    quarter_seconds_remaining SMALLINT NOT NULL,
    game_seconds_remaining    SMALLINT NOT NULL,
    elapsed_replay_seconds    INTEGER NOT NULL,
    description               TEXT NOT NULL,
    play_type                 TEXT NOT NULL,
    home_score_pre            SMALLINT NOT NULL,
    away_score_pre            SMALLINT NOT NULL,
    home_score_post           SMALLINT NOT NULL,
    away_score_post           SMALLINT NOT NULL,
    home_timeouts_remaining   SMALLINT,
    away_timeouts_remaining   SMALLINT,
    possession_team           TEXT,
    down                      SMALLINT,
    yards_to_go               SMALLINT,
    yardline_100              SMALLINT,
    UNIQUE (game_id, sequence_number)
);

CREATE TABLE IF NOT EXISTS predictions (
    id            BIGSERIAL PRIMARY KEY,
    play_id       BIGINT NOT NULL REFERENCES plays(id),
    model_version TEXT NOT NULL,
    win_prob_home REAL NOT NULL CHECK (win_prob_home BETWEEN 0 AND 1),
    UNIQUE (play_id, model_version)
);
