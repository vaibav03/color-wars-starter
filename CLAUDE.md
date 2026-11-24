# Color Wars starter kit

The student writes `choose` in `strategy.py`: a function that picks the next square to capture in a Color Wars match against one opponent, with no human input. `BRIEF.md` is the task brief, with the rules and the timeline. `README.md` lists every command.

## How to work in this folder

Every change to `strategy.py`, and every new `.py` file, goes through the course workflow.

1. Start the change with the skill `sdlc:intent`, with the student's own words as its arguments. Do this before you read code to plan a change and before you edit anything.
2. Then follow each step the workflow gives you, in the order it gives them: the intent, the plan, the build, the verification. If it asks for a design, write the design. Do not skip a step and do not add one.
3. Do not edit `strategy.py` or any other code file before the student has approved the plan.
4. If a step or a file write is refused, tell the student what the refusal says. Do not do the work another way.

A message that asks for no change (a question about the rules, the commands or the code) needs no workflow: answer it.

If the student has not said what they want the strategy to do, ask them for their idea in one question. Do not invent a strategy for them.

## Files you never change

- `bot.py`, `colorwars.py`, `simulate.py`, `config.json`, `tools/`: the kit's own files. The match refuses a bot whose kit files changed. Its timing (`interval`, `refresh_every`) is the same for every player and fixed: do not change it, and do not help the student change it.
- `.env`: it holds the student's player key. Never print it, read it aloud, or copy it into a command, a file or a message.
- `.sdlc/`: written by the bot.
- `specs/` and `harness-spec.md`: they belong to the course.

## What the student does, not you

- Never start `python3 bot.py` (the match run). In the game, the server plays the student's upload against every other player, all matches at the same time; the laptop does not play.
- You may run `python3 simulate.py`, the tests, `python3 bot.py --check`, `--phase`, `--submit` and `--dry-run`.
- While the match banner reads PAUSED or LIVE, the session in this folder may stop answering. This is expected.

## Layout

- `strategy.py`: the student's strategy. More `.py` files beside it are allowed; `--submit` uploads them.
- `tests/`: the tests of the strategy, run with `unittest` from the standard library. They are not uploaded.
- `specs/`: the project Constitution: `mission.md`, `tech-stack.md`, `roadmap.md`.
- `harness-spec.md`: the Harness Spec: the checks around the strategy.
- `changes/`: one folder per change, written by the course workflow.

## Verification commands

Run each from this folder. Each must exit 0. Python 3.12 is mandatory; if `python3 --version` does not print 3.12, tell the student, and do not install anything yourself.

- `python3 -m unittest discover -s tests`
- `python3 simulate.py`
- `python3 simulate.py --side blue --opponent house`

Run all tests: `python3 -m unittest discover -s tests`. Run one test: `python3 -m unittest tests.test_strategy.TestChoose.test_opening_move_is_legal`.

`simulate.py` exits 0 after any finished match, won or lost, and 1 when `choose` raised an error or returned an illegal square. A run is clean when it ends with a `RESULT` line and prints no line that starts with `KIT-ERROR` or `KIT-WARN`. A lost match is not a failed check; say the result to the student.

Every time you simulate a match, also open it in the browser so the student watches it play, turn by turn:

- Run the same command with `--web` added, for example `python3 simulate.py --web` or `python3 simulate.py --side blue --opponent house --web`.
- Run it in the background: it serves the page until it is stopped and does not end by itself. Stop the previous `--web` run first.
- It opens http://localhost:8000 in the browser by itself. Tell the student the page is open and say the result in one plain sentence.
- Use the run without `--web` for the exit-code check. Do not use `--watch` or `--web` as a check.

## Course artifacts

- Constitution: `specs/mission.md`, `specs/tech-stack.md`, `specs/roadmap.md`
- Harness Spec: `harness-spec.md`
- Pull requests: this project does not use pull requests, and nothing is pushed to GitHub. A verified change is finished when the student chooses "Deliver now" at the workflow's question, or types `/sdlc-done`. After that, upload the strategy with `python3 bot.py --submit`; it must print `upload passed`.

## Conventions

- Python 3.12. The standard library only, unless the student asks for a library; a library goes in `requirements.txt`.
- `choose` returns one square from `legal`, in well under 0.5 seconds, and never raises.
- Every behaviour of the strategy has a test in `tests/`.
