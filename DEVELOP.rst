DEVELOPMENT
==============================================================================


Installation
------------------------------------------------------------------------------

:Precondition: pip >= 1.1 is installed

Install the basic requirements for this python package.
Then install all the dependencies that are needed for the development::

    pip install -r requirements/all.txt


Basic Build-Support for Common Tasks
------------------------------------------------------------------------------

:Precondition: paver >= 1.0.5 is installed

``paver`` is used to support common build tasks.
Use the following command to show all commands::

    paver help

Cleanup temporary files::

    paver clean

Cleanup everything (precious parts, too)::

    paver clean_all


RELATED FILES:
  * pavement.py
  * paver_ext/*.py

SEE ALSO:
  * http://www.blueskyonmars.com/projects/paver/


Running Tests
------------------------------------------------------------------------------

:Precondition: nose  >= 1.1
:Precondition: mock  >= 0.8

Run all unittests by using the nose test runner::

    nosetests

Alternatively, you can also use ``py.test``::

    py.test

or run the tests via ``paver``::

    paver unittest


If you want to run the feature tests, use::

    paver behave_test

To run all tests (unittests and behave tests) use::

    paver test

To run behave tests manualy::

    bin/behave -f progress features/
    bin/behave -f progress issue.features/

RELATED FILES:
  * test/test_*.py                  -- Unit tests.
  * tools/test-features/*.feature   -- Feature tests.
  * selftest.features/*.feature     -- Selftests by using behave.
  * issue.features/*.feature        -- Selftests for behave issues.

SEE ALSO:
  * http://nose.readthedocs.org/en/latest/
  * http://pytest.org/


Code Coverage
------------------------------------------------------------------------------

:Precondition: coverage >= 3.5
:Precondition: nose-cov >= 1.4

The following command runs all tests (unittests, feature tests) with
coverage support and generates a coverage report in HTML format::

    paver coverage

RELATED FILES:
  * .coveragerc             -- Coverage configuration file.
  * build/coverage.html/    -- HTML-based coverage report.

SEE ALSO:
  * http://nedbatchelder.com/code/coverage/


Build the Documentation
------------------------------------------------------------------------------

To build the sphinx-based documentation, run the following command::

    paver docs


RELATED FILES:
  * docs/*.rst              -- Documentation sources.
  * build/docs/html/        -- HTML-based documentation.

SEE ALSO:
  * http://sphinx.pocoo.org/


Running tox
------------------------------------------------------------------------------

:Precondition: pip >= 1.1 is installed
:Precondition: pip2pi > 0.1.1  (for localpi)

``tox`` is used to simplify tests with various python versions in a
clean environment. It verifies that:

  * this python package can be installed
  * all its requirements are specified
  * all tests run with a certain python version (and interpreter variant)

PROCEDURE:

  1. Prepare tox by downloading all required dependencies
  2. Prepare tox by building a local python package index
  3. Run tox

All packages are downloaded by using the following commands::

    paver download_deps
    paver localpi

or use:

    tox -e init

This downloads all required python packages described in the
``requirements*.txt`` files and stores them in the

  * ``$HOME/.pip/downloads/`` subdirectory (default)
  * ``downloads/`` subdirectory (alternative).

The local python package index is also build.
After these 2 preparation steps, ``tox`` can be run::

    tox

or::

    tox -e py27

RELATED FILES:
  * $HOME/.pip/downloads/           -- Downloaded packages (local1 default).
  * $HOME/.pip/downloads/simple/    -- Local python package index (local1).
  * downloads/              -- Downloaded packages (local2 alternative).
  * downloads/simple/       -- Local python package index (local2).
  * tox.ini                 -- Tox configuration file.
  * .tox/                   -- Tox workspace and virtual environments.

SEE ALSO:
  * http://tox.testrun.org/
