# -*- coding: utf-8 -*-
try:
    import unittest2 as unittest  # to support Python 2.6
except ImportError:
    import unittest

from .utils import load_fixture, assert_deep_equal

from gazelib.containers import CommonV1
from gazelib import models as unit


class TestSaccade(unittest.TestCase):

    def test_empty_common(self):
        c = CommonV1()
        f = lambda: unit.saccade.fit(c)
        self.assertRaises(CommonV1.InsufficientDataException)

    def test_empty_saccade(self):
        raw = load_fixture('saccade_empty.common.json')
        c = CommonV1(raw)
        f = lambda: unit.saccade.fit(c)
        self.assertRaises(CommonV1.InsufficientDataException, f)

    # def test_fixture_saccade(self):
    #     raw = load_fixture('saccade.common.json')
    #     c1 = CommonV1(raw)
    #     c2 = c1.slice_by_tag('icl/experiment/reaction/period/target')
    #     t0 = c2.get_relative_start_time()
    #     # First second
    #     c3 = c2.slice_by_relative_time(t0, t0 + 1000000)
    #     r = unit.saccade.fit(c3)
    #     assert_deep_equal(self, r, {
    #         'type': 'gazelib/gaze/saccade',
    #         'start_time_relative': 123,
    #         'end_time_relative': 321,
    #         'mean_squared_error': 0.123
    #     })


class TestFixation(unittest.TestCase):
    pass

if __name__ == '__main__':
    unittest.main()
