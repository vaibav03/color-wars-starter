#!/usr/bin/env python3
"""Offline Color Wars: run your strategy against a sample opponent. No network, no token.

  python3 simulate.py                     you are Red, 600 turns (10 minutes at one capture per second)
  python3 simulate.py --side blue         play from the Blue crystal instead
  python3 simulate.py --opponent random   an opponent that takes random legal squares
  python3 simulate.py --opponent house    the practice arena's house bot: grabs bombs and defends
  python3 simulate.py --turns 100 --map   a short match, with the final board printed
  python3 simulate.py --watch             watch the match: the board is drawn again every 10 turns

The simulator applies the match rules: adjacency, walls, bombs, supply lines, and the three
ways to win. It does not model network delay or referee reverts.

The last line is "RESULT win|loss|draw <your squares>-<opponent's squares> <reason>". The exit
code is 0 for any finished match, and 1 when choose raised an error or returned an illegal square.
"""
import argparse, random, sys, time

from colorwars import (ALL_SQUARES, COLS, ROWS, name, capture, distance_map, legal_squares,
                       neighbors, safe_choose, threat, view)

CRYSTALS = {"red": ["B17", "B18", "C17", "C18"], "blue": ["AH17", "AH18", "AI17", "AI18"]}


def new_board():
    owner = {s: "empty" for s in ALL_SQUARES}
    for x in (7, 28):                                   # columns H and AC
        for y in list(range(4, 13)) + list(range(23, 32)):
            owner[name((x, y))] = "wall"
    for x in (17, 18):                                  # columns R and S
        for y in (15, 16, 19, 20):
            owner[name((x, y))] = "wall"
    for s in ("R3", "S3", "L9", "Y9", "G17", "AD17", "L26", "Y26", "R32", "S32"):
        owner[s] = "bomb"
    for who, crystal in CRYSTALS.items():
        for s in crystal:
            owner[s] = who
    return owner


def sample_opponent(board, legal, my_crystal, enemy_crystal, reverted):
    steps = distance_map(board, enemy_crystal)
    return min(legal, key=lambda s: steps.get(s, 999))


def random_opponent(board, legal, my_crystal, enemy_crystal, reverted):
    return random.choice(legal)


def house_opponent(board, legal, my_crystal, enemy_crystal, reverted):
    """The house bot: the square that gains the most (bombs, cuts, defence near home), else nearest the target."""
    crystals = {"me": my_crystal, "enemy": enemy_crystal}
    steps, home = distance_map(board, enemy_crystal), distance_map(board, my_crystal)
    mine, theirs = count(board, "me"), count(board, "enemy")
    def score(s):
        after = dict(board)
        capture(after, "me", s, crystals)
        cut = theirs - count(after, "enemy") - (board[s] == "enemy")    # enemy squares cut off
        defend = board[s] == "enemy" and home.get(s, 99) <= 6
        gain = count(after, "me") - mine + 2 * cut + 2 * defend
        return (-gain, board[s] == "enemy", steps.get(s, 999))
    return min(legal, key=score)


OPPONENTS = {"sample": sample_opponent, "random": random_opponent, "house": house_opponent}


def require_python():
    if sys.version_info[:2] != (3, 12):
        v = ".".join(map(str, sys.version_info[:3]))
        sys.exit(f"Python 3.12 is required (this is Python {v}). Install it from python.org or with "
                 f"`brew install python@3.12`, then run the kit with python3.12, e.g. python3.12 {sys.argv[0]}")


def count(owner, who):
    return sum(o == who for o in owner.values())


def draw(owner, me):
    marks = {me: "M", "empty": ".", "wall": "#", "bomb": "*"}
    for y in range(1, ROWS + 1):
        print("".join(marks.get(owner[name((x, y))], "x") for x in range(COLS)))


def frame(owner, me, foe, turn, every, delay):
    """One --watch frame: clear the terminal, then the turn, the counts and the board."""
    print("\033[2J\033[H", end="")
    print(f"turn {turn:4d}  you (M) {count(owner, me):4d}  opponent (x) {count(owner, foe):4d}"
          f"   . empty  # wall  * bomb   (every {every} turns, Ctrl-C stops)")
    draw(owner, me)
    sys.stdout.flush()
    time.sleep(delay)


def main():
    ap = argparse.ArgumentParser(description="Offline Color Wars simulator")
    ap.add_argument("--side", choices=["red", "blue"], default="red")
    ap.add_argument("--opponent", choices=list(OPPONENTS), default="sample")
    ap.add_argument("--turns", type=int, default=600)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--map", action="store_true", help="print the final board (M you, x opponent)")
    ap.add_argument("--watch", type=int, nargs="?", const=10, default=0, metavar="N",
                    help="draw the board again every N turns (default 10) while the match plays")
    ap.add_argument("--delay", type=float, default=0.15, help="seconds to show each --watch frame")
    a = ap.parse_args()
    require_python()
    random.seed(a.seed)

    try:
        from strategy import choose
    except Exception as e:
        sys.exit(f"strategy.py does not load: {e}")

    me, foe = a.side, {"red": "blue", "blue": "red"}[a.side]
    brains = {me: choose, foe: OPPONENTS[a.opponent]}
    quiet = lambda *_: None
    faults = {"KIT-ERROR": 0, "KIT-WARN": 0}            # choose raised / returned an illegal square

    def report(line):                                   # print the first three of each kind only
        kind = line.split()[0]
        faults[kind] += 1
        if faults[kind] <= 3:
            print(line)

    owner, skipped, winner, reason = new_board(), 0, None, ""
    last_change, last_counts = 0, None              # the turn the territory counts last moved

    for turn in range(1, a.turns + 1):
        order = (me, foe) if turn % 2 else (foe, me)    # alternate who moves first
        for who in order:
            other = foe if who == me else me
            board = view(owner, who)
            legal = legal_squares(board, CRYSTALS[who])
            pick = safe_choose(brains[who], board, legal, CRYSTALS[who], CRYSTALS[other], [],
                               log=report if who == me else quiet)
            if pick is None:
                skipped += who == me
                continue
            capture(owner, who, pick, CRYSTALS)
            if all(owner[s] == who for s in CRYSTALS[other]):
                winner, reason = who, f"captured the crystal on turn {turn}"
                break
        if winner:
            break
        counts = (count(owner, me), count(owner, foe))
        if counts != last_counts:
            last_change, last_counts = turn, counts
        if a.watch and turn % a.watch == 0:
            frame(owner, me, foe, turn, a.watch, a.delay)
        elif turn % 100 == 0:
            print(f"turn {turn:4d}  you {count(owner, me):4d}  opponent {count(owner, foe):4d}")

    mine, theirs = count(owner, me), count(owner, foe)
    if not winner:
        if mine != theirs:
            winner, reason = (me if mine > theirs else foe), "more territory at the end"
        else:
            t_me, t_foe = threat(owner, me, CRYSTALS), threat(owner, foe, CRYSTALS)
            if t_me != t_foe:
                winner, reason = (me if t_me < t_foe else foe), "lower crystal threat score"
            else:
                reason = "tied on territory and on threat score"
    if a.watch:
        frame(owner, me, foe, turn, a.watch, 0)
    elif a.map:
        draw(owner, me)
    if not winner and turn - last_change >= 50:
        print(f"note: the territory counts did not change after turn {last_change}: neither side gained ground. "
              f"Run with --map to see where the front line is stuck.")
    if skipped:
        print(f"note: your strategy had no legal square on {skipped} turns")
    print(f"final: you {mine}, opponent {theirs}; "
          f"threat on your crystal {threat(owner, me, CRYSTALS):.2f}, on theirs {threat(owner, foe, CRYSTALS):.2f}")
    if faults["KIT-ERROR"]:
        print(f"choose raised an error on {faults['KIT-ERROR']} turns; the first legal square was taken instead")
    if faults["KIT-WARN"]:
        print(f"choose returned an illegal square on {faults['KIT-WARN']} turns; the first legal square was taken instead")
    print("RESULT", "draw" if not winner else ("win" if winner == me else "loss"), f"{mine}-{theirs}", reason)
    if faults["KIT-ERROR"] or faults["KIT-WARN"]:
        sys.exit(1)                                     # a strategy fault is a failed run, win or lose


if __name__ == "__main__":
    main()
