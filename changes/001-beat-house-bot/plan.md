<!-- Saved by the course plugin from the plan approved at 2026-11-24T02:10:45.240Z. -->

# Plan: A strategy that attacks the enemy crystal and defends our own

- Change: changes/001-beat-house-bot/
- Goal: `choose()` in `strategy.py` attacks the enemy crystal along the shortest path and protects our own crystal (cutting the enemy's line, pulling them away from our base), so it beats the sample, random and house bots.
- Design: none (short way) — see changes/001-beat-house-bot/intent.md
- Run all tests: the six simulator matchups
  `for s in red blue; do for o in sample random house; do python3 simulate.py --side $s --opponent $o | tail -1; done; done`
- Run one test: `python3 simulate.py --side red --opponent house | tail -1`

## Approach
Only `strategy.py` changes. For every legal square, `choose()` tries the capture on a copy of the board with `capture()` from `colorwars.py` (the same rules the referee uses) and scores what happens: squares we gain (bombs count big), enemy squares we cut off from their crystal, and enemy squares near our crystal we remove (defence). When nothing scores, it advances toward the enemy crystal along `distance_map()` and prefers squares touching two or more of our own, so the attack line is wider than one square and a single cut costs less. The "test" for each task is a simulator match: it must print `RESULT win` and no `KIT-ERROR`/`KIT-WARN` line. No new test files: the intent allows editing only `strategy.py`.

## Success criteria → command that checks it
| Criterion | Command |
| --- | --- |
| Win vs sample, random, house as Red and Blue | the "Run all tests" loop above: six lines all `RESULT win` |
| No KIT-ERROR / KIT-WARN | `python3 simulate.py --side … --opponent … \| grep -c KIT-` prints 0 for all six |
| Each call under 0.5 s | timing one-liner in Task 4 prints max < 0.5 |
| Upload passed | `python3 bot.py --submit` prints `upload passed` |

### Task 1: Beat the sample bot on both sides
Files: strategy.py
1. Failing test: `python3 simulate.py --side red --opponent sample` and `--side blue`. Today: `RESULT draw 25-25`.
2. Run them and see draw, because both bots play the same move.
3. Smallest change: score each legal square by simulated capture (gain + 2×enemy squares cut off), tie-break by distance to the enemy crystal.
4. Run both again and see `RESULT win`; then run all six.
5. Commit: `git commit -m "strategy: score captures by gain and cuts"`

### Task 2: Beat the house bot on both sides
Files: strategy.py
1. Failing test: `python3 simulate.py --side red --opponent house` and `--side blue`. Today: `RESULT loss 16-34`.
2. Run and see loss, because the house bot cuts our one-square line and defends its home.
3. Change: add defence (big bonus for capturing an enemy square within 6 steps of our crystal, and for cutting their line), prefer advance squares touching ≥2 of ours (wide line), and grab bombs early. Tune weights until both sides win.
4. Run both and see `RESULT win`; then all six.
5. Commit: `git commit -m "strategy: defend home, wide attack line, beat house bot"`

### Task 3: Still beat the random bot on both sides
Files: strategy.py (only if needed)
1. Test: `python3 simulate.py --side red --opponent random` and `--side blue` (also with `--seed 2`, `--seed 3`).
2. If any is not a win, see why with `--map`.
3. Fix the smallest weight or rule causing it.
4. Run all six and see six wins.
5. Commit only if strategy.py changed: `git commit -m "strategy: hold up against random bot"`

### Task 4: Each call is under 0.5 s
Files: none unless too slow
1. Test: run one house match with a timing wrapper (one-liner that imports `simulate`, wraps `strategy.choose` with `time.perf_counter`, prints the max).
2. If max ≥ 0.5 s, it fails.
3. Fix: cap scored candidates (score only the nearest ~40 legal squares plus bombs/enemy squares) .
4. See max < 0.5 s (target < 0.2 s) and still six wins.
5. Commit if changed: `git commit -m "strategy: keep each move fast"`

### Task 5: Upload
Files: none (no test: this sends the file, it does not change code)
1. Check phase with `python3 bot.py --phase` (stop if LIVE or PAUSED).
2. Run `python3 bot.py --submit`; it must print `upload passed`.
3. `python3 bot.py --practice` only when the phase is TESTING (it is LOBBY now); otherwise tell the student to run it in TESTING.
