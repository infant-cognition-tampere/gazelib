try:
    import unittest2 as unittest  # to support Python 2.6
except ImportError:
    import unittest

import gazelib
from numpy import testing as nptest  # to assert almost equal lists
import os

class TestIO(unittest.TestCase):

    # Find file path
    this_dir = os.path.dirname(os.path.realpath(__file__))

    def test_read_csv(self):
        sample_filepath = os.path.join(self.this_dir, 'sample.gazedata')

        dl = gazelib.io.load_csv_as_dictlist(sample_filepath)
        self.assertEqual(len(dl), 10)

    def test_read_json(self):
        sample_filepath = os.path.join(self.this_dir, 'sample.json')

        dl = gazelib.io.load_json(sample_filepath)
        self.assertEqual(len(dl), 10)

if __name__ == '__main__':
    unittest.main()
