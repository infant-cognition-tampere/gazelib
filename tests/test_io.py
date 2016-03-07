try:
    import unittest2 as unittest  # to support Python 2.6
except ImportError:
    import unittest

from .utils import get_temp_filepath, remove_temp_file
import gazelib
import os

class TestIO(unittest.TestCase):

    # Find file path
    this_dir = os.path.dirname(os.path.realpath(__file__))

    def test_read_csv(self):
        sample_filepath = os.path.join(self.this_dir, 'fixtures', 'sample.gazedata')

        dl = gazelib.io.load_csv_as_dictlist(sample_filepath)
        self.assertEqual(len(dl), 10)

    def test_read_json(self):
        sample_filepath = os.path.join(self.this_dir, 'fixtures', 'sample.json')

        dl = gazelib.io.load_json(sample_filepath)
        self.assertEqual(len(dl), 10)

    def test_write_json(self):
        fx = [{'foo': 'hello'}, {'bar': 'world'}]
        fp = get_temp_filepath('foo.json')
        gazelib.io.write_json(fp, fx)
        dl = gazelib.io.load_json(fp)
        self.assertListEqual(dl, fx)
        remove_temp_file(fp)

    def test_write_fancy_json(self):
        fx = [{'foo': 'hello'}, {'bar': 'world'}]
        fp = get_temp_filepath('foo.json')
        gazelib.io.write_fancy_json(fp, fx)
        dl = gazelib.io.load_json(fp)
        self.assertListEqual(dl, fx)
        remove_temp_file(fp)

    def test_write_dictlist_as_csv(self):
        fx = [{'foo': 'hello', 'bar': 'world'}, {'foo': 'world', 'bar': 'baz'}]
        fp = get_temp_filepath('foo.csv')
        gazelib.io.write_dictlist_as_csv(fp, fx)
        dl = gazelib.io.load_csv_as_dictlist(fp)
        self.assertListEqual(dl, fx)
        remove_temp_file(fp)

if __name__ == '__main__':
    unittest.main()
