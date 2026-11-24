# Roadmap

The session's phases set the order. `BRIEF.md` has the times.

## Build

- Beat the sample strategy: `python3 simulate.py` ends with `RESULT win`.
- Hold against the house bot: `python3 simulate.py --opponent house`.
- Upload a strategy that passes: `python3 bot.py --submit` prints `upload passed`.

## Test and deploy

- Complete the pre-match checklist in `harness-spec.md`.
- Fix what fails, and upload again after every change to the strategy.

## Match

- Nothing to build. The script plays alone; no file changes.

## Ideas for later changes

- Defend the crystal when the opponent comes near.
- Take bombs when they are in reach.
- Build a supply line wider than one square, so that one capture cannot cut it.
