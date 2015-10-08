import unittest
from igazelib import *


class TestIgazelibMethods(unittest.TestCase):

    data = [
        {'x':0.1, 'y':-1, 'xval':1, 'yval':8, 'tag':'target', 'time':1},
        {'x':0.4, 'y':0.1, 'xval':1, 'yval':1, 'tag':'target', 'time':2},
        {'x':0.4, 'y':0.7, 'xval':1, 'yval':1, 'tag':'', 'time':3},
        {'x':0.8, 'y':0.2, 'xval':1, 'yval':2, 'tag':'target2', 'time':4},
        {'x':-1, 'y':-1, 'xval':4, 'yval':3, 'tag':'target2', 'time':5},
        {'x':0.1, 'y':0.2, 'xval':1, 'yval':1, 'tag':'target2', 'time':6} ]

    def test_selections(self):
        data = TestIgazelibMethods.data

        # get value works with some input
        self.assertEqual(get_value(data, 3, 'x'), 0.8)

        # check if right amount of rows returned after selection
        clip = first_gazepoints_by_time(data, 'time', 2)
        self.assertEqual(len(clip), 2)
        self.assertEqual(get_value(clip, 0, 'time'), 1)

        clip = first_gazepoints(data, 3)
        self.assertEqual(len(clip), 3)
        self.assertEqual(get_value(clip, 0, 'time'), 1)

        clip = gazepoints_after_time(data, 'time', 3)
        self.assertEqual(len(clip), 3)
        self.assertEqual(get_value(clip, 0, 'time'), 4)

        clip = gazepoints_containing_value(data, 'tag', ['definately_not_there', 'target2'])
        self.assertEqual(len(clip), 3)
        self.assertEqual(get_value(clip, 1, 'time'), 5)

        clip = gazepoints_not_containing_value(data, 'tag', ['target2'])
        self.assertEqual(len(clip), 3)
        self.assertEqual(get_value(clip, 2, 'time'), 3)


    def test_split(self):
        data = TestIgazelibMethods.data

        # data splitting when change in key
        data_splitted = split_at_change_in_value(data, 'tag')
        self.assertEqual(len(data_splitted[0]), 2)
        self.assertEqual(len(data_splitted[1]), 1)
        self.assertEqual(len(data_splitted[2]), 3)
        # test the first value of one of the clips
        self.assertEqual(get_value(data_splitted[1], 0, 'time'), 3)

    def test_filter_and_interpolation(self):
        data = TestIgazelibMethods.data

        # median filter (for vector)
        filtered = median_filter(get_key(data, 'x'), 3)
        correct_filtered = [0.1, 0.4, 0.4, 0.4, 0.1, 0.1]
        self.assertListEqual(filtered, correct_filtered)
        print get_key(data, 'x')
        add_key(data, 'x', correct_filtered)
        print get_key(data, 'x')
        self.assertListEqual(median_filter_data(data, 3, 'x'), add_key(data, 'x', correct_filtered))

        # interpolation
        self.assertListEqual(get_key(interpolate_using_last_good_value(data, 'x', 'xval', [1,0]), 'x'), [0.1, 0.4, 0.4, 0.8, 0.8, 0.1])


    def test_keyadd(self):
        data = TestIgazelibMethods.data

        # adding keys
        data2 = add_key(data, 'z', len(data)*[-1])
        self.assertEqual(get_value(data2, 4, 'z'), -1)

        # adding insuffisiently long vector of values produces error
        with self.assertRaises(IndexError):
            add_key(data, 'z', [1,2,3])


        # metrics calculations
        self.assertEqual(duration(data, 'time'), 5)
        self.assertEqual(longest_non_valid_streak(data, 'yval', 'time', [0,1]), 2)

    def test_aoi(self):
        data = TestIgazelibMethods.data

        # aoi-specific methods
        aoi = {"x1":0.35, "x2":0.45, "y1":0.05, "y2":0.8}
        self.assertAlmostEqual(gaze_inside_aoi_percentage(data, 'x', 'y', aoi), float(1)/3)
        self.assertEqual(gaze_inside_aoi(data, 'x', 'y', aoi, 'first'), 1)
        self.assertEqual(gaze_inside_aoi(data, 'x', 'y', aoi, 'last'), 2)
        self.assertTrue(border_violation(data, aoi, 'x', 'y', 'yval', [1]))
        self.assertFalse(border_violation(data, aoi, 'x', 'y', 'xval', [1]))

    def test_validity(self):
        data = TestIgazelibMethods.data

        # validity
        self.assertAlmostEqual(valid_gaze_percentage(data, 'yval', [1]), 0.5)

    def test_grouping_and_combination(self):
        data = TestIgazelibMethods.data

        # eye-combination tests
        self.assertAlmostEqual(mean_of_valid_values([0.4, 0.2], [3, 1], [1]), 0.2)
        self.assertAlmostEqual(mean_of_valid_values([0.4, 0.2, 0], [1, 1, 2], [1,2]), 0.2)
        self.assertAlmostEqual(mean_of_valid_values([0.4], [1], [1]), 0.4)
        self.assertAlmostEqual(mean_of_valid_values([0.4], [2], [1]), -1)

        # grouping test
        grouping = group(data, 'tag', 'time')
        self.assertDictEqual(grouping, {'': [3], 'target2': [4, 5, 6], 'target': [1, 2]})

        # make just an arbitary "list of data-lists"
        extra1 = [{'x':0.5, 'y':0.15, 'tag':'target'},{'x':0.3, 'y':0.1, 'tag':'target'}]
        extra2 = [{'x':0.7, 'y':0.4, 'tag':'test'}]
        datas = [data, extra1, extra2]
        grouping = group_lists(datas, 'tag')
        self.assertDictEqual(grouping, {'test':extra2, 'target': data + extra1})

        rtimes = [105, 120, 130, 1003]
        print SRT_index(rtimes, 1000, 100)
        #self.assertEqual(SRT_index(rtimes, 1000, 100), 100)

    def test_replace(self):
        data = TestIgazelibMethods.data

        data_replaced = replace_value(data, 'tag', 'target', 'target3')
        data_replaced_correct = data[:]
        data_replaced_correct[0]['tag'] = 'target3'
        data_replaced_correct[1]['tag'] = 'target3'
        self.assertListEqual(data_replaced, data_replaced_correct)
        #data_replaced_correct[1]['tag'] = 'target3'
        #self.assertListEqual(data_replaced, data_replaced_correct)

if __name__ == '__main__':
    unittest.main()
