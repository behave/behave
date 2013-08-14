.. _id.appendix.formatters:

==============================================================================
Formatters and Reporters
==============================================================================

`behave`_ provides 2 different concepts for reporting results of a test run:

  * formatters
  * reporters

A slightly different interface is provided for each "formatter" concept.
The ``Formatter`` is informed about each step that is taken.
The ``Reporter`` has a more coarse-grained API.


Formatters
------------------------------------------------------------------------------

The following formatters are currently supported:

============== ================================================================
Name           Description
============== ================================================================
help           Shows all registered formatters.
json           JSON dump of test run
json.pretty    JSON dump of test run (human readable)
plain          Very basic formatter with maximum compatibility
pretty         Standard colourised pretty formatter
progress       Shows dotted progress for each executed scenario.
progress2      Shows dotted progress for each executed step.
progress3      Shows detailed progress for each step of a scenario.
rerun          Emits scenario file locations of failing scenarios
sphinx.steps   Generate sphinx-based documentation for step definitions.
steps          Shows step definitions (step implementations).
steps.doc      Shows documentation for step definitions.
steps.usage    Shows how step definitions are used by steps.
tags           Shows tags (and how often they are used).
tags.location  Shows tags and the location where they are used.
============== ================================================================

.. note::

    You can use more that one formatter during a test run.
    But in general you have only one formatter that writes to ``stdout``.


Reporters
------------------------------------------------------------------------------

The following reporters are currently supported:

============== ================================================================
Name            Description
============== ================================================================
junit           Provides JUnit XML-like output.
summary         Provides a summary of the test run.
============== ================================================================

.. _behave: http://pypi.python.org/pypi/behave
