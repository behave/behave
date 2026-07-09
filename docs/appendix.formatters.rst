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
captured       normal   Inspect captured output.
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
steps.bad      dry-run  Shows BAD STEP-DEFINITION(s) (if any exist).
steps.catalog  dry-run  Shows non-technical documentation for step definitions.
steps.code     dry-run  Shows executed steps combined with their code.
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

Behave allows you to provide your own formatter (class):

.. code-block:: bash
    :caption: SHELL

    # -- USE: Formatter class "Json2Formatter" in python module "foo.bar"
    # NOTE: Formatter must be importable from python search path.
    behave -f foo.bar:Json2Formatter ...

The usage of a user-defined formatter can be simplified by providing an
alias name for it in the configuration file:

.. code-block:: ini
    :caption: FILE: behave.ini

    # ALIAS SUPPORTS: behave -f json2 ...
    # NOTE: Formatter aliases may override builtin formatters.
    [behave.formatters]
    json2 = foo.bar:Json2Formatter

Formatter API
-------------

A formatter receives events as behave processes each feature file. The
interface is defined in :class:`behave.formatter.api:IFormatter`. The
base class :class:`behave.formatter.base:Formatter` provides no-op
defaults for every method except ``close()`` (which you must implement),
so you only override the ones you care about.

**Methods (in call order):**

``uri(uri)``
    Fired before processing a feature file. Receives the filename.

``feature(feature)``
    Called before a feature runs. Receives a
    :class:`~behave.model.Feature` object.

``rule(rule)``
    Called before a rule runs. Receives a
    :class:`~behave.model.Rule` object.

``background(background)``
    Fired after ``feature()`` or ``rule()``, before any scenarios.
    Receives a :class:`~behave.model.Background` object.

``scenario(scenario)``
    Called before a scenario runs. Receives a
    :class:`~behave.model.Scenario` object.

``step(step)``
    Called before each step is matched and executed. Behave calls this
    for all steps in a scenario before running any of them.

``match(match)``
    Fired when a step has been matched against its step definition.
    Receives a ``Match`` object, or ``NoMatch`` for undefined steps.

``result(step)``
    Called after a step finishes. The step object carries its status
    (``passed``, ``failed``, ``skipped``, ``undefined``).

``eof()``
    Fired after a feature file is fully processed.

``close()``
    Called when the formatter is done. Close any open streams here.

The call sequence for one feature looks like this:

.. code-block:: text

    uri(filename)
    feature(feature)
    background(background)      # if present
    scenario(scenario)
    step(step_1)
    step(step_2)
    match(match_1)
    result(step_1)
    match(match_2)
    result(step_2)
    eof()

For multiple scenarios, ``scenario()`` / ``step()`` / ``match()`` /
``result()`` repeat per scenario.

.. note::

    ``step()`` is called for all steps in a scenario before any
    ``match()`` or ``result()``. This is different from what you might
    expect. If you need to print steps as they run, buffer them in
    ``step()`` and emit output in ``result()``.


Writing a Custom Formatter
~~~~~~~~~~~~~~~~~~~~~~~~~~

Subclass :class:`behave.formatter.base:Formatter` and set ``name`` and
``description`` class attributes. Behave calls ``__init__`` with a
``stream_opener`` and the ``config`` object.

The smallest useful formatter does almost nothing. It just prints the
feature name when a feature starts:

.. code-block:: python

    # -- FILE: my_formatters/hello.py
    from behave.formatter.base import Formatter


    class HelloFormatter(Formatter):
        name = "hello"
        description = "Prints the feature name and exits"

        def __init__(self, stream_opener, config):
            super().__init__(stream_opener, config)
            self.stream = self.open()

        def feature(self, feature):
            self.stream.write(f"Feature: {feature.name}\n")

        def close(self):
            self.close_stream()

Run it:

.. code-block:: bash

    $ behave -f my_formatters.hello:HelloFormatter features/login.feature
    Feature: Login

That is the whole pattern. Everything else is just more methods.

A slightly more useful formatter prints one line per scenario with its
status:

.. code-block:: python

    # -- FILE: my_formatters/scenario_status.py
    from behave.formatter.base import Formatter
    from behave.model_type import Status


    class ScenarioStatusFormatter(Formatter):
        name = "scenario-status"
        description = "Prints one line per scenario with its status"

        def __init__(self, stream_opener, config):
            super().__init__(stream_opener, config)
            self.stream = self.open()
            self.current_scenario = None

        def scenario(self, scenario):
            self.current_scenario = scenario

        def result(self, step):
            # -- Wait for the last step to finish before printing.
            if step.status.is_final() and self.current_scenario:
                status = self.current_scenario.status.name
                name = self.current_scenario.name
                self.stream.write(f"{status}: {name}\n")

        def eof(self):
            self.stream.flush()

Use it from the command line:

.. code-block:: bash

    $ behave -f my_formatters.scenario_status:ScenarioStatusFormatter features/login.feature
    passed: Valid user can log in
    failed: Wrong password shows an error
    skipped: Admin login via SSO

Or register an alias in your config file:

.. code-block:: ini

    # -- FILE: behave.ini
    [behave.formatters]
    scenario-status = my_formatters.scenario_status:ScenarioStatusFormatter

Then:

.. code-block:: bash

    behave -f scenario-status

If your formatter needs configuration, read it from ``config.userdata``
using the ``behave.formatter.<name>.<key>`` schema:

.. code-block:: ini

    # -- FILE: behave.ini
    [behave.userdata]
    behave.formatter.scenario-status.show_tags = true

Access it in your formatter:

.. code-block:: python

    show_tags = self.config.userdata.getbool(
        "behave.formatter.scenario-status.show_tags", default=False
    )


IFormatter2 (Alternative Interface)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:class:`behave.formatter.api:IFormatter2` provides a simpler, paired
interface with ``on_*`` methods instead of the streaming model above:

================================ ============================
Method                            When it runs
================================ ============================
``on_testrun_start()``            Before any features
``on_file_start(uri)``           Before each feature file
``on_feature_start(feature)``    Before each feature
``on_rule_start(rule)``          Before each rule
``on_scenario_start(scenario)``  Before each scenario
``on_step_start(step)``          Before each step
``on_step_end(step)``            After each step
``on_scenario_end(scenario)``    After each scenario
``on_rule_end(rule)``            After each rule
``on_feature_end(feature)``      After each feature
``on_file_end(uri)``             After each feature file
``on_testrun_end()``             After all features
================================ ============================

Subclass :class:`behave.formatter.api:BaseFormatter2` to use this
interface. Note that ``IFormatter2`` needs an adapter to work with
behave's runner, so ``IFormatter`` is the standard choice for most
formatters.


If your formatter can be configured, you should use the userdata concept
to provide them. The formatter should use the attribute schema:

.. code-block:: ini
    :caption: FILE: behave.ini

    # SCHEMA: behave.formatter.<FORMATTER_NAME>.<ATTRIBUTE_NAME>
    [behave.userdata]
    behave.formatter.json2.use_pretty = true

    # -- SUPPORTS ALSO:
    #    behave -f json2 -D behave.formatter.json2.use_pretty ...


Use ``behave -f help`` to:

* Inspect which formatters are currently defined/supported in your workspace
* Check if a formatter definition has a problem (and which), like: ``ModuleNotFoundError``

.. code-block:: bash
    :caption: SHELL

    $ behave -f help
    AVAILABLE FORMATTERS:
      captured       Inspect captured output.
      html           Very basic HTML formatter
      json           JSON dump of test run
      json.pretty    JSON dump of test run (human readable)
      null           Provides formatter that does not output anything.
      plain          Very basic formatter with maximum compatibility
      pretty         Standard colourised pretty formatter
      progress       Shows dotted progress for each executed scenario.
      progress2      Shows dotted progress for each executed step.
      progress3      Shows detailed progress for each step of a scenario.
      rerun          Emits scenario file locations of failing scenarios
      sphinx.steps   Generate sphinx-based documentation for step definitions.
      steps          Shows step definitions (step implementations).
      steps.bad      Shows BAD STEP-DEFINITION(s) (if any exist).
      steps.catalog  Shows non-technical documentation for step definitions.
      steps.code     Shows executed steps combined with their code.
      steps.doc      Shows documentation for step definitions.
      steps.missing  Shows undefined/missing steps definitions, implements them.
      steps.usage    Shows how step definitions are used by steps.
      tags           Shows tags (and how often they are used).
      tags.location  Shows tags and the location where they are used.

    UNAVAILABLE FORMATTERS:
      allure         ModuleNotFoundError: No module named 'allure_behave'


DESIGN CONSTRAINTS:

A formatter class must implement the following interface:

* :class:`behave.formatter.api:IFormatter`
* :class:`behave.formatter.api:IFormatter2` (alternative)

A formatter class should be derived from the following class:

* :class:`behave.formatter.api:Formatter` (aka: `behave.formatter.base:Formatter`) for :class:`~behave.formatter.api:IFormatter`
* :class:`behave.formatter.api:BaseFormatter2` (aka: `behave.formatter.base2:BaseFormatter2`) for :class:`~behave.formatter.api:IFormatter2`



More Formatters
---------------

The following contributed formatters are currently known:

============== =========================================================================
Name           Description
============== =========================================================================
allure         :pypi:`allure-behave`, an Allure formatter for behave.
html           :pypi:`behave-html-formatter`, a simple HTML formatter for behave.
html-pretty    :pypi:`behave-html-pretty-formatter`, a pretty HTML formatter for behave.
teamcity       :pypi:`behave-teamcity`, a formatter for JetBrains TeamCity CI testruns
               with behave.
============== =========================================================================

The usage of a custom formatter can be simplified if a formatter alias is defined for.

EXAMPLE:

.. code-block:: ini
    :caption: FILE: behave.ini

    # FORMATTER ALIASES: "behave -f allure" and others...
    [behave.formatters]
    allure = allure_behave.formatter:AllureFormatter
    html = behave_html_formatter:HTMLFormatter
    html-pretty = behave_html_pretty_formatter:PrettyHTMLFormatter
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
    :caption: FILE: features/steps/screenshot_example_steps.py

    from behave import given, when
    from behave4example.web_browser.util import take_screenshot_and_attach_to_scenario

    @given('I open the Google webpage')
    @when('I open the Google webpage')
    def step_open_google_webpage(ctx):
        ctx.browser.get("https://www.google.com")
        take_screenshot_and_attach_to_scenario(ctx)

.. code-block:: python
    :caption: FILE: behave4example/web_browser/util.py

    # HINTS:
    #   * EXAMPLE CODE ONLY
    #   * BROWSER-SPECIFIC: Implementation may depend on browser driver.
    def take_screenshot_and_attach_to_scenario(ctx):
        # -- HINT: SELENIUM WITH CHROME: ctx.browser.get_screenshot_as_base64()
        screenshot_image = ctx.browser.get_full_page_screenshot_as_png() # OUTDATED
        ctx.attach("image/png", screenshot_image)

.. code-block:: python
    :caption: FILE: features/environment.py

    # EXAMPLE REQUIRES: This browser driver setup code (or something similar).
    from selenium import webdriver

    def before_all(ctx):
        ctx.browser = webdriver.Firefox()

.. seealso::

    * Selenium Python SDK: https://www.selenium.dev/selenium/docs/api/py/
    * Playwright Python SDK: https://playwright.dev/python/docs/intro


    **RELATED:** Selenium webdriver details:

    * `Selenium: Take a screenshot`_
    * `Selenium webdriver (for Firefox)`_
    * `Selenium webdriver (for Chrome)`_


    **RELATED:** Playwright details:

    * https://playwright.dev/python/docs/api/class-locator#locator-screenshot
    * https://playwright.dev/python/docs/api/class-page#page-screenshot

.. _`Selenium: Take a screenshot`: https://www.selenium.dev/documentation/webdriver/interactions/windows/#takescreenshot
.. _`Selenium webdriver (for Chrome)`: https://www.selenium.dev/documentation/webdriver/browsers/chrome/
.. _`Selenium webdriver (for Firefox)`: https://www.selenium.dev/documentation/webdriver/browsers/firefox/
.. _`Selenium remote webdriver`: https://www.selenium.dev/documentation/webdriver/drivers/remote_webdriver/
.. _`Selenium: BrowsingContext.capture_screenshot`: https://www.selenium.dev/selenium/docs/api/py/selenium_webdriver_common_bidi/selenium.webdriver.common.bidi.browsing_context.html#selenium.webdriver.common.bidi.browsing_context.BrowsingContext.capture_screenshot
