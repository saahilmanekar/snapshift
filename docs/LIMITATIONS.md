# Known limitations

Numbers below come from `python3 -m model.src.evaluate` and `python3 -m scripts.validate_all_games`.

## Which games are in the library

nflverse lists 7,276 games for 1999-2025. 7,241 are replayable. The other 35:

- **15 real ties.** Valid data, excluded by policy: the model predicts "did the home team win?", and a tie has no answer.
- **3 games with no play-by-play data** at all (`1999_01_BAL_STL`, `2000_03_SD_KC`, `2000_06_BUF_MIA`). They have valid final scores in nflverse's schedule, but no plays.
- **16 Jacksonville home games from 2001 and 2002** (every one of them). nflverse's `td_team` field credits some touchdowns to the wrong team, so the running score is wrong, and the final score does not match the real result. A repair from possession data fixed some games but broke others, so these are excluded rather than patched.
- **1 game, `2011_13_DET_NO`.** A kickoff row repeats the previous touchdown's description and adds 6 phantom points.

## Play order

Plays are replayed in the order nflverse delivers them. For 2001-2025 that order matches the NFL's own `order_sequence` column on every row. `play_id` does not: it is a label, and it disagrees with that order on about 1% of rows (about 8% from 2022 on).

1999 and 2000 have no `order_sequence`, so their order is unverified.

## The model

- **Four features only:** score difference, seconds remaining, an overtime flag, and score x time. No down, distance, field position, possession, timeouts, or pregame team strength.
- **Held-out test:** five seasons, one per overtime-rule era (2003, 2011, 2014, 2019, 2024). Regulation plays only for the benchmark.

| Regulation Brier / log loss | |
|---|---|
| This model | 0.1637 / 0.4859 |
| nflfastR `home_wp` | 0.1576 / 0.4682 |
| nflfastR `vegas_home_wp` | 0.1426 / 0.4306 |

The gap to `home_wp` stays between 0.0056 and 0.0067 in every test season, and every probability bucket is within about 2 points of the real win rate. `vegas_home_wp` is not a like-for-like comparison: it includes the pregame betting spread, which this model never sees. nflfastR's exact training window was not verified.

## Overtime

On 1,253 overtime plays the model scores Brier 0.2558 and log loss 0.7046, no better than always guessing 50% (0.25 and 0.693). The likely cause, not tested here, is that the model cannot see who has the ball, which matters far more in overtime than in regulation. The `is_overtime` weight is also unstable (0.007 before the play-order fix, 0.103 after).

Overtime games stay replayable, but the probability line during an overtime period should not be trusted. The overtime flag also does not distinguish rule eras (playoff overtime changed in 2010 and 2022, regular-season overtime in 2012 and 2017).

## Other

- 3 plays with no game clock (a bare "Timeout." row) are dropped from model training.
