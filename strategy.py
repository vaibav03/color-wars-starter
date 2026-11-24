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


def choose(board, legal, my_crystal, enemy_crystal, reverted):
    to_enemy = distance_map(board, enemy_crystal)
    to_home = distance_map(board, my_crystal)
    enemy_now = _connected(board, enemy_crystal, "enemy")
    enemy_count = len(enemy_now)
    crystal_left = sum(board.get(c) != "me" for c in enemy_crystal)
    skip = set(reverted)

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
        return (value, -to_enemy.get(s, 999))

    pick = max(legal, key=score)
    _recent.append(pick)
    return pick
