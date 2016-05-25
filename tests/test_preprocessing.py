# -*- coding: utf-8 -*-
try:
    import unittest2 as unittest  # to support Python 2.6
except ImportError:
    import unittest

from gazelib import preprocessing as unit


class TestPreprocessing(unittest.TestCase):

    def test_fill_gaps(self):

        a = [1, None, 2]
        b = [None, 1, 2]
        c = [None, None, None]
        fa = unit.fill_gaps(a)
        self.assertEqual(fa, [1, 1, 2])
        fb = unit.fill_gaps(b)
        self.assertEqual(fb, [1, 1, 2])

        f = lambda: unit.fill_gaps(c)
        self.assertRaises(unit.ExtrapolationError, f)


if __name__ == '__main__':
    unittest.main()
