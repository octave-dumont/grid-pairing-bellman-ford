import os
import sys
import unittest

CURRENT_DIR = os.path.dirname(__file__)
SRC_DIR = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
sys.path.append(SRC_DIR)

from gridpairing import Grid


# Testing the following methods from the Grid class:
# - test_pair()
# - all_pairs()
# - is_forbidden()


class TestValidPairs(unittest.TestCase):

    def setUp(self):
        self.grid = Grid.grid_from_file("input/grid01.in", read_values=True)

    def test_validity_of_pairs(self):
        pairs = self.grid.all_pairs()
        for (c1, c2) in pairs:
            self.assertTrue(self.grid.test_pair(c1, c2), f"Pair {c1}-{c2} should be valid")

    def test_black_cells_not_in_pairs(self):
        black_cells = [(i, j) for i in range(self.grid.n) for j in range(self.grid.m) if self.grid.is_forbidden(i, j)]
        for pair in self.grid.all_pairs():
            self.assertNotIn(pair[0], black_cells)
            self.assertNotIn(pair[1], black_cells)

if __name__ == "__main__":
    unittest.main()
