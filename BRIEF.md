# Color Wars Script Challenge: Task Brief

Updated 2026-11-23

## Purpose

You build a script that plays Color Wars against one opponent at a time with no human input. You write the strategy. We supply the code that connects to the game server, reads the board, and sends your moves. The server is the referee. The dashboard (https://dash-sand-omega.vercel.app) shows every match, and you can only view it.

You work with an AI coding assistant for the whole session. Your result depends on two things: how well your strategy chooses squares, and whether your script runs for the full match without stopping.

## Timeline

The instructor starts the session when everyone has joined. Build comes first. Then all your matches play at the same time, on the server: your uploaded strategy plays every opponent at once. There are no rounds, and your laptop does not play. The dashboard shows each phase and how long it has left.

| Phase | When | What you do | What you must not do |
| --- | --- | --- | --- |
| Build | the instructor sets the length in class; the dashboard shows the time left | Start the change with `/sdlc:intent` and your idea, then approve the plan and let your AI assistant build and check it. Test it in the offline simulator. Upload it with `python3 bot.py --submit`. | Send moves to the game server. |
| Get ready | 30 seconds | Watch. The server starts your uploaded strategy once for each match. | Upload: the server refuses it and your last good upload stays. |
| Matches | the rest of the game | Watch. Your last good upload plays all your opponents at the same time, each on its own board, in the server's sandbox. Your laptop does not play. | Use your AI assistant: it stays locked until the game is over. Upload: the server refuses it. |

Build ends early when everyone has uploaded. Each match has its own board, and the dashboard shows all of them live.

## Game rules

The board is a grid of 36 columns and 34 rows. Columns are labelled A to Z, then AA to AJ. Rows are numbered 1 to 34. A square is named by column then row, for example `G17`.

Each player has a base of five squares in a plus shape, called the crystal. Red holds E29, D30, E30, F30, and E31 (bottom left). Blue holds AF4, AE5, AF5, AG5, and AF6 (top right).

The map is the same in every match. It has 40 walls and 16 bombs. If you turn the board through a half turn (180 degrees), each player sees the same map.

- Walls: R7 S7 F8 Q8 T8 G9 P9 U9 O10 V10 L13 Y13 K14 Z14 J15 AA15 I16 AB16 H17 AC17 H18 AC18 I19 AB19 J20 AA20 K21 Z21 L22 Y22 O25 V25 P26 U26 AD26 Q27 T27 AE27 R28 S28.
- Bombs: R4 S4 G7 H8 U14 F17 R17 S17 R18 S18 AE18 P21 AC27 AD28 R31 S31.

To see the map, run `python3 simulate.py --map`.

| Square | Fill color | Meaning |
| --- | --- | --- |
| Red | `#f16c7f` | Owned by Red |
| Blue | `#7b92ff` | Owned by Blue |
| Empty | `#f5f6f8` | Owned by no one |
| Wall | `#000000` | Cannot be captured |
| Bomb | `#f5d128` | Captures a 3 by 3 block when taken |

The game server is the referee. It checks every move against six rules.

1. **Capture.** You capture a square by sending it to the server as your move. The square must touch one of your squares on its top, bottom, left, or right side. Diagonal contact does not count. You may capture empty squares and enemy squares.
2. **Walls.** You cannot capture a wall.
3. **Bombs.** When you capture a bomb, the eight squares around it also become yours, except walls.
4. **Supply lines.** Every square you own must connect to your crystal through your own squares. Squares that lose this connection become empty.
5. **Rate.** You may capture one square per second. The server refuses a move that arrives early.
6. **Scope.** You play only with your own key, and only on your own match. The server refuses any other move.

## How you win

The referee decides the match in this order. It stops at the first rule that produces a winner.

1. **Crystal capture.** If you own all five squares of your opponent's crystal at any moment, you win and the match ends.
2. **Territory.** When the match time ends, the player who owns more squares wins.
3. **Crystal threat.** If both players own the same number of squares, the player whose crystal is under less threat wins.

The threat score measures how close your opponent came to your crystal. It combines two equal parts: how many enemy squares sit near your crystal, and how close the nearest one is.

```latex
\text{threat} = 0.5 \times \frac{n}{N} + 0.5 \times \frac{R + 1 - d}{R}
```

| Symbol | Meaning |
| --- | --- |
| R | The range, set to 5 squares |
| N | The number of capturable squares within R steps of your crystal |
| n | The number of those squares your opponent owns |
| d | The distance in steps from your crystal to the nearest enemy square within range |

A step is one move up, down, left, or right. If no enemy square is within range, the threat score is 0. The score runs from 0 to 1, and the lower score wins.

## What you build

You write one function, `choose`. The starter kit calls it once per second and sends the square it returns to the server. Everything else is already written.

| File | Who edits it | What it does |
| --- | --- | --- |
| `strategy.py` | You | Holds `choose`, your strategy |
| `config.json` | No one | Sets the game server's address, the practice arena's address, and how often to re-read the board. The timing is the same for every player and fixed. Your color and crystals come from the server |
| `bot.py` | No one | Connects to the game server, reads the board, calls `choose`, sends one move, waits one second, repeats |
| `simulate.py` | No one | Runs your strategy against a sample opponent on your laptop, with no network. The sample strategy draws against itself, so your first goal is to beat it |
| `colorwars.py` | No one | Holds the game rules and two helpers your strategy may import: `neighbors` and `distance_map` |
| `tools/fake_server.py` | No one | A game server on your laptop, with short phases, for testing `bot.py` |

`choose` receives the current board and returns the name of one square, for example `"G17"`. The starter kit passes it five things.

| Input | Content |
| --- | --- |
| `board` | The owner of every square: `me`, `enemy`, `empty`, `wall`, or `bomb` |
| `legal` | The squares you can capture right now under rule 1 |
| `my_crystal` | Your five crystal squares |
| `enemy_crystal` | Your opponent's five crystal squares |
| `reverted` | The squares the server refused since the last board read |

If `choose` returns a square that is not in `legal`, or raises an error, the starter kit logs a warning and captures the first square in `legal` instead, so your script keeps running. The arena's sandbox does the same in the round robin (and also when `choose` takes longer than 0.5 s).

Two decisions are yours and affect the result.

- **Which square to take.** The sample strategy takes the legal square closest to the enemy crystal. It ignores defense.
- **What to do after a refusal.** The server refuses moves that break a rule. The starter kit tells `choose` which squares were refused since the last read.

## Join the game

You join as your Claude Code account (any account works). Nothing else to create. Allow 1 minute.

1. Open a terminal in the starter kit folder and start Claude Code there: `cd color-wars-starter`, then `claude`. In the desktop app, choose the `color-wars-starter` folder for the session. Claude Code must run inside this folder, not in a folder above it.
2. Check that Claude Code is logged in (type `/status`; if not, `/login`).
3. Run `python3 bot.py --login`. It prints `joined as`, your name on the dashboard, and the link to watch your match.
4. Run `python3 bot.py --check`. It prints `connected`; your color and crystal appear once BUILD has made the pairings.
5. Run `python3 bot.py --watch` and leave it running in its own terminal. It reads the phase every 5 seconds and writes `.sdlc/arena-phase.json`.

Join before BUILD starts: the server makes the pairings from everyone who joined. `--login` reads your account's id, email and name from Claude Code's settings on this computer and sends them to the game server, which gives you a player key; `bot.py` saves the key in `.env`. The same account always gets the same key, so `--login` again is safe. Do not share the key. Git ignores `.env`, and the script never prints the key. In Claude Code, `/join` does these steps with you.

## Workflow

Every change to your strategy goes through the same steps in Claude Code. `/sdlc:intent` starts them.

1. Type `/sdlc:intent` and your idea, in your own words. For example: `/sdlc:intent defend my crystal when the enemy is within 5 squares, otherwise push to their crystal`.
2. Read the intent your assistant writes from your words, and approve it or ask for changes.
3. Read the plan, and approve it or ask for changes. Your assistant edits no code before you approve the plan.
4. Your assistant builds the change, one small tested task at a time, then runs the checks again and shows you the results to accept.
5. When you are asked whether to deliver the change, choose "Deliver now" if you are happy with it. This closes the change; nothing is sent anywhere.
6. Upload with `python3 bot.py --submit`.

For the next idea, type `/sdlc:intent` again. The files of each change are in `changes/`.

## Test in three levels

| Level | Command | What it tests | Needs |
| --- | --- | --- | --- |
| 1. Simulator | `python3 simulate.py` (also `--opponent random`, `--opponent house`, and `--web` to watch the match in your browser at http://localhost:8000) | Your strategy and the rules | Nothing |
| 2. Fake server | `python3 tools/fake_server.py` in one terminal, then `python3 bot.py --server http://127.0.0.1:8765 --check`, `--practice` and a full run | `bot.py` with your strategy, the phases, refused moves | Nothing; any key works |
| 3. Practice arena | `python3 bot.py --dry-run` | Your upload, the sandbox checks, and a 1-minute game against the house bot, with a live link | Your key |

## Commands

| Command | What it does |
| --- | --- |
| `python3 bot.py --login` | Joins as your Claude Code account and saves your player key in `.env` |
| `python3 bot.py --check` | Prints `connected`, your color and your crystal |
| `python3 bot.py --practice` | In TESTING only: sends one practice move and prints `practice passed` |
| `python3 bot.py --phase` | Prints the phase once |
| `python3 bot.py --watch` | Keeps `.sdlc/arena-phase.json` fresh until Ctrl-C |
| `python3 bot.py --submit` | Uploads all your `.py` files except `bot.py`, `simulate.py`, `colorwars.py` and the tests in `tests/`, plus `requirements.txt` |
| `python3 bot.py --dry-run` | Practice arena: prints the checks and the live link |
| `python3 bot.py` | Waits for LIVE, then plays the match |

Join is open in LOBBY only. Uploads are open in LOBBY, BUILD, TESTING and the strategy windows. The server installs `requirements.txt` once, at upload. A failed upload keeps your last good one. The arena runs Python 3.12. Python 3.12 is mandatory on your laptop too, even if you already have another version: the kit stops on every other version, newer or older.

## Pre-match checklist

Complete all six checks before minute 30. A script that fails a check is not ready to play.

- [ ] `python3 simulate.py` ends with a `RESULT` line and prints no line that starts with `KIT-ERROR` or `KIT-WARN`.
- [ ] `python3 bot.py --check` prints `connected`, your color, and your crystal squares.
- [ ] `python3 bot.py --submit` prints `upload passed`.
- [ ] `python3 bot.py --practice`, in TESTING, sends one move next to your crystal and prints `practice passed`.
- [ ] `python3 bot.py --watch` runs in its own terminal.
- [ ] `python3 bot.py`, started in your own terminal after your last edit, prints `waiting` until the phase is LIVE.

Leave the last command running. The script starts on its own when the phase changes to LIVE. Start it yourself; do not ask your AI assistant to start it. Each run before LIVE records your four kit files. After LIVE, the script starts only with those same files. A script that stopped can be started again, and a script that was edited cannot.

## Rules of conduct

The match tests your script, so you do not help it once the match starts.

- Do not edit any file between LIVE and the end of the match.
- If your script stops, you may start it again with `python3 bot.py`. Type nothing else. The script runs only if no kit file has changed since before LIVE.
- Do not send moves by hand or through an AI assistant.
- Do not use another student's key or run a second script.

The server logs every move request with the key that sent it. A player who breaks a rule forfeits the match. Your AI assistant may stop answering in the starter kit folder while the banner reads PAUSED or LIVE. This is expected.

## Troubleshooting

Each row is a failure seen in practice rounds or one the setup steps can cause. Fix these during the test phase. You cannot fix them during the match.

| What you see | Cause | Fix |
| --- | --- | --- |
| `Set your player key first` | The script found no key in `.env` | Run `python3 bot.py --login` |
| `Log in to Claude Code first` | Claude Code is not logged in on this computer | Run `claude`, type `/login`, sign in |
| `join failed: joining is closed` | BUILD has started | Ask the instructor |
| `HTTP 401` or `HTTP 403` on `--check` | The key is wrong or not loaded | Run `python3 bot.py --login` again |
| `HTTP 403` on a move, then `Laptop play is over` | The move is not for your current match, or the round robin has started | The script stops. In the round robin this is expected: your upload plays. In round 0, run `python3 bot.py` again |
| `HTTP 429` | Too many requests | The starter kit slows down and retries on its own. Close every other copy of `bot.py` |
| `Python 3.12 is mandatory` | Your Python is not 3.12 (another version installed is not enough) | Install Python 3.12 (python.org or `brew install python@3.12`) and run the kit with `python3.12` |
| `upload refused` | `strategy.py` does not import, `choose` failed, or `requirements.txt` did not install | Fix the error it prints and run `--submit` again |
| `practice failed: ... practice_used` | You already sent your one practice move | Nothing to fix |
| The script prints `waiting` after the phase is LIVE | A board read is in progress | Wait a few seconds. The script reads every 2 seconds |
| `KIT-WARN reverted` with `illegal` | Your opponent took the square next to it since the last read | Take squares from `legal` only, and use `reverted` in `choose` |
| `KIT-WARN reverted` with `cooldown` | A second program is sending moves with your key | Close every other copy of `bot.py` |
| Your squares turn empty in a block | Your opponent cut your supply line | Your strategy needs a wider line or a defense rule. This is a strategy problem, not a bug |
| KIT-ERROR match already live, not starting | A kit file changed after LIVE, or the script never ran before LIVE | Run the script after your last edit and before LIVE. During a match there is no fix |
