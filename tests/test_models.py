try:
    import unittest2 as unittest  # to support Python 2.6
except ImportError:
    import unittest

from .utils import load_fixture

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


class TestFixation(unittest.TestCase):
    pass

if __name__ == '__main__':
    unittest.main()
