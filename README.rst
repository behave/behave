======
Behave
======

.. image:: https://travis-ci.org/behave/behave.png?branch=master
    :target: https://travis-ci.org/behave/behave
    :alt: Travis CI Build Status

.. image:: https://pypip.in/v/behave/badge.png
    :target: https://crate.io/packages/behave/
    :alt: Latest PyPI version

.. image:: https://pypip.in/d/behave/badge.png
    :target: https://crate.io/packages/behave/
    :alt: Number of PyPI downloads

.. |logo| image:: https://raw.github.com/behave/behave/master/docs/_static/behave_logo1.png

behave is behavior-driven development, Python style.

|logo|

Behavior-driven development (or BDD) is an agile software development
technique that encourages collaboration between developers, QA and
non-technical or business participants in a software project.

*behave* uses tests written in a natural language style, backed up by Python
code.

First, `install *behave*.`_


Now make a directory called "features/".
In that directory create a file called "example.feature" containing:

.. code-block:: gherkin

    # -- FILE: features/example.feature
    Feature: Showing off behave

      Scenario: Run a simple test
        Given we have behave installed
         When we implement 5 tests
         Then behave will test them for us!

Make a new directory called "features/steps/".
In that directory create a file called "example_steps.py" containing:

.. code-block:: python

    # -- FILE: features/steps/example_steps.py
    from behave import given, when, then, step

    @given('we have behave installed')
    def step_impl(context):
        pass

    @when('we implement {number:d} tests')
    def step_impl(context, number):  # -- NOTE: number is converted into integer
        assert number > 1 or number == 0
        context.tests_count = number

    @then('behave will test them for us!')
    def step_impl(context):
        assert context.failed is False
        assert context.tests_count >= 0

Run behave:

.. code-block:: bash

    $ behave
    Feature: Showin off behave # features/example.feature:2

      Scenario: Run a simple test          # features/example.feature:4
        Given we have behave installed     # features/steps/example_steps.py:4
        When we implement 5 tests          # features/steps/example_steps.py:8
        Then behave will test them for us! # features/steps/example_steps.py:13

    1 feature passed, 0 failed, 0 skipped
    1 scenario passed, 0 failed, 0 skipped
    3 steps passed, 0 failed, 0 skipped, 0 undefined

Now, continue reading to learn how to the most of *behave*. To get started,
we recommend the `tutorial`_ and then the `feature testing language`_ and
`api`_ references.


.. _`Install *behave*.`: http://pythonhosted.org/behave/install.html
.. _`tutorial`: http://pythonhosted.org/behave/tutorial.html#features
.. _`feature testing language`: http://pythonhosted.org/behave/gherkin.html
.. _`api`: http://pythonhosted.org/behave/api.html


More Information
-------------------------------------------------------------------------------

* `behave documentation`_ (`latest changes`_)
* `behave.example`_: Behave Examples and Tutorials (docs, executable examples).

.. _behave documentation: http://pythonhosted.org/behave/
.. _latest changes: https://github.com/behave/behave/blob/master/CHANGES.rst
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
Web, SMS, ...   `behaving`_       Test Web Apps, Email, SMS, Personas (step library).
=============== ================= =========================================================

.. _behave4cmd: https://github.com/jenisys/behave4cmd
.. _django-behave: https://github.com/rwillmer/django-behave
.. _behaving: https://github.com/ggozad/behaving
