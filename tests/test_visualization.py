# -*- coding: utf-8 -*-
try:
    import unittest2 as unittest  # to support Python 2.6
except ImportError:
    import unittest

from os.path import isfile
from .utils import (get_temp_filepath, remove_temp_file, load_fixture)
from gazelib.containers import CommonV1
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

    def test_render_overview_without_errors(self):
        raw = load_fixture('sample.common.json')
        c = CommonV1(raw)
        fpath = get_temp_filepath('myfile.html')
        unit.common.render_overview(c, fpath)
        isfile(fpath)
        remove_temp_file(fpath)

if __name__ == '__main__':
    unittest.main()
