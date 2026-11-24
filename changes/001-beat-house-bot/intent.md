# Intent: A strategy that attacks the enemy crystal and defends our own

- Change: changes/001-beat-house-bot/
- Date: 2026-11-23
- Task as given: "my strategy is to find the most efficient path the attack their base/crystal, while protect our own ( u can try to distract their target so our base is protected)"
- Roadmap: not on the roadmap (the starter kit has no specs/roadmap.md)

## Goal
`choose()` in `strategy.py` attacks the enemy crystal along the shortest path and protects our own crystal, for example by cutting the enemy's attack line or drawing the opponent away from our base, so it beats the sample and house bots.

## Users
The student, in the Color Wars class matches: round 0 runs on the laptop, and the uploaded strategy plays the later rounds against other students.

## Success criteria
- `python3 simulate.py` against the sample, random and house opponents, as both Red and Blue, ends in `RESULT win`, with no `KIT-ERROR` or `KIT-WARN` line.
- Example: when the student runs `python3 simulate.py --opponent house`, then the result is `RESULT win` (the sample strategy loses 16-34 today).
- `python3 bot.py --submit` prints `upload passed`.

## Out of scope
- No edits to `bot.py`, `colorwars.py`, `config.json` or `simulate.py`.
- No moves sent to the game server during BUILD.
- No starting `python3 bot.py` for the match: the student starts it.

## Constraints
- None from the Constitution or a Harness Spec: the starter kit has neither. BRIEF.md: only `strategy.py` is edited.

## Assumptions
- Each `choose()` call returns in under 0.5 s (the arena sandbox's limit).
- The standard library only; no `requirements.txt`.

## What the student said
- Find the most efficient path to attack the enemy base/crystal, while protecting our own.
- Distracting the opponent so our base is protected is a welcome idea.
- Edit only strategy.py; it must beat the sample bot (setup message).
- Skipped the remaining questions ("好吧继续build"); agreed to the write-back ("yes").
