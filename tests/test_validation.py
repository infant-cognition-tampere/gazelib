try:
    import unittest2 as unittest  # to support Python 2.6
except ImportError:
    import unittest

from gazelib import validation as unit

class TestValidation(unittest.TestCase):

    def test_has_keys(self):

        d = { 'a': 0, 'b': 1, 'c': 2 }
        self.assertTrue(unit.has_keys(d, ['a', 'b']))
        self.assertFalse(unit.has_keys(d, ['c', 'e']))
        self.assertTrue(unit.has_keys(d, []))

        self.assertTrue(unit.has_only_keys(d, ['a', 'b', 'c']))
        self.assertFalse(unit.has_only_keys(d, ['a', 'b']))

    def test_is_list_of_strings(self):

        self.assertFalse(unit.is_list_of_strings(['1',1]))
        self.assertFalse(unit.is_list_of_strings(('a','b')))
        self.assertTrue(unit.is_list_of_strings(['a','b']))
        self.assertTrue(unit.is_list_of_strings([]))

if __name__ == '__main__':
    unittest.main()
