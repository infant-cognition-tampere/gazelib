========
gazelib
========

The Python package *gazelib* provides software tools to manage and analyze gaze data from eye-trackers.

*Gazelib* is developed at `Infant Cognition Laboratory
<http://www.uta.fi/med/icl/index.html>`_ at University of Tampere.



1. Install
==========

With `pip
<https://pypi.python.org/pypi/gazelib>`_::

    $ pip install gazelib



2. Usage
========


3. API
======

The API provides the following methods:

- add_key
- border_violation
- combine_coordinates
- duration
- first_gazepoints
- first_gazepoints_by_time
- gaze_inside_aoi
- gaze_inside_aoi_percentage
- gazepoints_after_time
- gazepoints_containing_value
- gazepoints_not_containing_value
- get_key
- get_value
- group
- group_lists
- inside_aoi
- interpolate_using_last_good_value
- load_json
- load_csv_as_dictlist
- longest_non_valid_streak
- mean_of_valid_values
- median_filter
- median_filter_data
- replace_value
- SRT_index
- split_at_change_in_value
- valid_gaze_percentage
- version
- write_json
- write_fancy_json



4. For developers
=================

Tips for the developers of the package.


4.1. Use Git
------------

To develop, clone the repository from GitHub::

    $ git clone https://github.com/infant-cognition-tampere/gazelib

Make changes to files, add them to commit, and do commit::

    (edit README.rst)
    $ git add README.rst
    $ git commit -m "Improved documentation"

List files that are not added or not committed::

    $ git status

Push local commits to GitHub::

    $ git push

Ignore some files by editing ``.gitignore``::

    $ nano .gitignore


4.2. Virtualenv
---------------

Manage python versions and requirements by using virtualenv::

    $ cd gazelib
    $ virtualenv -p python3.5 env
    $ source env/bin/activate
    ...
    $ deactivate


4.3. Testing
------------

Follow `instructions to install pyenv
<http://sqa.stackexchange.com/a/15257/14918>`_ and then either run quick tests::

    $ python3.5 setup.py test

or run comprehensive tests for multiple Python versions listed in ``tox.ini``::

    $ pyenv local 2.6.9 2.7.10 3.1.5 3.2.6 3.3.6 3.4.3 3.5.0
    $ eval "$(pyenv init -)"
    $ pyenv rehash
    $ tox

Install new pyenv environments for example by::

    $ pyenv install 3.5.0

Validate README.rst at `http://rst.ninjs.org/
<http://rst.ninjs.org/>`_


4.4. Publishing to PyPI
-----------------------

Follow `python packaging instructions
<https://python-packaging-user-guide.readthedocs.org/en/latest/distributing/>`_:

1.  Create an unpacked sdist: ``$ python setup.py sdist``
2.  Create a universal wheel: ``$ python setup.py bdist_wheel --universal``
3.  Go to `PyPI and register the project by filling the package form
    <https://pypi.python.org/pypi?%3Aaction=submit_form>`_ by uploading
    ``gazelib.egg-info/PKG_INFO`` file.
4.  Upload the package with twine:

    1. Sign the dist: ``$ gpg --detach-sign -a dist/gazelib-1.2.3.tar.gz`` and ``$ gpg --detach-sign -a dist/gazelib-1.2.3-py2.py3-none-any.whl``
    2. Upload: ``twine upload dist/gazelib-1.2.3*`` (will ask your PyPI password)

5. Package published!

Updating the package takes same steps except the 3rd.


4.5 Version release
-------------------

1.  Change version string in ``gazelib/version.py`` and ``setup.py`` to
    ``'1.2.3'``
2.  Run tox tests. See *4.3. Testing*.
3.  Git commit: ``$ git commit --all -m "v1.2.3 release"``
4.  Create tag: ``$ git tag -a 1.2.3 -m "v1.2.3 stable"``
5.  Push commits and tags: ``$ git push && git push --tags``
6.  Publish to PyPI. See *4.4. Publishing to PyPI*.



5. Versioning
=============

`Semantic Versioning 2.0.0
<http://semver.org/>`_



6. License
==========

`GNU General Public License version 3
<http://www.gnu.org/licenses/>`_
