# -*- coding: utf-8 -*-
'''Test suite which runs flake8, i.e. ensures PEP8 code convetions and more.'''

try:
    import unittest2 as unittest  # to support Python 2.6
except ImportError:
    import unittest
from subprocess import check_call

class TestFlake8(unittest.TestCase):
    '''Test case which runs flake8.'''

    def test_flake8(self):
        check_call(['flake8', 'gazelib'])
