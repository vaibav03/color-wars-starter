# Harness Spec

The engineering around the strategy: what checks it, what guards it, and what it leaves on record. The script has no model in it, so the sections about a model say so.

| Section | Now |
|---|---|
| Context strategy | None: no model in the script. `choose` sees the board, the legal squares, both crystals and the refused squares, once per move |
| Tool inventory and MCP wiring | None in the script. The kit's commands are listed in `README.md` |
| Memory model | Whatever `strategy.py` keeps in its own variables during one run. Nothing is saved between runs |
| Model selection and fallbacks | None |
| Eval suite | The tests in `tests/` and the simulator checks below |
| Guardrails | The kit takes the first legal square when `choose` raises an error or returns a square that is not legal. The arena does the same, and also after 0.5 seconds |
| Observability | The `KIT-ERROR`, `KIT-WARN` and `RESULT` lines the kit prints; `.sdlc/arena-run.log`; the dashboard |
| Reliability budget | No `KIT-ERROR` and no `KIT-WARN` line in any simulator run. The script runs for the whole match |
| Security and governance | The player key stays in `.env` and is never printed. Nobody edits the kit's files. No file changes from LIVE to the end of the match |

## Simulator checks

Offline, no key. Run after every change to the strategy. These are the verification commands in `CLAUDE.md`.

| Check | Command | Passes when |
|---|---|---|
| Tests | `python3 -m unittest discover -s tests` | Exit code 0 |
| Against the sample strategy | `python3 simulate.py` | Exit code 0, a `RESULT` line, no `KIT-ERROR` or `KIT-WARN` line |
| Against the house bot, from the other side | `python3 simulate.py --side blue --opponent house` | The same |

A `RESULT loss` is a finished run, not a failed check. It tells you the strategy needs work.

## Practice arena check

Needs your key and the network.

| Check | Command | Passes when |
|---|---|---|
| Upload and a 1-minute game against the house bot | `python3 bot.py --dry-run` | Every check it prints passes |

## Pre-match checklist

Complete all six before the match. The student runs the last three in their own terminal.

- [ ] `python3 simulate.py` ends with a `RESULT` line and prints no line that starts with `KIT-ERROR` or `KIT-WARN`.
- [ ] `python3 bot.py --check` prints `connected`, your color, and your crystal squares.
- [ ] `python3 bot.py --submit` prints `upload passed`.
- [ ] `python3 bot.py --practice`, in TESTING, sends one move next to your crystal and prints `practice passed`. The server allows it once.
- [ ] `python3 bot.py --watch` runs in its own terminal.
- [ ] `python3 bot.py`, started in your own terminal after your last edit, prints `waiting` until the phase is LIVE.
