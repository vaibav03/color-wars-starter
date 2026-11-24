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
3. Next, start the workflow with `sdlc:intent`. Tell the student: "You are in. Next, start the workflow: type
   `/sdlc:intent` and your idea for the strategy, for example `/sdlc:intent defend my crystal and take bombs`."
   - If the student already said in this conversation what the strategy should do, start the skill `sdlc:intent`
     yourself, with their words as its arguments.
   - Otherwise stop there and wait. Do not start it with no idea from the student, and do not invent one.
   Do not edit `strategy.py` in this skill. The upload (`python3 bot.py --submit`, before BUILD ends) comes after
   the workflow's checks. The server plays the upload in all matches at once; nothing runs on the laptop.

Most students are not technical, so show results in the browser, not only in the terminal:
- Every time you simulate a match, add `--web` (for example `python3 simulate.py --web`) and run it in the
  background: it does not end by itself. It opens the match in the browser, and the student watches it play turn
  by turn. Tell the student the page is open, and the result in one plain sentence (won or lost, and the score).
- `python3 bot.py --submit` opens the student's dashboard page after `upload passed`. Tell the student in plain
  words that their strategy is uploaded; the page shows a green line that says so.

Never print the player key from `.env`. Do not tell the student anything about groups.
