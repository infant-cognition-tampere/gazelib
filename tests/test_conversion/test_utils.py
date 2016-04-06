# -*- coding: utf-8 -*-
try:
    import unittest2 as unittest  # to support Python 2.6
except ImportError:
    import unittest

from gazelib.conversion import utils as unit
split = unit.split_to_ranges_at_change_in_value

class TestEstimateSamplingInterval(unittest.TestCase):

    def test_basic(self):
        interval = unit.estimate_sampling_interval([1,2])
        self.assertEqual(interval, 1)

    def test_empty(self):
        interval = unit.estimate_sampling_interval([])
        self.assertEqual(interval, None)

class TestSplitToRangesAtChangeInValue(unittest.TestCase):

    def test_value_error(self):

        def value_converter(r):
            return int(r['a'])

        def time_converter(r):
            return r['t']

        rows = [
            {'t': 1, 'a': ''},
            {'t': 2, 'a': '1'},
            {'t': 3, 'a': ''}
        ]
        slices = list(split(rows, value_converter, time_converter))
        self.assertEqual(len(slices), 1)
        self.assertEqual(slices[0]['start'], 2)
        self.assertEqual(slices[0]['end'], 3)
        self.assertEqual(slices[0]['value'], 1)
        self.assertEqual(slices[0]['first']['t'], 2)

        rows = [
            {'t': 1, 'a': ''},
            {'t': 2, 'a': '1'}
        ]
        slices = list(split(rows, value_converter, time_converter))
        self.assertEqual(len(slices), 1)
        self.assertEqual(slices[0]['start'], 2)
        self.assertEqual(slices[0]['end'], 3)
        self.assertEqual(slices[0]['value'], 1)
        self.assertEqual(slices[0]['first']['t'], 2)
