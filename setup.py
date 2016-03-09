# -*- coding: utf-8 -*-
"""
Gazelib for Python

This setup.py is based on:
https://packaging.python.org/en/latest/distributing.html
https://github.com/pypa/sampleproject
"""

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path

def get_package_info(module_name):
    '''
    Read info about package version, author etc from <module>/package.py

    Return
        dict {'version': '1.2.3', 'author': 'John Doe', ...}
    '''
    here = path.dirname(path.abspath(__file__))
    code_globals = {}
    code_locals = {}
    with open(path.join(here, module_name, 'package.py')) as f:
        code = compile(f.read(), "package.py", 'exec')
        exec(code, code_globals, code_locals)
    return code_locals

def get_long_description():
    '''
    Get the long description from the README file
    '''
    # Path to here to find README
    here = path.abspath(path.dirname(__file__))
    with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
        long_description = f.read()
    return long_description


# Get the version from gazelib/version.py
# Modified from http://stackoverflow.com/a/21784019/638546
def get_version(module_name, filename):
    import re

    here = path.dirname(path.abspath(__file__))
    with open(path.join(here, module_name, filename)) as f:
        version_file = f.read()
        version_match = re.search(r'^__version__ = [\'\"]([^\'\"]*)[\'\"]',
                                  version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")

# Read setup parameters from package.py
pkg_info = get_package_info('gazelib')
pkg_info['long_description'] = get_long_description()
setup(**pkg_info)
