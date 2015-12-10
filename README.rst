========
igazelib
========

The Python package *igazelib* provides software tools to manage and analyze gaze data from eye-trackers.

*Igazelib* is developed at `Infant Cognition Laboratory
<http://www.uta.fi/med/icl/index.html>`_ at University of Tampere.



1. Install
==========

With `pip
<https://pypi.python.org/pypi/igazelib>`_::

    $ pip install igazelib



2. Usage
========


3. API
======



4. For developers
=================

Tips for the developers of the package.


4.1. Clone from GitHub
----------------------

To develop, clone the repository from GitHub::

    $ git clone https://github.com/infant-cognition-tampere/igazelib


4.2. Virtualenv
---------------

Manage python versions and requirements by using virtualenv::

    $ virtualenv -p python3.5 igazelib
    $ cd igazelib
    $ source bin/activate
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

Install new pyenv environments by::

    $ pyenv install 3.4.5

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
    ``saccademodel.egg-info/PKG_INFO`` file.
4.  Upload the package with twine:

    1. Sign the dist: ``$ gpg --detach-sign -a dist/igazelib-1.2.3*``
    2. Upload: ``twine upload dist/igazelib-1.2.3*`` (will ask your PyPI password)

5. Package published!

Updating the package takes same steps except the 3rd.



5. Versioning
=============

`Semantic Versioning 2.0.0
<http://semver.org/>`_



6. License
==========

`GNU General Public License version 3
<http://www.gnu.org/licenses/>`_
