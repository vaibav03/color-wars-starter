"""Your strategy. This is the only code file you edit.

The starter kit calls choose() once per second and paints the square you return.

Inputs
  board          dict: every square label -> "me", "enemy", "empty", "wall" or "bomb"
  legal          list: the squares you can capture right now
  my_crystal     list: your five crystal squares
  enemy_crystal  list: your opponent's five crystal squares
  reverted       list: squares the referee took back from you since the last board read

Return one label from `legal`, for example "G17".

Helpers you may use:
  neighbors(label)            the squares touching a square
  distance_map(board, goals)  steps from every square to the nearest goal, around walls
"""
from colorwars import neighbors, distance_map


def choose(board, legal, my_crystal, enemy_crystal, reverted):
    # Sample strategy: take the legal square closest to the enemy crystal.
    # It never defends, ignores bombs, and builds a line one square wide.
    steps = distance_map(board, enemy_crystal)
    return min(legal, key=lambda square: steps.get(square, 999))
