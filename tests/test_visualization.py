# -*- coding: utf-8 -*-
try:
    import unittest2 as unittest  # to support Python 2.6
except ImportError:
    import unittest

import gazelib.visualization as unit

class TestUtils(unittest.TestCase):

    def test_get_valid_sublists(self):
        l = [None, 1, None, 2]
        sl = unit.utils.get_valid_sublists(l)
        self.assertEqual(len(sl), 2)
        self.assertEqual(sl[0], [1])
        self.assertEqual(sl[1], [2])

        l = []
        sl = unit.utils.get_valid_sublists(l)
        self.assertEqual(sl, [])

if __name__ == '__main__':
    unittest.main()
