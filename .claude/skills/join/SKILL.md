---
name: join
description: Join the Color Wars game with the student's own Miro token. Use when the student types /join or asks how to log in, join, or get a player key.
---

Walk the student through joining. Do each step in order and wait for the student where a step needs them.

1. Check `.env` in the kit folder. If it has a non-empty `MIRO_TOKEN=` line, skip to step 4. Never print the token.
2. Tell the student to make a Miro app (they must do this in the browser; you cannot):
   - Miro, avatar, **Settings**, **Your apps**, **+ Create new app**. Name it `color-wars-<their name>`. Leave
     **Expire user authorization token** cleared. **Create app**.
   - Permissions: `boards:read` and `identity:read` only.
   - **Install app and get OAuth token**, team **ASU CIS**, **Install & authorize**, copy the token.
3. Ask the student to paste the token. Copy `.env.example` to `.env` if `.env` is missing, and put the token after
   `MIRO_TOKEN=`. Keep any `PLAYER_KEY=` line. Do not echo the token back.
4. Run `python3 bot.py --login`.
   - `joined as ...`: tell the student their dashboard name and the watch link it printed.
   - `Miro refused this token`: the token is wrong or the app was deleted. Go back to step 2 (copy it again).
   - `not for the class team`: the app is installed to another team. Reinstall it to **ASU CIS**, new token, step 3.
   - `joining is closed`: BUILD has started. Tell the student to ask the instructor. Stop.
5. Run `python3 bot.py --check` and confirm it prints `connected`.
6. Tell the student the next step: write `strategy.py`, test with `python3 simulate.py --watch`, upload with
   `python3 bot.py --submit` before BUILD ends. They start `python3 bot.py` themselves before round 0, not you.
