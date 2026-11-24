# Verify: Expand first, then flank the enemy crystal

- Change: changes/002-expand-then-flank/
- Run at: 2026-11-23 (local date; the clock time was not read in this step, because this step runs only the registered commands)

## Commands
| Command | Exit code | What the output shows |
|---|---|---|
| `python3 simulate.py --side red --opponent sample` | 0 | `RESULT win 141-0 captured the crystal on turn 353`; no KIT-ERROR / KIT-WARN line |
| `python3 simulate.py --side red --opponent random` | 0 | `RESULT win 161-0 captured the crystal on turn 163`; no KIT-ERROR / KIT-WARN line |
| `python3 simulate.py --side red --opponent house` | 0 | `RESULT win 207-15 more territory at the end`; no KIT-ERROR / KIT-WARN line |
| `python3 simulate.py --side blue --opponent sample` | 0 | `RESULT win 141-0 captured the crystal on turn 353`; no KIT-ERROR / KIT-WARN line |
| `python3 simulate.py --side blue --opponent random` | 0 | `RESULT win 159-0 captured the crystal on turn 163`; no KIT-ERROR / KIT-WARN line |
| `python3 simulate.py --side blue --opponent house` | 0 | `RESULT win 207-15 more territory at the end`; no KIT-ERROR / KIT-WARN line |

6 of 6 commands end in `RESULT win`; 0 KIT-ERROR, 0 KIT-WARN.

## Failures
None.

## Test plan
There is no design.md (short way); the test plan is the success criteria in plan.md.

| Requirement | Test | Result in this run |
|---|---|---|
| All 6 matches `RESULT win`, no KIT-ERROR / KIT-WARN | the six registered commands above | passed (6/6) |
| Territory clearly grows in the first half | `check_002.py expand` (scratchpad) | not run in this step; passed during the build (64 squares at turn 60, 0 picks more than 8 steps from home, both sides) |
| Second half reaches the enemy crystal by a side route | `check_002.py flank` (scratchpad) | not run in this step; passed during the build (0–1% of raid picks in the central front, 14–17 picks within 3 steps of the enemy crystal) |
| Defends first when our crystal is in danger | `check_002.py defend` (scratchpad) | not run in this step; passed during the build |
| Each `choose()` call under 0.5 s | `check_002.py speed` (scratchpad) | not run in this step; passed during the build (slowest 0.006 s) |

## Summary
All six registered simulator matches, red and blue against sample, random and house, end in `RESULT win` with exit code 0 and no KIT-ERROR or KIT-WARN line. The red-vs-house output shows territory growing from 89 at turn 100 to 207 by the end. The expand, flank, defend and speed checks are not registered commands, so this step did not re-run them; they passed during the build. Watching the expand-then-flank pattern by eye (`--watch`) was not done in this step.
