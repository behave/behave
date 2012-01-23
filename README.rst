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
  def step(context):
      pass

  @when('we implement a test')
  def step(context):
      assert True is not False

  @then('behave will test it for us!')
  def step(context):
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
