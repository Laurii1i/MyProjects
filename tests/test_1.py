import unittest

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from GlobalElements.Languages import Lang

class TestDataTransformation(unittest.TestCase):

    def test_runko(self):
        self.assertEqual(0, 0)
        self.assertEqual(1, 1)

    def test_Lang(self):
        self.assertEqual(Lang.FI, 0)
        self.assertEqual(Lang.SV, 1)
        self.assertEqual(Lang.EN, 2)


if __name__ == '__main__':
    unittest.main()