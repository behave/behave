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

============== ======== ================================================================
Name           Mode     Description
============== ======== ================================================================
help           normal   Shows all registered formatters.
json           normal   JSON dump of test run
json.pretty    normal   JSON dump of test run (human readable)
plain          normal   Very basic formatter with maximum compatibility
pretty         normal   Standard colourised pretty formatter
progress       normal   Shows dotted progress for each executed scenario.
progress2      normal   Shows dotted progress for each executed step.
progress3      normal   Shows detailed progress for each step of a scenario.
rerun          normal   Emits scenario file locations of failing scenarios
sphinx.steps   dry-run  Generate sphinx-based documentation for step definitions.
steps          dry-run  Shows step definitions (step implementations).
steps.doc      dry-run  Shows documentation for step definitions.
steps.usage    dry-run  Shows how step definitions are used by steps (in feature files).
tags           dry-run  Shows tags (and how often they are used).
tags.location  dry-run  Shows tags and the location where they are used.
============== ======== ================================================================

.. note::

    You can use more that one formatter during a test run.
    But in general you have only one formatter that writes to ``stdout``.

    The "Mode" column indicates if a formatter is intended to be used in
    dry-run (``--dry-run`` command-line option) or normal mode.


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
