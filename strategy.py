"""Your strategy. This is the only code file you edit.

The starter kit calls choose() once per second and paints the square you return.

Inputs
  board          dict: every square label -> "me", "enemy", "empty", "wall" or "bomb"
  legal          list: the squares you can capture right now
  my_crystal     list: your four crystal squares
  enemy_crystal  list: your opponent's four crystal squares
  reverted       list: squares the referee took back from you since the last board read

Return one label from `legal`, for example "G17".

Helpers you may use:
  neighbors(label)            the squares touching a square
  distance_map(board, goals)  steps from every square to the nearest goal, around walls

Strategy: try each legal square and score what the capture would do.
  - territory: squares we gain plus enemy squares we take or cut off from their crystal
  - win: owning all four enemy crystal squares ends the match
  - defence: enemy squares close to our crystal are worth extra
  - shape: squares touching several of ours make a wide line that one cut cannot break
  - direction: among equal moves, head for the enemy crystal (claim the middle first)
"""
from collections import deque

from colorwars import neighbors, distance_map, parse, name

_recent = deque(maxlen=12)     # our last picks, to break back-and-forth loops
_state = {"moves": 0, "phase": "expand", "lane": None}

EXPAND_SQUARES = 60            # switch to the raid once we own this many squares...
EXPAND_MOVES = 90              # ...or after this many moves, whichever comes first
HOME_RADIUS = 7                # the expand half stays within this many steps of our crystal
DANGER_STEPS = 3              # an enemy square this close to our crystal means danger


def _phase(board):
    """'expand' in the first half, 'flank' in the second. Resets on a fresh match."""
    mine = sum(o == "me" for o in board.values())
    if mine <= 6 and _state["moves"] > 10:           # a new match started: forget the old one
        _state.update(moves=0, phase="expand", lane=None)
        _recent.clear()
    _state["moves"] += 1
    if _state["phase"] == "expand" and (mine >= EXPAND_SQUARES or _state["moves"] > EXPAND_MOVES):
        _state["phase"] = "flank"
    return _state["phase"]


def _connected(board, crystal, who):
    seen = {c for c in crystal if board.get(c, who) == who}
    todo = deque(seen)
    while todo:
        for n in neighbors(todo.popleft()):
            if n not in seen and board.get(n) == who:
                seen.add(n)
                todo.append(n)
    return seen


def _area(square, board):
    """The squares that become ours when we take `square` (a bomb takes its 3x3 block)."""
    if board[square] != "bomb":
        return [square]
    x, y = parse(square)
    out = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            q = name((x + dx, y + dy))
            if parse(q) == (x + dx, y + dy) and q in board and board[q] not in ("wall", "me"):
                out.append(q)
    return out


def _in_center(square):
    """The central front: columns L to Y, rows 14 to 21."""
    x, y = parse(square)
    return 11 <= x <= 24 and 14 <= y <= 21


def _flank_map(board, enemy_crystal):
    """Steps to the enemy crystal through one side lane, with the central front walled off."""
    if _state["lane"] is None:                        # pick the emptier lane once, then keep it
        top = sum(o == "enemy" and parse(s)[1] <= 13 for s, o in board.items())
        bottom = sum(o == "enemy" and parse(s)[1] >= 22 for s, o in board.items())
        _state["lane"] = "top" if top <= bottom else "bottom"
    blocked = dict(board)
    for s in board:
        x, y = parse(s)
        if 11 <= x <= 24 and (14 <= y <= 21 or (y >= 22 if _state["lane"] == "top" else y <= 13)):
            blocked[s] = "wall"
    return distance_map(blocked, enemy_crystal)


def choose(board, legal, my_crystal, enemy_crystal, reverted):
    to_enemy = distance_map(board, enemy_crystal)
    to_home = distance_map(board, my_crystal)
    enemy_now = _connected(board, enemy_crystal, "enemy")
    enemy_count = len(enemy_now)
    crystal_left = sum(board.get(c) != "me" for c in enemy_crystal)
    skip = set(reverted)
    phase = _phase(board)

    if crystal_left == 1:                             # 1. the last enemy crystal square wins
        for s in legal:
            if s in enemy_crystal:
                _recent.append(s)
                return s
    near = {s for s in enemy_now if to_home.get(s, 99) <= DANGER_STEPS}
    if near:                                          # 2. our crystal is in danger: defend first
        def relief(s):                                # (danger squares removed, all removed)
            after = dict(board)
            for q in _area(s, board):
                after[q] = "me"
            left = _connected(after, enemy_crystal, "enemy")
            return (len(near - left), enemy_count - len(left))
        options = [s for s in legal if board[s] == "enemy"]
        best = max(options, key=lambda s: (relief(s), -to_home.get(s, 99), s not in skip), default=None)
        if best is not None and relief(best)[0] > 0:
            _recent.append(best)
            return best                               # the deepest cut that clears the danger

    flank = _flank_map(board, enemy_crystal) if phase == "flank" else {}

    def expand_score(s):
        area = _area(s, board)
        d = to_home.get(s, 99)
        value = float(len(area)) * 1.5                # squares we gain (a bomb gains many)
        own = sum(board.get(n) == "me" for n in neighbors(s))
        value += 0.5 * own                            # thick blob, no thin fingers
        value -= 0.4 * d                              # fill near home first
        if board[s] == "empty" and any(board.get(n) == "enemy" for n in neighbors(s)):
            value += 1.0                              # hug an enemy finger, so we can cut it deep
        if d > HOME_RADIUS:
            value -= 20                               # stay home in the first half
        if s in skip:
            value -= 5
        value -= 1.0 * _recent.count(s)
        return (value, -d)

    def score(s):
        area = _area(s, board)
        took = [q for q in area if board[q] == "enemy"]
        value = float(len(area))                     # squares we gain
        if took:                                      # enemy squares lost, incl. cut-off ones
            after = dict(board)
            for q in area:
                after[q] = "me"
            lost = enemy_count - len(_connected(after, enemy_crystal, "enemy"))
            value += lost
            if lost <= len(took):                     # no cut: they can simply take it back
                value -= 0.5
        if s in enemy_crystal:
            value += 50 if crystal_left == 1 else 6
        for q in took:                                # defend home
            d = to_home.get(q, 99)
            if d <= 6:
                value += (7 - d) * 1.5
        own = sum(board.get(n) == "me" for n in neighbors(s))
        value += 0.3 * own                            # wide, compact line
        if s in skip:
            value -= 5
        value -= 1.0 * _recent.count(s)              # stop trading the same square forever
        if _in_center(s):
            value -= 3                                # keep off the central front
        return (value, -flank.get(s, 999), -to_enemy.get(s, 999))

    pick = max(legal, key=expand_score if phase == "expand" else score)
    _recent.append(pick)
    return pick
