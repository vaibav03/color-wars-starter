# Mission

You build a script that plays Color Wars against one opponent at a time, with no human input. The script is one function, `choose` in `strategy.py`, which picks the next square to capture once per second.

## For whom

- You, the player: your script plays your matches while you watch.
- The game server, the referee: it checks every move and decides every match.

## What success looks like

- The script runs for the whole match without stopping: `choose` never raises an error and never returns a square that is not legal.
- The script wins: it captures the opponent's crystal, or it owns more squares when the match ends.
- Every change to the strategy is checked in the offline simulator before it is uploaded.

The rules of the game and the timeline of the session are in `BRIEF.md`.
