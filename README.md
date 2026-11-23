# Color Wars starter kit

## The task

Write `choose` in `strategy.py`: a function that picks the next square to capture in a 10-minute Color Wars match against one opponent, with no human input.
You win by capturing the opponent's crystal, or by owning more squares when the match ends.
The work is ready when `python3 simulate.py` ends with a `RESULT` line, exit code 0, and no `KIT-ERROR` or `KIT-WARN` line. The next goal is `RESULT win`.
The full task brief, with the rules, the timeline and the connection steps, is `BRIEF.md` in this folder.

You edit one file: `strategy.py`. You may add more `.py` files and a `requirements.txt`; `--submit` uploads them too.
The kit needs Python 3.12 and nothing else. The arena runs Python 3.12; `bot.py` and `simulate.py` print a warning on any other version.

## Files

| File | Edit it? | Purpose |
| --- | --- | --- |
| `strategy.py` | Yes | Holds `choose`, the function that picks your next square |
| `config.json` | No | The game server's address (`server_url`) and the practice arena's (`practice_url`) |
| `bot.py` | No | Connects to the game server and plays your strategy, one move per second |
| `simulate.py` | No | Plays your strategy against a sample opponent, offline |
| `colorwars.py` | No | Game rules and the helpers your strategy may import |
| `tools/fake_server.py` | No | A local game server for testing `bot.py` without the network |
| `.env` | No | `python3 bot.py --login` writes your player key here |
| `.sdlc/` | No | Written by the bot: match phase, recorded hashes, run log |

Your color, your crystal and your opponent's crystal come from the server. You do not set them.

## Test in three levels

**Level 1: offline simulator.** No network, no key.

```
python3 simulate.py
python3 simulate.py --side blue --opponent random --map
python3 simulate.py --opponent house
python3 simulate.py --watch
```

`--watch` draws the board again every 10 turns while the match plays (`--watch 5` for every 5 turns). `M` is you, `x` is the opponent.

The sample strategy draws against itself. Your first goal is to beat it. The `house` opponent is the practice arena's house bot.

**Level 2: local fake server.** No network. Any key works. Start the server in one terminal:

```
python3 tools/fake_server.py                         lobby 5 s, build 5 s, testing 30 s, paused 5 s, live 120 s
python3 tools/fake_server.py --start testing --hold  stay in TESTING
```

Then run the bot against it in a second terminal. Add `--server http://127.0.0.1:8765` to every command:

```
python3 bot.py --server http://127.0.0.1:8765 --check
python3 bot.py --server http://127.0.0.1:8765 --practice
python3 bot.py --server http://127.0.0.1:8765
```

**Level 3: practice arena.** The real pipeline: upload, checks in the sandbox, and a 1-minute game against the house bot that you can watch.

```
python3 bot.py --dry-run
```

It prints each check and a live link to the game.

## Connect to the game server

1. Get your player key from the instructor. It starts with `cwk_`.
2. Run `python3 bot.py --login`. It joins the game as your Claude Code account and writes your player key into `.env`. Git ignores `.env`, and the bot never prints the key.
3. Run `python3 bot.py --check`. It prints `connected`, your color and your crystal squares.
4. In TESTING, run `python3 bot.py --practice`. It sends one legal move next to your crystal and confirms the server accepts it.
5. Run `python3 bot.py --phase` at any time to print the match phase.
6. Start `python3 bot.py --watch` when you arrive and leave it running. It keeps `.sdlc/arena-phase.json` up to date.

## Commands

| Command | What it does |
| --- | --- |
| `bot.py --login` | Joins as your Claude Code account and saves your player key in `.env` |
| `bot.py --check` | Reads your match and prints `connected`, your color, your crystal and the link to watch your match |
| `bot.py --practice` | In TESTING: one practice move; prints `practice passed` |
| `bot.py --phase` | Prints the phase and the banner once |
| `bot.py --watch` | Reads the phase every 5 seconds and keeps `.sdlc/arena-phase.json` fresh, until Ctrl-C |
| `bot.py --submit` | Uploads every `.py` file except `bot.py`, `simulate.py` and `colorwars.py`, plus `requirements.txt` |
| `bot.py --dry-run` | Practice arena: uploads, prints the checks and the live link of a 1-minute game |
| `bot.py` | Waits for LIVE, then plays until the match ends |
| `--server URL` | Added to any command: use that server instead of `config.json` |

Uploads are open in LOBBY, BUILD, TESTING and the strategy windows. A failed upload keeps your last good one.

## Play

```
python3 bot.py
```

Start the bot yourself, in your own terminal, before the phase is LIVE. Do not ask your AI assistant to start it.
The bot prints `waiting` until the phase is LIVE, then plays until the match ends.
Do not touch the keyboard during the match.

Each time the bot reads the phase before the match, it records the hashes of `strategy.py`, `config.json`, `bot.py` and `colorwars.py`.
After LIVE, the bot starts only if those four files are unchanged. A bot that crashed can be started again; a bot that was edited cannot.
Run `--check`, `--phase`, `--watch` or `bot.py` at least once after your last edit and before LIVE, or the bot refuses a late start.
Every move carries the same four hashes to the server.

## Output the tools rely on

| Line | Meaning |
| --- | --- |
| `KIT-ERROR choose raised: <Type>: <message>` | `choose` raised an error; the first legal square was taken |
| `KIT-WARN illegal square: <square>` | `choose` returned a square that is not legal; the first legal square was taken instead (the arena sandbox does the same) |
| `KIT-WARN reverted: <square>` | The server refused the move |
| `KIT-ERROR http <status> <GET or POST>` | The server refused a request |
| `KIT-WARN http 429` | The server asked the bot to slow down; the bot retries |
| `KIT-ERROR match already live, not starting` | The files changed after LIVE, or were never recorded |
| `KIT-ERROR match already over, not starting` | The bot was started after the match ended |
| `RESULT win\|loss\|draw <yours>-<theirs> <reason>` | Last line of `simulate.py` |

`simulate.py` exits with 0 after any finished match and with 1 when `choose` raised an error or returned an illegal square.
`bot.py --check`, `--practice`, `--phase`, `--submit` and `--dry-run` exit with 1 on any failure.

## What the kit does for you

- Reads the board from the server and tells `choose` which squares are legal.
- Takes the first legal square if `choose` returns a square that is not legal or raises an error,
  so the bot keeps running (the arena sandbox does the same, and also after a 0.5 s timeout).
- Tells `choose` which moves the server refused since the last board read (`reverted`).
- Retries when the server is slow or asks it to slow down.
- Corrects the match end time in `.sdlc/arena-phase.json` for a laptop clock that is wrong.
