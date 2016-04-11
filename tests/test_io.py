try:
    import unittest2 as unittest  # to support Python 2.6
except ImportError:
    import unittest

from .utils import get_temp_filepath, remove_temp_file
import gazelib
import os

# Find file path
this_dir = os.path.dirname(os.path.realpath(__file__))
fixtures_dir = os.path.join(this_dir, 'fixtures')

class TestIO(unittest.TestCase):

    def test_load_json(self):
        sample_filepath = os.path.join(fixtures_dir, 'sample.json')
        dl = gazelib.io.load_json(sample_filepath)
        self.assertEqual(len(dl), 10)

    def test_load_json_from_missing_file(self):

        def f():
            return gazelib.io.load_json('foo')

        self.assertRaises(IOError, f)

    def test_load_json_from_nonjson_file(self):

        def f():
            path = os.path.join(fixtures_dir, 'sample.gazedata')
            return gazelib.io.load_json(path)

        self.assertRaises(ValueError, f)

    def test_load_csv_as_dictlist(self):
        sample_filepath = os.path.join(fixtures_dir, 'sample.gazedata')
        dl = gazelib.io.load_csv_as_dictlist(sample_filepath)
        self.assertEqual(len(dl), 10)

    def test_load_csv_as_dictlist_from_missing_file(self):

        def load_csv():
            return gazelib.io.load_csv_as_dictlist('foofile')

        self.assertRaises(IOError, load_csv)

    def test_load_csv_as_dictlist_from_noncsv_file(self):

        def f():
            path = os.path.join(fixtures_dir, 'sample.json')
            return gazelib.io.load_csv_as_dictlist(path)

        # No exceptions
        self.assertRaises(ValueError, f)

    def test_write_json(self):
        fx = [{'foo': 'hello'}, {'bar': 'world'}]
        fp = get_temp_filepath('foo.json')
        gazelib.io.write_json(fp, fx)
        dl = gazelib.io.load_json(fp)
        self.assertListEqual(dl, fx)
        remove_temp_file(fp)

    def test_write_json_with_invalid_data(self):
        fp = get_temp_filepath('foo.json')

        def f():
            # Try to save a function
            gazelib.io.write_json(fp, self.test_write_json_with_invalid_data)

        self.assertRaises(TypeError, f)
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
