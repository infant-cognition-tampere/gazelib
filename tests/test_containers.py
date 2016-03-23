# -*- coding: utf-8 -*-
try:
    import unittest2 as unittest  # to support Python 2.6
except ImportError:
    import unittest

from deepdiff import DeepDiff

from pprint import PrettyPrinter
pp = PrettyPrinter(indent=4)

import gazelib
from gazelib.containers import CommonV1

from .utils import (get_temp_filepath, remove_temp_file, frange,
    get_fixture_filepath, load_sample, assert_files_equal)
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
        raw = load_sample('sample.common.json')
        subraw = load_sample('subsample.common.json')

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

    def test_global_and_relative_time_with_none(self):
        c = CommonV1(get_fixture_filepath('sample.common.json'))

        gt = c.get_global_time()

        t = c.convert_to_global_time(5.0);
        self.assertEqual(t - 5.0, gt)
        self.assertEqual(c.convert_to_relative_time(t), 5.0)

        self.assertIsNone(c.convert_to_global_time(None))
        self.assertIsNone(c.convert_to_relative_time(None))

    def test_get_start_end_time(self):
        subraw = load_sample('subsample.common.json')
        subg = CommonV1(subraw)

        t0 = subg.get_relative_start_time()
        t1 = subg.get_relative_end_time()
        dur = subg.get_duration()

        self.assertEqual(t0, -0.5)
        self.assertEqual(t1, 0.5)
        self.assertEqual(dur, 1.0)

    def test_get_relative_time_by_index(self):
        c = CommonV1(get_fixture_filepath('sample.common.json'))

        t = c.get_relative_time_by_index('ecg', 3)
        self.assertEqual(t, 0.03)

        f = lambda: c.get_relative_time_by_index('ecg', 100)
        self.assertRaises(IndexError, f)

    def test_slice_by_relative_time(self):

        raw = load_sample('sample.common.json')
        subraw = load_sample('subsample.common.json')
        g = gazelib.containers.CommonV1(raw)
        subg = gazelib.containers.CommonV1(subraw)

        sliceg = g.slice_by_relative_time(0.05, 0.11)

        dd = DeepDiff(sliceg.raw, subg.raw)
        self.assertEqual(dd, {})

    def test_slice_by_global_time(self):
        raw = load_sample('sample.common.json')
        subraw = load_sample('subsample.common.json')
        g = gazelib.containers.CommonV1(raw)
        subg = gazelib.containers.CommonV1(subraw)

        gt1 = g.convert_to_global_time(0.05)
        gt2 = g.convert_to_global_time(0.11)

        sliceg = g.slice_by_global_time(gt1, gt2)

        dd = DeepDiff(sliceg.raw, subg.raw)
        self.assertEqual(dd, {})

    def test_slice_by_timeline(self):

        raw = load_sample('sample.common.json')
        subraw = load_sample('subsample.common.json')
        g = gazelib.containers.CommonV1(raw)
        subg = gazelib.containers.CommonV1(subraw)

        # Test invalid timeline
        f = lambda: g.slice_by_timeline('foo', 5)
        self.assertRaises(CommonV1.MissingTimelineException, f)

        # Test invalid end index
        f = lambda: g.slice_by_timeline('ecg', 5, 4)
        self.assertRaises(CommonV1.InvalidRangeException, f)

        sliceg = g.slice_by_timeline('ecg', 5)

        dd = DeepDiff(subg.raw, sliceg.raw)
        # pp.pprint(dd)
        # pp.pprint(sliceg.raw)
        self.assertEqual(dd, {})

    def test_slice_by_tag(self):

        raw = load_sample('sample.common.json')
        subraw = load_sample('subsample.common.json')
        g = gazelib.containers.CommonV1(raw)
        subg = gazelib.containers.CommonV1(subraw)

        sliceg = g.slice_by_tag('test/last-half')
        dd = DeepDiff(subg.raw, sliceg.raw)
        self.assertEqual(dd, {})

        # Reference by index
        slicec = g.slice_by_tag('test/center', index=1)
        self.assertEqual(len(slicec.get_timeline('eyetracker')), 1)

    def test_iter_by_tag(self):

        raw = load_sample('sample.common.json')
        g = gazelib.containers.CommonV1(raw)

        slices = list(g.iter_by_tag('test/center'))

        self.assertEqual(len(slices), 2)
        self.assertEqual(len(slices[0].raw['events']), 5)
        self.assertEqual(len(slices[1].raw['events']), 4)  # no first-half
        self.assertEqual(len(slices[1].raw['timelines']['eyetracker']), 1)

        #dd = DeepDiff(subg.raw, sliceg.raw)
        #self.assertEqual(dd, {})

    def test_set_global_posix_time(self):
        c = CommonV1()
        f = lambda: c.set_global_time(1234567890.123456)
        self.assertRaises(CommonV1.InvalidGlobalTimeException, f)

    def test_add_environment(self):

        raw = load_sample('sample.common.json')
        g = gazelib.containers.CommonV1(raw)

        g.add_environment('test_env', 123)
        self.assertEqual(g.get_environment('test_env'), 123)
        self.assertIn('test_env', g.get_environment_names())

        self.assertTrue(g.has_environments(['test_env']))
        f = lambda: g.assert_has_environments(['test_env', 'foo'])
        self.assertRaises(CommonV1.InsufficientDataException, f)

        assert_valid(self, g.raw)

    def test_add_stream(self):

        raw = load_sample('sample.common.json')
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
        c.add_timeline('myline', frange(0.0, 100.0, 0.1))
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
        c.add_timeline('myline', frange(0.0, 100.0, 0.1))
        tl = c.get_timeline('myline')
        self.assertEqual(len(tl), 1000)
        self.assertTrue(isinstance(tl, list))

    def test_add_event(self):

        raw = load_sample('sample.common.json')
        g = CommonV1(raw)

        ieex = CommonV1.InvalidEventException

        f = lambda: g.add_event('my_tag', 0.0, 1.4)
        self.assertRaises(ieex, f)

        f = lambda: g.add_event(['my_tag', 'my_tag2'], 'a', 1.4)
        self.assertRaises(ieex, f)

        g.add_event(['my_tag', 'my_tag2'], 0.0, 1.4)
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
        c.set_global_time(0)
        c.save_as_json(fpath, human_readable=True)
        assert_files_equal(self, fpath,
                           get_fixture_filepath('minimal.common.json'))

        remove_temp_file(fpath)

if __name__ == '__main__':
    unittest.main()
