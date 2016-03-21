# -*- coding: utf-8 -*-
try:
    import unittest2 as unittest  # to support Python 2.6
except ImportError:
    import unittest

import gazelib
import pkg_resources  # part of setuptools

class TestVersion(unittest.TestCase):

    def test_equal(self):
        '''
        should have version that match package
        '''
        setuppy_version = pkg_resources.require('gazelib')[0].version
        self.assertEqual(gazelib.__version__, setuppy_version)

if __name__ == '__main__':
    unittest.main()
