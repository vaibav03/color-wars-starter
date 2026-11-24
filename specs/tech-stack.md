# Tech stack

- Language: Python 3.12, and no other version. The kit stops on every other version, and the arena runs 3.12.
- Libraries: the standard library, and the two helpers `neighbors` and `distance_map` from `colorwars.py`. A library you add goes in `requirements.txt`; the server installs it once, at upload.
- Your code: `strategy.py`, and any `.py` file you add beside it.
- The kit's code: `bot.py`, `simulate.py`, `colorwars.py`, `config.json` and `tools/`. Nobody edits these. The bot records their hashes before the match and does not start a match with changed files.
- Tests: `unittest` from the standard library, in `tests/`, run with `python3 -m unittest discover -s tests`.
- Checks: the offline simulator `simulate.py`, the fake server in `tools/`, and the practice arena (`python3 bot.py --dry-run`). `harness-spec.md` lists them.
- Limits: `choose` gets 0.5 seconds per move in the arena. The server accepts one move per second.
- Secrets: the player key lives in `.env`. It is never printed and never put in a command.
- No model calls in the script: it plays alone.
