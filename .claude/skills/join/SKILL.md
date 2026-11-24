---
name: join
description: Join the Color Wars game. Use when the student types /join or asks how to log in, join, or get a player key.
---

Walk the student through joining. Do each step in order.

1. Run `python3 bot.py --login` in the kit folder.
   - `joined as ...`: tell the student their dashboard name and the watch link it printed. Go to step 2.
   - `Log in to Claude Code first`: ask the student to type `/login` and sign in, then run
     step 1 again.
   - `joining is closed`: BUILD has started. Tell the student to ask the instructor. Stop.
2. Run `python3 bot.py --check` and confirm it prints `connected`.
3. Tell the student the next step: write `strategy.py`, test with `python3 simulate.py --watch`, upload with
   `python3 bot.py --submit` before BUILD ends. They start `python3 bot.py` themselves before round 0, not you.

Never print the player key from `.env`. Do not tell the student anything about groups.
