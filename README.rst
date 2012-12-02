======
Behave
======

behave is behaviour-driven development, Python style

Behavior-driven development (or BDD) is an agile software development
technique that encourages collaboration between developers, QA and
non-technical or business participants in a software project.

*behave* uses tests written in a natural language style, backed up by Python
code.

First, `install *behave*.`_

Now make a directory called "example". In that directory create a file
called "example.feature" containing::

 Feature: showing off behave

   Scenario: run a simple test
      Given we have behave installed
       when we implement a test
       then behave will test it for us!

Make a new directory called "example/steps". In that directory create a
file called "example.py" containing::

  from behave import *

  @given('we have behave installed')
  def impl(context):
      pass

  @when('we implement a test')
  def impl(context):
      assert True is not False

  @then('behave will test it for us!')
  def impl(context):
      assert context.failed is False

Run behave::

    % behave
    Feature: showin off behave # example/example.feature:1

      Scenario: run a simple test        # example/example.feature:3
        Given we have behave installed   # example/steps/example.py:3
        When we implement a test         # example/steps/example.py:7
        Then behave will test it for us! # example/steps/example.py:11

    1 feature passed, 0 failed, 0 skipped
    1 scenario passed, 0 failed, 0 skipped
    3 steps passed, 0 failed, 0 skipped, 0 undefined

Now, continue reading to learn how to the most of *behave*. To get started,
we recommend the `tutorial`_ and then the `feature testing language`_ and
`api`_ references.

Download from http://pypi.python.org/pypi/behave

---------------
Version History
---------------

Next Version 1.2.2.x - UNRELEASED

OPEN:

  * issue #93: Generic code adds format-specific text to failed scenarios
  * issue #91: Jenkins confused by null package on classnames in JUnit XML report
  * issue #87: Add name option support
  * issue #82: JUnitReporter fails with Python 3.x
  * issue #79: support for scenario descriptions
  * issue #76: environment.py is loaded twice
  * issue #60: JSONFormatter has several problems (invalid JSON format).
  * issue #54: Include step in JUnit/XML <failure> tag.
  * issue #47: Formatter processing chain is broken.

OPEN ENHANCEMENTS:

  * issue #90: Allow using multiple formatters
  * issue #86: Html formatter
  * issue #79: support for scenario descriptions

FIXED:

  * FIX issue #96: Sub-steps failed without any error info to help debug issue
  * FIX issue #92: Output from --format=plain shows skipped steps in next scenario (same as #35)
  * FIX issue #85: AssertionError with nested regex and pretty formatter
  * FIX issue #84: behave.runner behave does not reliably detected failed test runs
  * FIX issue #83: behave.__main__:main() Various sys.exit issues
  * FIX issue #80: source file names not properly printed with python 3.3.0
  * FIX issue #75: behave @list_of_features.txt is broken.
  * FIX issue #73: current_matcher is not predictable.
  * FIX issue #72: Using GHERKIN_COLORS caused an TypeError.
  * FIX issue #70: JUnitReporter: Generates invalid UTF-8 in CDATA sections
               (stdout/stderr output) when ANSI escapes are used.
  * FIX issue #69: JUnitReporter: Fault when processing ScenarioOutlines with failing steps
  * FIX issue #67: JSON formatter cannot serialize tables.
  * FIX issue #66: context.table and context.text are not cleared.
  * FIX issue #65: unrecognized --tag-help argument.
  * FIX issue #64: Exit status not set to 1 even there are failures in certain cases (related to: #52)
  * FIX issue #63: 'ScenarioOutline' object has no attribute 'stdout'.
  * FIX issue #62: --format=json: Background steps are missing.

RESOLVED:

  * issue #81: Allow defining steps in a separate library.
  * issue #78: Added references to django-behave (pull-request).
  * issue #77: Does not capture stdout from sub-processes

REJECTED:

  * issue #88: Python 3 compatibility changes (=> use 2to3 tool instead).

DUPLICATED:

  * issue #95: Failed test run still returns exit code 0 (same as #84, #64).
  * issue #94: JUnit format does not handle ScenarioOutlines (same as #69).
  * issue #92: Output from --format=plain shows skipped steps in next scenario (same as #35).


Version 1.2.2 - August 21, 2012

NEW:

  * "progress" formatter added.
  * "json-pretty" formatter added (master-repo).
  * Add "selftest.features/" to increase quality, based on cucumber idea.
    Simplifies specifying acceptance tests by building a temporary workdir
    and running behave against it.

IMPROVED:

  * Better support for Windows.
  * Use tox to improve quality w/ testruns in clean sandbox.
  * Add paver for better support project-specific tasks.
  * Add coverage support to improve quality (better detect missing test areas).
  * Add "DEVELOP.txt" to describe common developer tasks/usecases.

CHANGES:

  * Selective merge of release-1.2.2 from master repository (2012-08-20).
  * Selective merge of latest changes/fixes from master repository (2012-08-17).

OPEN:

  * issue #70: JUnitReporter: Generates invalid UTF-8 in CDATA sections (stdout/stderr output) when ANSI escapes are used.
  * issue #60: JSONFormatter has several problems.

FIXES:

  * FIX issue #59: Fatal error when using --format=json
  * FIX issue #56: Use function names other than 'step(...)' in tutorial
  * FIX issue #53: Conflict with @step decorator (similar to #56)
  * FIX issue #46: behave returns 0 (SUCCESS) even in case of test failures
  * FIX issue #45: Parser removes empty lines in multiline text argument
  * FIX issue #44: Parser removes shell-like comment lines in multiline text argument
  * FIX issue #43: Enhance the format of Junit report
  * FIX issue #44: Parser removes shell-like comments in multiline text before multiline is parsed
  * FIX issue #41: Show missing steps in ScenarioOutline only once.
  * FIX issue #40: Test summary reports incorrect passed/failed scenarios and steps when Scenario Outline is used
  * FIX issue #39: make "up" escape sequence work right (provided by Noel Bush)
  * FIX issue #38: escape sequences don't work on terminal output (provided by Noel Bush)
  * FIX issue #37: Strange behaviour when no steps directory is present / path specified
  * FIX issue #35: "behave --format=plain --tags @one" seems to execute right scenario w/ wrong steps
  * FIX issue #34: "behave --version" runs features, but shows no version (DUPLICATES: #30)
  * FIX issue #33: behave 1.1.0: Install fails under Windows
  * FIX issue #32: "behave ... --junit-directory=xxx" fails for more than 1 level
  * FIX issue #31: "behave --format help" raises an error
  * FIX issue #30: behave --version runs tests/features


Version 1.1.0 - January 23, 2012

* Context variable now contains current configuration.
* Context values can now be tested for (``name in context``) and deleted.
* ``__file__`` now available inside step definition files.
* Fixes for various formatting issues.
* Add support for configuration files.
* Add finer-grained controls for various things like log capture, coloured
  output, etc.
* Fixes for tag handling.
* Various documentation enhancements, including an example of full-stack
  testing with Django thanks to David Eyk.
* Split reports into a set of modules, add junit output.
* Added work-in-progress ("wip") mode which is useful when developing new code
  or new tests. See documentation for more details.

Version 1.0.0 - December 5, 2011

* Initial release

.. _`Install *behave*.`: http://packages.python.org/behave/install.html
.. _`tutorial`: http://packages.python.org/behave/tutorial.html#features
.. _`feature testing language`: http://packages.python.org/behave/gherkin.html
.. _`api`: http://packages.python.org/behave/api.html
