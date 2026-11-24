# Verify: A strategy that attacks the enemy crystal and defends our own

- Change: changes/001-beat-house-bot/
- Run at: 2026-11-23 (local time, fresh /sdlc:verify run; each command run alone from the repository root)

## Commands
| Command | Exit code | What the output shows |
|---|---|---|
| `python3 simulate.py --side red --opponent sample` | 0 | RESULT win 89-0, captured the crystal on turn 175; no KIT-ERROR/KIT-WARN |
| `python3 simulate.py --side red --opponent random` | 0 | RESULT win 85-0, captured the crystal on turn 77; no KIT-ERROR/KIT-WARN |
| `python3 simulate.py --side red --opponent house` | 0 | RESULT win 110-16, more territory at the end (600 turns); no KIT-ERROR/KIT-WARN |
| `python3 simulate.py --side blue --opponent sample` | 0 | RESULT win 89-0, captured the crystal on turn 175; no KIT-ERROR/KIT-WARN |
| `python3 simulate.py --side blue --opponent random` | 0 | RESULT win 88-0, captured the crystal on turn 72; no KIT-ERROR/KIT-WARN |
| `python3 simulate.py --side blue --opponent house` | 0 | RESULT win 110-16, more territory at the end (600 turns); no KIT-ERROR/KIT-WARN |

## Failures
None.

## Test plan
No design.md (short flow); the success criteria come from intent.md.

| Requirement | Test | Result in this run |
|---|---|---|
| Win vs sample as Red and Blue | the two `--opponent sample` commands | passed |
| Win vs random as Red and Blue | the two `--opponent random` commands | passed |
| Win vs house as Red and Blue | the two `--opponent house` commands | passed |
| No KIT-ERROR / KIT-WARN line | all six commands | passed (none printed, exit code 0) |
| Each `choose()` call under 0.5 s | not a registered command | not run in this step (Build measured max 0.0035 s) |
| `python3 bot.py --submit` prints `upload passed` | not a registered command | not run in this step (printed `upload passed` during Build) |

## Summary
All six registered simulator matches end in `RESULT win` with exit code 0 and no KIT-ERROR or KIT-WARN line. The time per call and the upload are not registered checks, so this step did not rerun them; both passed during the Build. The practice move (`python3 bot.py --practice`) is still to do once the phase is TESTING.
