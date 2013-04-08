======
Behave
======

behave is behaviour-driven development, Python style.

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


Project Info
-------------------------------------------------------------------------------

=============== ===============================================================
Category        Hyperlink
=============== ===============================================================
Documentation:  http://packages.python.org/behave/
                (or: https://behave.readthedocs.org/)
Download:       http://pypi.python.org/pypi/behave (or: `github archive`_)
Development:    https://github.com/behave/behave
Issue Tracker:  https://github.com/behave/behave/issues
Changelog:      `CHANGES.rst <CHANGES.rst>`_
=============== ===============================================================


.. _`Install *behave*.`: http://packages.python.org/behave/install.html
.. _`tutorial`: http://packages.python.org/behave/tutorial.html#features
.. _`feature testing language`: http://packages.python.org/behave/gherkin.html
.. _`api`: http://packages.python.org/behave/api.html
.. _`github archive`: https://github.com/behave/behave/tags


More Information
-------------------------------------------------------------------------------

* `behave.example`_: Behave Examples and Tutorials (docs, executable examples).


.. _behave.example: https://github.com/jenisys/behave.example


Testing Domains
-------------------------------------------------------------------------------

Behave and other BDD frameworks allow you to provide **step libraries**
to reuse step definitions in similar projects that address the same 
problem domain.

Support of the following testing domains is currently known:

=============== ================= =========================================================
Testing Domain   Name              Description
=============== ================= =========================================================
Command-line    `behave4cmd`_     Test command-line tools, like behave, etc. (coming soon).
Web Apps        `django-behave`_  Test Django Web apps with behave.
=============== ================= =========================================================

.. _behave4cmd: https://github.com/jenisys/behave4cmd
.. _django-behave: https://github.com/rwillmer/django-behave



