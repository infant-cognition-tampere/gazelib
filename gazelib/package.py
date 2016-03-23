# -*- coding: utf-8 -*-

name = 'gazelib'
version = '1.2.4'
description = 'Software tools to manage and analyze data from eye-trackers'
url = 'https://github.com/infant-cognition-tampere/gazelib'
author = 'Akseli Palen'
author_email = 'akseli.palen@gmail.com'
license = 'GPLv3'

# See https://pypi.python.org/pypi?%3Aaction=list_classifiers
classifiers = [
    # How mature is this project? Common values are
    #   3 - Alpha
    #   4 - Beta
    #   5 - Production/Stable
    'Development Status :: 4 - Beta',

    # Indicate who your project is intended for
    'Intended Audience :: Developers',
    'Intended Audience :: Science/Research',
    'Topic :: Scientific/Engineering :: Bio-Informatics',
    'Topic :: Scientific/Engineering :: Image Recognition',
    'Topic :: Scientific/Engineering :: Human Machine Interfaces',
    'Topic :: Scientific/Engineering :: Information Analysis',

    # Pick your license as you wish (should match "license" above)
    'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',

    # Specify the Python versions you support here. In particular, ensure
    # that you indicate whether you support Python 2, Python 3 or both.
    'Programming Language :: Python :: 2',
    'Programming Language :: Python :: 3',
    'Operating System :: OS Independent',
]

# What does your project relate to?
keywords = 'eye-tracking data'

# You can just specify the packages manually here if your project is
# simple. Or you can use find_packages().
# packages = ['gazelib']
# Note: to use find_packages, it must be run on upper level. Otherwise
# it will be run each time the package becomes imported. See setup.py

# Alternatively, if you want to distribute just a my_module.py, uncomment
# this:
#   py_modules=["my_module"],

# List run-time dependencies here.  These will be installed by pip when
# your project is installed. For an analysis of "install_requires" vs pip's
# requirements files see:
# https://packaging.python.org/en/latest/requirements.html
# Note for Tox: if install_requires changes, .tox must be recreated.
install_requires = ['deepdiff', 'jsonschema']

# List additional groups of dependencies here (e.g. development
# dependencies). You can install these using the following syntax,
# for example:
# $ pip install -e .[dev,test]
extras_require = {
    'dev': ['Sphinx']
}

# If there are data files included in your packages that need to be
# installed, specify them here.  If using Python 2.6 or less, then these
# have to be included in MANIFEST.in as well.
package_data = {}

# Although 'package_data' is the preferred approach, in some case you may
# need to place data files outside of your packages. See:
# http://docs.python.org/3.4/distutils/setupscript.html#installing-additional-files # noqa
# In this case, 'data_file' will be installed into '<sys.prefix>/my_data'
data_files = []

# To provide executable scripts, use entry points in preference to the
# "scripts" keyword. Entry points provide cross-platform support and allow
# pip to create the appropriate form of executable for the target platform.
entry_points = {}

# DEPRECATED: Use 'tox' with 'pyenv' instead.
#   Put test dependencies to 'tox.ini'
# To use nose2 to run your package’s tests, add the following
# tests_require = ['nose2', 'unittest2', 'flake8']
# test_suite = 'nose2.collector.collector'
