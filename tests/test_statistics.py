try:
    import unittest2 as unittest  # to support Python 2.6
except ImportError:
    import unittest

from gazelib import statistics as unit

class TestUtils(unittest.TestCase):

    def test_deltas(self):

        l = [1, 2, 3, 4, 5]
        self.assertListEqual(unit.utils.deltas(l), [1, 1, 1, 1])
        l = [-1, 0, 1, 2]
        self.assertListEqual(unit.utils.deltas(l), [1, 1, 1])
        l = [1, 0, 1, 0, -1]
        self.assertListEqual(unit.utils.deltas(l), [-1, 1, -1, -1])

    def test_arithmetic_mean(self):

        l = [1, 2, 3]
        self.assertEqual(unit.utils.arithmetic_mean(l), 2.0)
        l = []
        self.assertEqual(unit.utils.arithmetic_mean(l), None)
        l = [None, 1]
        self.assertEqual(unit.utils.arithmetic_mean(l), 1.0)

    def test_weighted_arithmetic_mean(self):

        l = [1, 5, 1]
        w = [1, 0, 1]
        self.assertEqual(unit.utils.weighted_arithmetic_mean(l, w), 1.0)
        l = [2, 5, 0]
        w = [1, None, 1]
        self.assertEqual(unit.utils.weighted_arithmetic_mean(l, w), 1.0)

if __name__ == '__main__':
    unittest.main()
