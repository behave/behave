======
behave
======

.. |badge.latest_version| image:: https://img.shields.io/pypi/v/behave.svg
    :target: https://pypi.python.org/pypi/behave
    :alt: Latest Version

.. |badge.license| image:: https://img.shields.io/pypi/l/behave.svg
    :target: https://pypi.python.org/pypi/behave/
    :alt: License

.. |badge.CI_status| image:: https://github.com/behave/behave/actions/workflows/test.yml/badge.svg
    :target: https://github.com/behave/behave/actions/workflows/test.yml
    :alt: CI Build Status

.. |badge.docs_status| image:: https://readthedocs.org/projects/behave/badge/?version=latest
    :target: https://behave.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status

.. |badge.discussions| image:: https://img.shields.io/badge/chat-github_discussions-darkgreen
   :target: https://github.com/behave/behave/discussions
   :alt: Discussions at https://github.com/behave/behave/discussions

.. |badge.gitter| image:: https://badges.gitter.im/join_chat.svg
   :target: https://app.gitter.im/#/room/#behave_behave:gitter.im
   :alt: Chat at https://gitter.im/behave/behave

.. |badge.gurubase| image:: https://img.shields.io/badge/Gurubase-Ask%20behave%20Guru-006BFF
   :target: https://gurubase.io/g/behave
   :alt: Ask behave Guru at https://gurubase.io/g/behave


.. |logo| image:: https://raw.github.com/behave/behave/master/docs/_static/behave_logo1.png

|badge.latest_version| |badge.license| |badge.CI_status| |badge.docs_status| |badge.discussions| |badge.gitter| |badge.gurubase|

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

.. code-block:: console

    $ behave
    Feature: Showing off behave # features/example.feature:2

      Scenario: Run a simple test          # features/example.feature:4
        Given we have behave installed     # features/steps/example_steps.py:4
        When we implement 5 tests          # features/steps/example_steps.py:8
        Then behave will test them for us! # features/steps/example_steps.py:13

    1 feature passed, 0 failed, 0 skipped
    1 scenario passed, 0 failed, 0 skipped
    3 steps passed, 0 failed, 0 skipped, 0 undefined

Now, continue reading to learn how to get the most out of *behave*. To get started,
we recommend the `tutorial`_ and then the `feature testing language`_ and
`api`_ references.


.. _`Install *behave*.`: https://behave.readthedocs.io/en/stable/install/
.. _`tutorial`: https://behave.readthedocs.io/en/stable/tutorial/
.. _`feature testing language`: https://behave.readthedocs.io/en/stable/gherkin/
.. _`api`: https://behave.readthedocs.io/en/stable/api/


More Information
-------------------------------------------------------------------------------

* `behave documentation`_: `latest edition`_, `stable edition`_, `PDF`_
* `behave.example`_: Behave Examples and Tutorials (docs, executable examples).
* `changelog`_ (latest changes)


.. _behave documentation: https://behave.readthedocs.io/
.. _changelog:      https://github.com/behave/behave/blob/main/CHANGES.rst
.. _behave.example: https://github.com/behave/behave.example

.. _`latest edition`: https://behave.readthedocs.io/en/latest/
.. _`stable edition`: https://behave.readthedocs.io/en/stable/
.. _PDF:              https://behave.readthedocs.io/_/downloads/en/latest/pdf/

