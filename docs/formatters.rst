.. _id.appendix.formatters:

========================
Formatters and Reporters
========================

:pypi:`behave` provides 2 different concepts for reporting results of a test run:

  * formatters
  * reporters

A slightly different interface is provided for each "formatter" concept.
The ``Formatter`` is informed about each step that is taken.
The ``Reporter`` has a more coarse-grained API.


Reporters
---------

The following reporters are currently supported:

============== ================================================================
Name            Description
============== ================================================================
junit           Provides JUnit XML-like output.
summary         Provides a summary of the test run.
============== ================================================================


Formatters
----------

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

    You can use more than one formatter during a test run.
    But in general you have only one formatter that writes to ``stdout``.

    The "Mode" column indicates if a formatter is intended to be used in
    dry-run (``--dry-run`` command-line option) or normal mode.


User-Defined Formatters
-----------------------

Behave allows you to provide your own formatter (class)::

    # -- USE: Formatter class "Json2Formatter" in python module "foo.bar"
    # NOTE: Formatter must be importable from python search path.
    behave -f foo.bar:Json2Formatter ...

The usage of a user-defined formatter can be simplified by providing an
alias name for it in the configuration file:

.. code-block:: ini

    # -- FILE: behave.ini
    # ALIAS SUPPORTS: behave -f json2 ...
    # NOTE: Formatter aliases may override builtin formatters.
    [behave.formatters]
    json2 = foo.bar:Json2Formatter

If your formatter can be configured, you should use the userdata concept
to provide them. The formatter should use the attribute schema:

.. code-block:: ini

    # -- FILE: behave.ini
    # SCHEMA: behave.formatter.<FORMATTER_NAME>.<ATTRIBUTE_NAME>
    [behave.userdata]
    behave.formatter.json2.use_pretty = true

    # -- SUPPORTS ALSO:
    #    behave -f json2 -D behave.formatter.json2.use_pretty ...


More Formatters
---------------

The following contributed formatters are currently known:

============== =========================================================================
Name           Description
============== =========================================================================
allure         :pypi:`allure-behave`, an Allure formatter for behave.
html           :pypi:`behave-html-formatter`, a simple HTML formatter for behave.
teamcity       :pypi:`behave-teamcity`, a formatter for JetBrains TeamCity CI testruns
               with behave.
============== =========================================================================

.. code-block:: ini

    # -- FILE: behave.ini
    # FORMATTER ALIASES: behave -f allure ...
    [behave.formatters]
    allure = allure_behave.formatter:AllureFormatter
    html = behave_html_formatter:HTMLFormatter
    teamcity = behave_teamcity:TeamcityFormatter


Embedding data (e.g. screenshots) in reports
------------------------------------------------------------------------------

You can embed data in reports with the :class:`~behave.runner.Context` method
:func:`~behave.runner.Context.attach`, if you have configured a formatter that
supports it. Currently only the JSON formatter supports embedding data.

For example:

.. code-block:: python

    @when(u'I open the Google webpage')
    def step_impl(context):
        context.browser.get('http://www.google.com')
        img = context.browser.get_full_page_screenshot_as_png()
        context.attach("image/png", img)
