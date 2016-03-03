try:
    import unittest2 as unittest  # to support Python 2.6
except ImportError:
    import unittest

from deepdiff import DeepDiff
from pprint import PrettyPrinter
pp = PrettyPrinter(indent=4)
import gazelib
import os

def load_sample(sample_name):
    '''
    Reads from fixtures/ directory
    Access e.g. by: load_sample('sample.common.json')
    '''

    this_dir = os.path.dirname(os.path.realpath(__file__))
    full_path = os.path.join(this_dir, 'fixtures', sample_name)
    return gazelib.io.load_json(full_path)

class TestCommonV1(unittest.TestCase):

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

        sliceg = g.slice_by_global_time(1234567890.05, 1234567890.11)

        dd = DeepDiff(sliceg.raw, subg.raw)
        self.assertEqual(dd, {})

    def test_slice_by_timeline(self):

        raw = load_sample('sample.common.json')
        subraw = load_sample('subsample.common.json')
        g = gazelib.containers.CommonV1(raw)
        subg = gazelib.containers.CommonV1(subraw)

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

    def test_iter_slices_by_tag(self):

        raw = load_sample('sample.common.json')
        g = gazelib.containers.CommonV1(raw)

        slices = list(g.iter_slices_by_tag('test/center'))

        self.assertEqual(len(slices), 2)
        self.assertEqual(len(slices[0].raw['events']), 5)
        self.assertEqual(len(slices[1].raw['events']), 4)  # no first-half
        self.assertEqual(len(slices[1].raw['timelines']['eyetracker']), 1)

        #dd = DeepDiff(subg.raw, sliceg.raw)
        #self.assertEqual(dd, {})

    def test_add_environment(self):

        raw = load_sample('sample.common.json')
        g = gazelib.containers.CommonV1(raw)

        g.add_environment('test_env', 123)
        self.assertEqual(g.get_environment('test_env'), 123)

    def test_add_stream(self):

        raw = load_sample('sample.common.json')
        g = gazelib.containers.CommonV1(raw)

        tlex = gazelib.containers.CommonV1.MissingTimelineException
        isex = gazelib.containers.CommonV1.InvalidStreamException

        f = lambda: g.add_stream('my_stream', 'my_timeline', [1,2,3])
        self.assertRaises(tlex, f)

        f = lambda: g.add_stream('my_stream', 'eyetracker', [1])
        self.assertRaises(isex, f)

        g.add_stream('my_stream', 'eyetracker', [1, 2, 3, 4, 5])
        self.assertIn('my_stream', g.iter_stream_names())

    def test_add_event(self):

        raw = load_sample('sample.common.json')
        g = gazelib.containers.CommonV1(raw)

        ieex = gazelib.containers.CommonV1.InvalidEventException

        f = lambda: g.add_event('my_tag', 0.0, 1.4)
        self.assertRaises(ieex, f)

        f = lambda: g.add_event(['my_tag', 'my_tag2'], 'a', 1.4)
        self.assertRaises(ieex, f)

        g.add_event(['my_tag', 'my_tag2'], 0.0, 1.4)
        l = list(g.iter_events_by_tag('my_tag'))
        self.assertEqual(len(l), 1)
