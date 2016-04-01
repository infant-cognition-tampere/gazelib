# -*- coding: utf-8 -*-
try:
    import unittest2 as unittest  # to support Python 2.6
except ImportError:
    import unittest

import gazelib
from gazelib.containers import CommonV1

from .utils import (get_temp_filepath, remove_temp_file, frange,
    get_fixture_filepath, load_fixture, assert_files_equal,
    assert_deep_equal)
import jsonschema  # import ValidationError
import os


def assert_valid(self, common_raw, msg='Invalid CommonV1 structure'):
    '''
    Assert given dict is valid gazelib/common/v1
    '''
    try:
        CommonV1.validate(common_raw)
    except:
        self.fail(msg)


class TestCommonV1(unittest.TestCase):

    def test_empty_init(self):
        c = CommonV1()
        assert_valid(self, c.raw, 'CommonV1 default structure is invalid.')

    def test_init_with_file(self):
        fpath = get_fixture_filepath('sample.common.json')
        c = CommonV1(fpath)
        assert_valid(self, c.raw)

    def test_validate(self):
        raw = load_fixture('sample.common.json')
        subraw = load_fixture('subsample.common.json')

        # Ensure fixtures are valid
        assert_valid(self, raw)
        assert_valid(self, subraw)

        # Make invalid modification
        raw['events'] = 'foo'
        f = lambda: CommonV1.validate(raw)
        self.assertRaises(jsonschema.ValidationError, f)

        # Make invalid modification
        subraw['schema'] = 'foo'
        f = lambda: CommonV1.validate(subraw)
        self.assertRaises(jsonschema.ValidationError, f)

    def test_unix_and_relative_time_with_none(self):
        c = CommonV1(get_fixture_filepath('sample.common.json'))

        gt = c.get_time_reference()

        t = c.convert_to_unix_time(5000000);
        self.assertEqual(t - 5000000, gt)
        self.assertEqual(c.convert_to_relative_time(t), 5000000)

        self.assertIsNone(c.convert_to_unix_time(None))
        self.assertIsNone(c.convert_to_relative_time(None))

    def test_get_start_end_time(self):
        subraw = load_fixture('subsample.common.json')
        subg = CommonV1(subraw)

        t0 = subg.get_relative_start_time()
        t1 = subg.get_relative_end_time()
        dur = subg.get_duration()

        self.assertEqual(t0, 50000)
        self.assertEqual(t1, 110000)
        self.assertEqual(dur, 60000)

    def test_get_relative_time_by_index(self):
        c = CommonV1(get_fixture_filepath('sample.common.json'))

        t = c.get_relative_time_by_index('ecg', 3)
        self.assertEqual(t, 30000)

        f = lambda: c.get_relative_time_by_index('ecg', 100)
        self.assertRaises(IndexError, f)

    def test_get_stream_values_and_timeline(self):
        c = CommonV1(get_fixture_filepath('sample.common.json'))

        s = c.get_stream('ecg/voltage_V')
        self.assertIn('values', s)
        self.assertIn('timeline', s)

        f = lambda: c.get_stream('fox')
        self.assertRaises(CommonV1.MissingStreamException, f)

        v = c.get_stream_values('ecg/voltage_V')
        self.assertEqual(len(v), 10)

        f = lambda: c.get_stream_values('fox')
        self.assertRaises(CommonV1.MissingStreamException, f)

        f = lambda: c.get_stream_values('')
        self.assertRaises(CommonV1.MissingStreamException, f)

        t = c.get_stream_timeline_name('ecg/voltage_V')
        self.assertEqual(t, 'ecg')

        f = lambda: c.get_stream_timeline_name('fox')
        self.assertRaises(CommonV1.MissingStreamException, f)

    def test_slice_by_relative_time(self):

        raw = load_fixture('sample.common.json')
        subraw = load_fixture('subsample.common.json')
        g = gazelib.containers.CommonV1(raw)
        subg = gazelib.containers.CommonV1(subraw)

        sliceg = g.slice_by_relative_time(50000, 110000)
        assert_deep_equal(self, sliceg.raw, subg.raw)

    def test_slice_by_global_time(self):
        raw = load_fixture('sample.common.json')
        subraw = load_fixture('subsample.common.json')
        g = gazelib.containers.CommonV1(raw)
        subg = gazelib.containers.CommonV1(subraw)

        gt1 = g.convert_to_unix_time(50000)
        gt2 = g.convert_to_unix_time(110000)

        sliceg = g.slice_by_unix_time(gt1, gt2)
        assert_deep_equal(self, sliceg.raw, subg.raw)

    def test_slice_by_timeline(self):

        raw = load_fixture('sample.common.json')
        g = gazelib.containers.CommonV1(raw)

        # Test invalid timeline
        f = lambda: g.slice_by_timeline('foo', 5)
        self.assertRaises(CommonV1.MissingTimelineException, f)

        # Test invalid end index
        f = lambda: g.slice_by_timeline('ecg', 5, 4)
        self.assertRaises(CommonV1.InvalidRangeException, f)

        sliceg = g.slice_by_timeline('ecg', 5)

        t = g.get_relative_time_by_index('ecg', 5)
        self.assertEqual(sliceg.get_relative_start_time(), t)

    def test_slice_by_tag(self):

        raw = load_fixture('sample.common.json')
        subraw = load_fixture('subsample.common.json')
        g = gazelib.containers.CommonV1(raw)
        subg = gazelib.containers.CommonV1(subraw)

        sliceg = g.slice_by_tag('test/last-half')
        assert_deep_equal(self, subg.raw, sliceg.raw)

        # Reference by index
        slicec = g.slice_by_tag('test/center', index=1)
        self.assertEqual(len(slicec.get_timeline('eyetracker')), 1)

    def test_iter_by_tag(self):

        raw = load_fixture('sample.common.json')
        g = gazelib.containers.CommonV1(raw)

        slices = list(g.iter_by_tag('test/center'))

        self.assertEqual(len(slices), 2)
        self.assertEqual(len(slices[0].raw['events']), 5)
        self.assertEqual(len(slices[1].raw['events']), 4)  # no first-half
        self.assertEqual(len(slices[1].raw['timelines']['eyetracker']), 1)

    def test_set_time_reference(self):
        c = CommonV1()
        f = lambda: c.set_time_reference(1234567890123456.1234)
        self.assertRaises(CommonV1.InvalidTimeException, f)

    def test_add_environment(self):

        raw = load_fixture('sample.common.json')
        g = gazelib.containers.CommonV1(raw)

        g.add_environment('test_env', 123)
        self.assertEqual(g.get_environment('test_env'), 123)
        self.assertIn('test_env', g.get_environment_names())

        self.assertTrue(g.has_environments(['test_env']))
        f = lambda: g.assert_has_environments(['test_env', 'foo'])
        self.assertRaises(CommonV1.InsufficientDataException, f)

        assert_valid(self, g.raw)

    def test_add_stream(self):

        raw = load_fixture('sample.common.json')
        g = gazelib.containers.CommonV1(raw)

        tlex = CommonV1.MissingTimelineException
        isex = CommonV1.InvalidStreamException

        f = lambda: g.add_stream('my_stream', 'my_timeline', [1,2,3])
        self.assertRaises(tlex, f)

        f = lambda: g.add_stream('my_stream', 'eyetracker', [1])
        self.assertRaises(isex, f)

        g.add_stream('my_stream', 'eyetracker', [1, 2, 3, 4, 5])
        self.assertIn('my_stream', g.get_stream_names())

        self.assertTrue(g.has_streams(['my_stream']))
        f = lambda: g.assert_has_streams(['my_stream', 'foo'])
        self.assertRaises(CommonV1.InsufficientDataException, f)

        assert_valid(self, g.raw)

    def test_add_stream_with_invalid_confidence(self):
        '''Confidency too short or elements not between 0.0 and 1.0'''
        ex = CommonV1.InvalidStreamException
        c = CommonV1()
        c.add_timeline('mytime', [1, 2, 3])

        # Too short
        f = lambda: c.add_stream('foo', 'mytime', [5, 5, 5], [0.1])
        self.assertRaises(ex, f)

        # Too large and small values
        f = lambda: c.add_stream('foo', 'mytime', [5, 5, 5], [0.1, -0.1, 10.0])
        self.assertRaises(ex, f)

    def test_add_stream_from_generator(self):
        '''
        Ensure add_timeline can handle generators and converts them to lists.
        '''
        c = CommonV1()
        c.add_timeline('myline', range(0, 100000000, 100000))
        c.add_stream('mystream', 'myline', frange(0.0, 200.0, 0.2),
                     frange(0.0, 1.0, 0.001))
        stream = c.raw['streams']['mystream']
        self.assertEqual(len(stream['values']), 1000)
        self.assertEqual(len(stream['confidence']), 1000)

    def test_add_timeline_from_generator(self):
        '''
        Ensure add_timeline can handle generators and converts them to lists.
        '''
        c = CommonV1()
        c.add_timeline('myline', range(0, 100000000, 100000))
        tl = c.get_timeline('myline')
        self.assertEqual(len(tl), 1000)
        self.assertTrue(isinstance(tl, list))

    def test_add_event(self):

        raw = load_fixture('sample.common.json')
        g = CommonV1(raw)

        ieex = CommonV1.InvalidEventException

        f = lambda: g.add_event('my_tag', 0, 1400000)
        self.assertRaises(ieex, f)

        f = lambda: g.add_event(['my_tag'], 0, 1400000.123)
        self.assertRaises(ieex, f)

        f = lambda: g.add_event(['my_tag', 'my_tag2'], 'a', 1400000)
        self.assertRaises(ieex, f)

        # Invalid range
        f = lambda: g.add_event(['my_tag'], 100, 0)
        self.assertRaises(ieex, f)

        g.add_event(['my_tag', 'my_tag2'], 0, 1400000)
        l = list(g.iter_events_by_tag('my_tag'))
        self.assertEqual(len(l), 1)

        assert_valid(self, g.raw)

    def test_save_timeline_as_csv(self):
        # Load JSON file
        c = CommonV1(get_fixture_filepath('sample.common.json'))
        # Save it partially as CSV
        fpath = get_temp_filepath('myfile.csv')
        c.save_timeline_as_csv('eyetracker', fpath, delimiter=',')

        # Test equivalency
        assert_files_equal(self, fpath,
                           get_fixture_filepath('sample_eyetracker.csv'))
        # Remove saved file
        remove_temp_file(fpath)

    def test_save_as_json(self):

        fpath = get_temp_filepath('myfile.json')
        c = CommonV1()
        c.add_environment('test', 'hello')
        c.save_as_json(fpath)

        cc = CommonV1(fpath)
        self.assertTrue(cc.has_environments(['test']))

        self.assertTrue(os.path.exists(fpath))
        remove_temp_file(fpath)
        self.assertFalse(os.path.exists(fpath))

    def test_save_as_json_human_readable(self):

        fpath = get_temp_filepath('myfile.json')
        c = CommonV1()
        c.set_time_reference(0)
        c.save_as_json(fpath, human_readable=True)
        assert_files_equal(self, fpath,
                           get_fixture_filepath('minimal.common.json'))

        remove_temp_file(fpath)

if __name__ == '__main__':
    unittest.main()
