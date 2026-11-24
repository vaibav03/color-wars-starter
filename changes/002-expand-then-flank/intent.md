# Intent: Expand first, then flank the enemy crystal

- Change: changes/002-expand-then-flank/
- Date: 2026-11-23
- Task as given: "我的strategy是一开始在我周围占领足够多的地盘然后走偏路偷袭对方水晶"
- Roadmap: not on the roadmap (the starter kit has no specs/roadmap.md)

## Goal
`choose()` in `strategy.py` plays in two halves. In the first half it expands territory around our own crystal ("让自己肉厚"). In the second half it takes a side route, not the central front, to raid the enemy crystal. Whenever our own crystal is in danger, it falls back to defend first.

## Users
The student, in the Color Wars class matches: round 0 runs on the laptop, and the uploaded strategy plays the later rounds against other students.

## Success criteria
- All 6 verification commands in `CLAUDE.md` (red and blue against sample, random and house) end in `RESULT win`, with no `KIT-ERROR` or `KIT-WARN` line.
- In the simulator, our territory clearly grows in the first half, and in the second half the attack reaches the enemy crystal along a side route rather than the central front.
- Example: when the student runs `python3 simulate.py --side blue --opponent house`, then the result is `RESULT win`, and watching with `--web` shows the expand-first, flank-later pattern.

## Out of scope
- Only `strategy.py` changes. No edits to `config.json` (including `refresh_every`), `bot.py`, `colorwars.py`, `simulate.py` or `tools/`.

## Constraints
- None from the Constitution or a Harness Spec: the starter kit has neither. `CLAUDE.md` and BRIEF.md: only `strategy.py` is edited.

## Assumptions
- `choose()` does not receive the match time, so "first half / second half" is estimated from the number of moves made so far. The match length is not fixed (rounds share 20 minutes); the exact switch point is decided in design.
- "Danger" means enemy squares coming near our crystal (for example within 5 steps, the same range as the threat rule). The exact test is decided in design.
- Each `choose()` call returns in under 0.5 s (the arena sandbox's limit). Standard library only.
- The new strategy replaces change 001's approach but may keep useful parts of it, such as the logic that stops trade loops over the same squares.

## What the student said
- 一开始在我周围占领足够多的地盘，然后走偏路偷袭对方水晶。
- 前半段时间占地盘，让自己肉厚；后半段直接偷袭；出现危险再回防。
- Success: option (b): all six verification runs win, and the simulator visibly shows the first-half expansion and the second-half flank attack.
- Out of scope: option (a): only `strategy.py`; no changes to `config.json` or the other kit files.
- Agreed to the write-back ("yes").
