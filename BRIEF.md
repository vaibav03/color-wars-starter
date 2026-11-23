# Color Wars Script Challenge: Task Brief

Updated 2026-11-22

## Purpose

You build a script that plays Color Wars against one opponent for 10 minutes with no human input. You write the strategy. We supply the code that connects to the game server, reads the board, and sends your moves. The server is the referee. The Miro boards show every match, and you can only view them.

You work with an AI coding assistant for the whole session. Your result depends on two things: how well your strategy chooses squares, and whether your script runs for the full match without stopping.

## Timeline

The session runs about 2.5 hours. The first 40 minutes have three phases; then your uploaded strategy plays a round robin against every other student. The instructor announces the start and end of each phase.

| Phase | Minutes | What you do | What you must not do |
| --- | --- | --- | --- |
| Build | 0 to 20 | Write your strategy with your AI assistant. Test it in the offline simulator. Upload it with `python3 bot.py --submit`. | Send moves to the game server. |
| Test and deploy | 20 to 30 | Connect your script to the game server. Run the pre-match checklist. Fix what fails. Upload again if you changed `strategy.py`. | Send more than the one practice move. |
| Match (round 0) | 30 to 40 | Watch. Your script is already running on your laptop and starts on its own when the phase is LIVE. | Edit any file, send moves by hand, or use your AI assistant. |
| Round robin | 40 to about 150 | Watch. 29 rounds of 2 minutes with a 30-second gap between rounds. Your last good upload plays every round in the server's sandbox; your laptop does not play. | Use your AI assistant: it stays locked during every round and every gap. |
| Strategy window | after rounds 10 and 20, 5 minutes each | Improve your strategy with your AI assistant and run `--submit` again. These two windows are the only chances to change what plays. | Upload outside a window: the server refuses it and your last good upload stays. |

The course pairs you with one opponent. You and your opponent play on your own board, and the server mirrors it to Miro. Fifteen matches run at the same time.

## Game rules

The board is a grid of 36 columns and 34 rows. Columns are labelled A to Z, then AA to AJ. Rows are numbered 1 to 34. A square is named by column then row, for example `G17`.

Each player has a base of four squares, called the crystal. Red holds B17, B18, C17, and C18. Blue holds AH17, AH18, AI17, and AI18.

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

1. **Crystal capture.** If you own all four squares of your opponent's crystal at any moment, you win and the match ends.
2. **Territory.** At 10 minutes, the player who owns more squares wins.
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
| `config.json` | No one | Sets the game server's address, the practice arena's address, and how often to re-read the board. Your color and crystals come from the server |
| `bot.py` | No one | Connects to the game server, reads the board, calls `choose`, sends one move, waits one second, repeats |
| `simulate.py` | No one | Runs your strategy against a sample opponent on your laptop, with no network. The sample strategy draws against itself, so your first goal is to beat it |
| `colorwars.py` | No one | Holds the game rules and two helpers your strategy may import: `neighbors` and `distance_map` |
| `tools/fake_server.py` | No one | A game server on your laptop, with short phases, for testing `bot.py` |

`choose` receives the current board and returns the name of one square, for example `"G17"`. The starter kit passes it five things.

| Input | Content |
| --- | --- |
| `board` | The owner of every square: `me`, `enemy`, `empty`, `wall`, or `bomb` |
| `legal` | The squares you can capture right now under rule 1 |
| `my_crystal` | Your four crystal squares |
| `enemy_crystal` | Your opponent's four crystal squares |
| `reverted` | The squares the server refused since the last board read |

If `choose` returns a square that is not in `legal`, or raises an error, the starter kit logs a warning and captures the first square in `legal` instead, so your script keeps running. The arena's sandbox does the same in the round robin (and also when `choose` takes longer than 0.5 s).

Three decisions are yours and affect the result.

- **Which square to take.** The sample strategy takes the legal square closest to the enemy crystal. It ignores defense.
- **How often to re-read the board.** Between reads your script acts on old information: it sees your own captures at once, but not your opponent's. `refresh_every` in `config.json` sets the number of captures between reads.
- **What to do after a refusal.** The server refuses moves that break a rule. The starter kit tells `choose` which squares were refused since the last read.

## Join the game

You join with your own Miro account, as in the course's Miro game. You create a Miro app, install it to the class team, and copy the access token it gives you. `bot.py --login` sends the token to the game server once. The server asks Miro who you are, checks that you are in the class team, gives you a seat and a player key, and `bot.py` saves the key in `.env`. Join before BUILD starts: the server makes the pairings from everyone who joined. Allow 5 minutes. In Claude Code, `/join` walks you through these steps.

**Create the app**

1. Sign in to Miro. Click your avatar, then select **Settings**.
2. Open the **Your apps** tab. Click **+ Create new app**.
3. Enter an app name, for example `color-wars-yourname`.
4. Leave **Expire user authorization token** cleared.
5. Click **Create app**.

**Set permissions**

1. On the app settings page, find the permissions list.
2. Select `boards:read` and `identity:read`. Select nothing else.

**Install the app and copy the token**

1. At the bottom of the app settings page, click **Install app and get OAuth token**.
2. In **Select a team**, choose the class team, **ASU CIS**.
3. Click **Install & authorize**.
4. Miro shows your access token. Copy it. Click **Close**.

**Join**

1. Open a terminal in the starter kit folder.
2. Copy `.env.example` to `.env`. Put your token after `MIRO_TOKEN=` and save the file. You or your AI assistant may do this.
3. Run `python3 bot.py --login`. It prints `joined as`, your name on the dashboard, and the link to watch your match.
4. Run `python3 bot.py --check`. It prints `connected`; your color and crystal appear once BUILD has made the pairings.
5. Run `python3 bot.py --watch` and leave it running in its own terminal. It reads the phase every 5 seconds and writes `.sdlc/arena-phase.json`.

The server uses the Miro token only to learn who you are; it does not store it. The player key identifies you to the game server: the same Miro account always gets the same key, so `--login` again is safe. Use both for this course only and do not share them. Git ignores `.env`, and the script never prints the token or the key. After the session, delete the app in **Your apps**.

## Test in three levels

| Level | Command | What it tests | Needs |
| --- | --- | --- | --- |
| 1. Simulator | `python3 simulate.py` (also `--opponent random` and `--opponent house`) | Your strategy and the rules | Nothing |
| 2. Fake server | `python3 tools/fake_server.py` in one terminal, then `python3 bot.py --server http://127.0.0.1:8765 --check`, `--practice` and a full run | `bot.py` with your strategy, the phases, refused moves | Nothing; any key works |
| 3. Practice arena | `python3 bot.py --dry-run` | Your upload, the sandbox checks, and a 1-minute game against the house bot, with a live link | Your key |

## Commands

| Command | What it does |
| --- | --- |
| `python3 bot.py --login` | Joins with `MIRO_TOKEN` from `.env` and saves your player key in `.env` |
| `python3 bot.py --check` | Prints `connected`, your color and your crystal |
| `python3 bot.py --practice` | In TESTING only: sends one practice move and prints `practice passed` |
| `python3 bot.py --phase` | Prints the phase once |
| `python3 bot.py --watch` | Keeps `.sdlc/arena-phase.json` fresh until Ctrl-C |
| `python3 bot.py --submit` | Uploads all your `.py` files except `bot.py`, `simulate.py` and `colorwars.py`, plus `requirements.txt` |
| `python3 bot.py --dry-run` | Practice arena: prints the checks and the live link |
| `python3 bot.py` | Waits for LIVE, then plays the match |

Join is open in LOBBY only. Uploads are open in LOBBY, BUILD, TESTING and the strategy windows. The server installs `requirements.txt` once, at upload. A failed upload keeps your last good one. The arena runs Python 3.12; the kit prints a warning on any other version.

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
| `Put your Miro token in .env first` | `.env` has no `MIRO_TOKEN=` line | Copy `.env.example` to `.env` and put your Miro token after `MIRO_TOKEN=` |
| `join failed: Miro refused this token` | The token is wrong or the app was deleted | Copy the token again from **Your apps** |
| `join failed: ... not for the class team` | The app is installed to another team | Install the app to **ASU CIS** and copy the new token |
| `join failed: joining is closed` | BUILD has started | Ask the instructor |
| `HTTP 401` or `HTTP 403` on `--check` | The key is wrong or not loaded | Run `python3 bot.py --login` again |
| `HTTP 403` on a move, then `Laptop play is over` | The move is not for your current match, or the round robin has started | The script stops. In the round robin this is expected: your upload plays. In round 0, run `python3 bot.py` again |
| `HTTP 429` | Too many requests | Raise `refresh_every` in `config.json`. The starter kit retries on its own |
| `warning: this is Python 3.x` | Your Python is not 3.12 | Install Python 3.12 and run the kit with it |
| `upload refused` | `strategy.py` does not import, `choose` failed, or `requirements.txt` did not install | Fix the error it prints and run `--submit` again |
| `practice failed: ... practice_used` | You already sent your one practice move | Nothing to fix |
| The script prints `waiting` after the phase is LIVE | A board read is in progress | Wait a few seconds. The script reads every 2 seconds |
| `KIT-WARN reverted` with `illegal` | Your opponent took the square next to it since the last read | Take squares from `legal` only, or lower `refresh_every` |
| `KIT-WARN reverted` with `cooldown` | A second program is sending moves with your key | Close every other copy of `bot.py` |
| Your squares turn empty in a block | Your opponent cut your supply line | Your strategy needs a wider line or a defense rule. This is a strategy problem, not a bug |
| KIT-ERROR match already live, not starting | A kit file changed after LIVE, or the script never ran before LIVE | Run the script after your last edit and before LIVE. During a match there is no fix |
