# -*- coding: utf-8 -*-
from gazelib.legacy import igazelib as gazelib
try:
    import unittest2 as unittest  # to support Python 2.6
except ImportError:
    import unittest
import os

def assertListAlmostEqual(self, lst1, lst2, msg=None):
    '''
    Parameters
        self
            A unittest.TestCase instance
    '''
    if len(lst1) != len(lst2):
        self.fail(msg)
    for e1, e2 in zip(lst1, lst2):
        self.assertAlmostEqual(e1, e2)

class TestGazelibMethods(unittest.TestCase):

    data = [
        {'x':0.1, 'y':-1, 'xval':1, 'yval':8, 'tag':'target', 'time':1},
        {'x':0.4, 'y':0.1, 'xval':1, 'yval':1, 'tag':'target', 'time':2},
        {'x':0.4, 'y':0.7, 'xval':1, 'yval':1, 'tag':'', 'time':3},
        {'x':0.8, 'y':0.2, 'xval':1, 'yval':2, 'tag':'target2', 'time':4},
        {'x':-1, 'y':-1, 'xval':4, 'yval':3, 'tag':'target2', 'time':5},
        {'x':0.1, 'y':0.2, 'xval':1, 'yval':1, 'tag':'target2', 'time':6}
    ]

    # Two eyes
    # combined x: 0.1, 0.3, 0.3, 0.8, -1, 0.1
    data2 = [
        {'rx':0.1, 'ry':0.3, 'lx':-1,  'ly':-1,  'rval':1, 'lval':8, 'tag':'target', 'time':1},
        {'rx':0.4, 'ry':0.1, 'lx':0.2, 'ly':0.1, 'rval':1, 'lval':1, 'tag':'target', 'time':2},
        {'rx':0.4, 'ry':0.7, 'lx':0.2, 'ly':0.9, 'rval':1, 'lval':1, 'tag':'', 'time':3},
        {'rx':0.8, 'ry':0.2, 'lx':0.8, 'ly':0.2, 'rval':1, 'lval':2, 'tag':'target2', 'time':4},
        {'rx':-1,  'ry':-1,  'lx':-1,  'ly':-1,  'rval':4, 'lval':3, 'tag':'target2', 'time':5},
        {'rx':0.1, 'ry':0.2, 'lx':0.1, 'ly':0.2, 'rval':1, 'lval':1, 'tag':'target2', 'time':6}
    ]

    def test_selections(self):
        data = TestGazelibMethods.data

        # get value works with some input
        self.assertEqual(gazelib.get_value(data, 3, 'x'), 0.8)

        # check if right amount of rows returned after selection
        clip = gazelib.first_gazepoints_by_time(data, 'time', 2)
        self.assertEqual(len(clip), 2)
        self.assertEqual(gazelib.get_value(clip, 0, 'time'), 1)

        clip = gazelib.first_gazepoints(data, 3)
        self.assertEqual(len(clip), 3)
        self.assertEqual(gazelib.get_value(clip, 0, 'time'), 1)

        clip = gazelib.gazepoints_after_time(data, 'time', 3)
        self.assertEqual(len(clip), 3)
        self.assertEqual(gazelib.get_value(clip, 0, 'time'), 4)

        clip = gazelib.gazepoints_containing_value(data, 'tag', ['definately_not_there', 'target2'])
        self.assertEqual(len(clip), 3)
        self.assertEqual(gazelib.get_value(clip, 1, 'time'), 5)

        clip = gazelib.gazepoints_not_containing_value(data, 'tag', ['target2'])
        self.assertEqual(len(clip), 3)
        self.assertEqual(gazelib.get_value(clip, 2, 'time'), 3)


    def test_split(self):
        data = TestGazelibMethods.data

        # data splitting when change in key
        data_splitted = gazelib.split_at_change_in_value(data, 'tag')
        self.assertEqual(len(data_splitted[0]), 2)
        self.assertEqual(len(data_splitted[1]), 1)
        self.assertEqual(len(data_splitted[2]), 3)
        # test the first value of one of the clips
        self.assertEqual(gazelib.get_value(data_splitted[1], 0, 'time'), 3)

    def test_filter_and_interpolation(self):
        data = TestGazelibMethods.data

        # median filter (for vector)
        filtered = gazelib.median_filter(gazelib.get_key(data, 'x'), 3)
        correct_filtered = [0.1, 0.4, 0.4, 0.4, 0.1, 0.1]
        self.assertListEqual(filtered, correct_filtered)
        #print(gazelib.get_key(data, 'x'))
        gazelib.add_key(data, 'x', correct_filtered)
        #print(gazelib.get_key(data, 'x'))
        self.assertListEqual(gazelib.median_filter_data(data, 3, 'x'),
                             gazelib.add_key(data, 'x', correct_filtered))

        # interpolation
        self.assertListEqual(gazelib.get_key(
            gazelib.interpolate_using_last_good_value(data, 'x', 'xval', [1,0]), 'x'),
            [0.1, 0.4, 0.4, 0.8, 0.8, 0.1])


    def test_keyadd(self):
        data = TestGazelibMethods.data

        # adding keys
        data2 = gazelib.add_key(data, 'z', len(data)*[-1])
        self.assertEqual(gazelib.get_value(data2, 4, 'z'), -1)

        # adding insuffisiently long vector of values produces error
        with self.assertRaises(IndexError):
            gazelib.add_key(data, 'z', [1,2,3])


        # metrics calculations
        self.assertEqual(gazelib.duration(data, 'time'), 5)
        self.assertEqual(gazelib.longest_non_valid_streak(data, 'yval', 'time', [0,1]), 2)

    def test_aoi(self):
        data = TestGazelibMethods.data

        # aoi-specific methods
        aoi = {"x1":0.35, "x2":0.45, "y1":0.05, "y2":0.8}
        self.assertAlmostEqual(gazelib.gaze_inside_aoi_percentage(data, 'x', 'y', aoi), float(1)/3)
        self.assertEqual(gazelib.gaze_inside_aoi(data, 'x', 'y', aoi, 'first'), 1)
        self.assertEqual(gazelib.gaze_inside_aoi(data, 'x', 'y', aoi, 'last'), 2)
        self.assertTrue(gazelib.border_violation(data, aoi, 'x', 'y', 'yval', [1]))
        self.assertFalse(gazelib.border_violation(data, aoi, 'x', 'y', 'xval', [1]))

    def test_validity(self):
        data = TestGazelibMethods.data

        # validity
        self.assertAlmostEqual(gazelib.valid_gaze_percentage(data, 'yval', [1]), 0.5)

    def test_grouping_and_combination(self):
        data = TestGazelibMethods.data

        # eye-combination tests
        self.assertAlmostEqual(gazelib.mean_of_valid_values([0.4, 0.2], [3, 1], [1]), 0.2)
        self.assertAlmostEqual(gazelib.mean_of_valid_values([0.4, 0.2, 0], [1, 1, 2], [1,2]), 0.2)
        self.assertAlmostEqual(gazelib.mean_of_valid_values([0.4], [1], [1]), 0.4)
        self.assertAlmostEqual(gazelib.mean_of_valid_values([0.4], [2], [1]), -1)

        xs, ys, vals = gazelib.combine_coordinates(TestGazelibMethods.data2,
            [0, 1], 'rx', 'ry', 'rval', 'lx', 'ly', 'lval')
        assertListAlmostEqual(self, xs, [0.1, 0.3, 0.3, 0.8, -1, 0.1])

        # grouping test
        grouping = gazelib.group(data, 'tag', 'time')
        self.assertDictEqual(grouping, {'': [3], 'target2': [4, 5, 6], 'target': [1, 2]})

        # make just an arbitary "list of data-lists"
        extra1 = [{'x':0.5, 'y':0.15, 'tag':'target'},{'x':0.3, 'y':0.1, 'tag':'target'}]
        extra2 = [{'x':0.7, 'y':0.4, 'tag':'test'}]
        datas = [data, extra1, extra2]
        grouping = gazelib.group_lists(datas, 'tag')
        self.assertDictEqual(grouping, {'test':extra2, 'target': data + extra1})

        rtimes = [105, 120, 130, 1003]
        #print(gazelib.SRT_index(rtimes, 1000, 100))
        #self.assertEqual(SRT_index(rtimes, 1000, 100), 100)

    def test_replace(self):
        data = TestGazelibMethods.data

        data_replaced = gazelib.replace_value(data, 'tag', 'target', 'target3')
        data_replaced_correct = data[:]
        data_replaced_correct[0]['tag'] = 'target3'
        data_replaced_correct[1]['tag'] = 'target3'
        self.assertListEqual(data_replaced, data_replaced_correct)
        #data_replaced_correct[1]['tag'] = 'target3'
        #self.assertListEqual(data_replaced, data_replaced_correct)

if __name__ == '__main__':
    unittest.main()
