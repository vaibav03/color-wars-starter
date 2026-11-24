<!-- Saved by the course plugin from the plan approved at 2026-11-24T04:04:20.875Z. -->

# Plan: Expand first, then flank the enemy crystal

- Change: changes/002-expand-then-flank/
- Goal: `choose()` in `strategy.py` first grows territory around our own crystal, then raids the enemy crystal along a side route (not the central front), and always defends first when our crystal is in danger.
- Design: none (short way) — see changes/002-expand-then-flank/intent.md
- Run all tests: the six simulator matchups from CLAUDE.md
  `for s in red blue; do for o in sample random house; do python3 simulate.py --side $s --opponent $o | grep -E 'RESULT|KIT-'; done; done`
- Run one test: `python3 $SCRATCH/check_002.py <test name>` (one named check), where
  `SCRATCH=/private/tmp/claude-501/-Users-weiboli-color-wars-starter/ff005a73-483e-4952-b8f3-5d8d7d2347ec/scratchpad`

## Approach
Only `strategy.py` changes. `choose()` keeps a small memory (moves made so far) and plays in two halves: **expand** — score each legal square by squares gained (bombs count big), a compact wide shape, and closeness to our own crystal, so territory grows as a thick blob at home; **flank** — once we own about 60 squares (or after 90 moves), it walks to the enemy crystal along a `distance_map()` computed with the central front (columns L–Y, rows 14–21) treated as wall, so the attack goes through the top or bottom lane (whichever has fewer enemy squares, fixed once picked). Before either half, two rules come first: a square that finishes the enemy crystal wins at once, and an enemy square within 5 steps of our crystal is taken back (defence). Useful parts of change 001 stay: cut-off scoring, the refused-square penalty and the `_recent` anti-loop memory. The memory resets when we own 6 or fewer squares (a new match).

Because only `strategy.py` may change in the repository, the tests live in one helper script outside it, `$SCRATCH/check_002.py` (scratchpad, not uploaded). It imports `strategy` and the simulator's own pieces (`simulate.new_board`, `simulate.OPPONENTS`, `colorwars.view/legal_squares/capture`) and runs small matches, recording every square we pick.

## Success criteria → command that checks it
| Criterion (intent.md) | Command |
| --- | --- |
| All 6 matches `RESULT win`, no `KIT-ERROR`/`KIT-WARN` | the "Run all tests" loop: six `RESULT win` lines, no `KIT-` line |
| Territory clearly grows in the first half | `python3 $SCRATCH/check_002.py expand` |
| Second half reaches the enemy crystal by a side route | `python3 $SCRATCH/check_002.py flank` |
| Falls back to defend when our crystal is in danger | `python3 $SCRATCH/check_002.py defend` |
| Each `choose()` call under 0.5 s | `python3 $SCRATCH/check_002.py speed` |
| Watch the pattern by eye | `python3 simulate.py --side blue --opponent house --watch` (the simulator has `--watch`, not `--web`) |

### Task 1: The first half builds territory at home
Files: strategy.py (test: $SCRATCH/check_002.py)
1. Write the failing test `expand`: play 60 turns against `house` as red and as blue; every square we pick is within 8 steps of our crystal, and we own at least 50 squares at turn 60.
2. Run `python3 $SCRATCH/check_002.py expand` and see it fail, because today's strategy heads straight for the enemy crystal (picks more than 8 steps from home).
3. Smallest change: add the move counter + reset, a `_phase()` helper (expand until ≥60 squares or 90 moves), and the expand scoring (gain + bombs + shape − distance from home) used while in expand.
4. Run `expand` and see it pass. Then run all six matches.
5. Commit: `git commit -m "strategy: expand around home in the first half"`

### Task 2: The second half flanks through a side lane
Files: strategy.py
1. Write the failing test `flank`: full matches against `sample` and `house`, both sides; after the switch, at most 10% of our picks fall in the central front box (columns L–Y, rows 14–21), and at least one pick lands within 3 steps of the enemy crystal.
2. Run `python3 $SCRATCH/check_002.py flank` and see it fail, because after Task 1 the flank half still uses the straight `distance_map` to the enemy crystal, through the middle.
3. Smallest change: `_flank_map(board)` — copy the board, mark the central box and the other lane as wall, choose top/bottom lane by fewer enemy squares (kept in memory), then `distance_map()` to the enemy crystal; the flank scoring advances along it, preferring squares touching two of ours (wide line).
4. Run `flank` and see it pass. Then run all six matches.
5. Commit: `git commit -m "strategy: raid the enemy crystal by a side lane"`

### Task 3: Defend first when our crystal is in danger
Files: strategy.py
1. Write the test `defend`: hand-made boards (from `simulate.new_board()` via `view`) in both phases, with an enemy square 3 steps from our crystal that is in `legal`, and a tempting bomb elsewhere; `choose()` must return the enemy square. A second board where the last enemy crystal square is in `legal` must return that (win beats defence).
2. Run `python3 $SCRATCH/check_002.py defend` and see it fail, because in flank mode the bomb/advance scores outweigh the old defence bonus.
3. Smallest change: at the top of `choose()`, return the winning crystal square if present; else, if any legal enemy square is within 5 steps of our crystal, return the closest one.
4. Run `defend` and see it pass. Then run all six matches.
5. Commit: `git commit -m "strategy: defend home before expanding or raiding"`

### Task 4: Win all six and stay fast
Files: strategy.py (only if tuning is needed)
1. Test: the "Run all tests" loop, plus `python3 $SCRATCH/check_002.py speed` (wraps `choose` with `time.perf_counter` over a full house match, both sides; fails if the slowest call ≥ 0.5 s).
2. Run them; if any match is not `RESULT win` or speed fails, see why with `--map`.
3. Smallest fix: tune the switch point (60 squares / 90 moves) or the weights; for speed, compute the flank map once per call and score only the nearest ~40 legal squares.
4. Run all six and `speed`, and see six wins with no `KIT-` line and max < 0.5 s. Also re-run `expand`, `flank`, `defend`.
5. Commit only if strategy.py changed: `git commit -m "strategy: tune expand/flank to win all six"`

## Verification (end to end)
- Six `RESULT win` lines, no `KIT-ERROR`/`KIT-WARN`.
- `expand`, `flank`, `defend`, `speed` checks all print `PASS`.
- `python3 simulate.py --side blue --opponent house --watch` shows the blob at home first, then a lane attack.
