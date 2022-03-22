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

The usage of a custom formatter can be simplified if a formatter alias is defined for.

EXAMPLE:

.. code-block:: ini

    # -- FILE: behave.ini
    # FORMATTER ALIASES: "behave -f allure" and others...
    [behave.formatters]
    allure = allure_behave.formatter:AllureFormatter
    html = behave_html_formatter:HTMLFormatter
    teamcity = behave_teamcity:TeamcityFormatter


Embedding Screenshots / Data in Reports
------------------------------------------------------------------------------

:Hint 1: Only supported by JSON formatter
:Hint 2: Binary attachments may require base64 encoding.

You can embed data in reports with the :class:`~behave.runner.Context` method
:func:`~behave.runner.Context.attach()`, if you have configured a formatter that
supports it. Currently only the JSON formatter supports embedding data.

For example:

.. code-block:: python

    # -- FILE: features/steps/screenshot_example_steps.py
    from behave import fiven, when
    from behave4example.web_browser.util import take_screenshot_and_attach_to_scenario

    @given(u'I open the Google webpage')
    @when(u'I open the Google webpage')
    def step_open_google_webpage(ctx):
        ctx.browser.get("https://www.google.com")
        take_screenshot_and_attach_to_scenario(ctx)

.. code-block:: python

    # -- FILE: behave4example/web_browser/util.py
    # HINTS:
    #   * EXAMPLE CODE ONLY
    #   * BROWSER-SPECIFIC: Implementation may depend on browser driver.
    def take_screenshot_and_attach_to_scenario(ctx):
        # -- HINT: SELENIUM WITH CHROME: ctx.browser.get_screenshot_as_base64()
        screenshot_image = ctx.browser.get_full_page_screenshot_as_png()
        ctx.attach("image/png", screenshot_image)

.. code-block:: python

    # -- FILE: features/environment.py
    # EXAMPLE REQUIRES: This browser driver setup code (or something similar).
    from selenium import webdriver

    def before_all(ctx):
        ctx.browser = webdriver.Firefox()

.. seealso::

    * Selenium Python SDK: https://www.selenium.dev/selenium/docs/api/py/
    * Playwright Python SDK: https://playwright.dev/python/docs/intro


    **RELATED:** Selenium webdriver details:

    * Selenium webdriver (for Firefox): `selenium.webdriver.firefox.webdriver.WebDriver.get_full_page_screenshot_as_png`_
    * Selenium webdriver (for Chrome):  `selenium.webdriver.remote.webdriver.WebDriver.get_screenshot_as_base64`_


    **RELATED:** Playwright details:

    * https://playwright.dev/python/docs/api/class-locator#locator-screenshot
    * https://playwright.dev/python/docs/api/class-page#page-screenshot

.. _`selenium.webdriver.firefox.webdriver.WebDriver.get_full_page_screenshot_as_png`: https://www.selenium.dev/selenium/docs/api/py/webdriver_firefox/selenium.webdriver.firefox.webdriver.html?highlight=screenshot#selenium.webdriver.firefox.webdriver.WebDriver.get_full_page_screenshot_as_png
.. _`selenium.webdriver.remote.webdriver.WebDriver.get_screenshot_as_base64`: https://www.selenium.dev/selenium/docs/api/py/webdriver_remote/selenium.webdriver.remote.webdriver.html?highlight=get_screenshot_as_base64#selenium.webdriver.remote.webdriver.WebDriver.get_screenshot_as_base64
