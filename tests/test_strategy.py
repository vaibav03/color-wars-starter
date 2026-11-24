"""Tests of your strategy. Run them all with: python3 -m unittest discover -s tests

Add one test for each behaviour you give choose(). These files are not uploaded.
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from colorwars import legal_squares, view
from simulate import CRYSTALS, new_board
from strategy import choose


def opening(side):
    """What choose() receives on the first turn, playing `side` ("red" or "blue")."""
    other = "blue" if side == "red" else "red"
    board = view(new_board(), side)
    return board, legal_squares(board, CRYSTALS[side]), CRYSTALS[side], CRYSTALS[other]


class TestChoose(unittest.TestCase):
    def test_opening_move_is_legal(self):
        for side in ("red", "blue"):
            board, legal, mine, theirs = opening(side)
            self.assertIn(choose(board, legal, mine, theirs, []), legal)


if __name__ == "__main__":
    unittest.main()
