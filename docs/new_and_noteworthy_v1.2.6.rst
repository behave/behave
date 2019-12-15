Noteworthy in Version 1.2.6
==============================================================================

Summary:

* Tagged Examples: Examples in a ScenarioOutline can now have tags.

* Feature model elements have now language attribute based on language tag
  in feature file (or the default language tag that was used by the parser).

* Gherkin parser: Supports escaped-pipe in Gherkin table cell value

* Configuration: Supports now to define default tags in configfile

* Configuration: language data is now used as default-language that should
  be used by the Gherkin parser. Language tags in the Feature file override
  this setting.

* Runner: Can continue after a failed step in a scenario

* Runner: Hooks processing handles now exceptions.
  Hook errors (exception in hook processing) lead now to scenario failures
  (even if no step fails).

* Testing support for asynchronuous frameworks or protocols (:mod:`asyncio` based)

* Context-cleanups: Register cleanup functions that are executed at the end
  of the test-scope (scenario, feature or test-run) via
  :func:`~behave.runner.Context.add_cleanup()`.

* :ref:`docid.fixtures`: Simplify setup/cleanup in scenario, feature or test-run



Scenario Outline Improvements
-------------------------------------------------------------------------------

.. _tagged examples:

.. index::
    pair:   ScenarioOutline; tagged examples
    pair:   Gherkin parser; tagged examples

Tagged Examples
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Since:  behave 1.2.6.dev0

The Gherkin parser (and the model) supports now to use tags with the
``Examples`` section in a ``Scenario Outline``. This functionality can be
used to provide multiple ``Examples`` sections, for example one section per
testing stage (development, integration testing, system testing, ...) or
one section per test team.

The following feature file provides a simple example of this functionality:

.. code-block:: gherkin

    # -- FILE: features/tagged_examples.feature
    Feature:
      Scenario Outline: Wow
        Given an employee "<name>"

        @develop
        Examples: Araxas
          | name  | birthyear |
          | Alice |  1985     |
          | Bob   |  1975     |

        @integration
        Examples:
          | name   | birthyear |
          | Charly |  1995     |

.. note::

    The generated scenarios from a ScenarioOutline inherit the tags from
    the ScenarioOutline and its Examples section::

        # -- FOR scenario in scenario_outline.scenarios:
        scenario.tags = scenario_outline.tags + examples.tags

To run only the first ``Examples`` section, you use:

.. code-block:: shell

    behave --tags=@develop features/tagged_examples.feature

.. code-block:: gherkin

    Scenario Outline: Wow -- @1.1 Araxas  # features/tagged_examples.feature:7
      Given an employee "Alice"

    Scenario Outline: Wow -- @1.2 Araxas  # features/tagged_examples.feature:8
      Given an employee "Bob"


Tagged Examples with Active Tags and Userdata
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

An even more natural fit is to use ``tagged examples`` together with
``active tags`` and ``userdata``:

.. code-block:: gherkin

    # -- FILE: features/tagged_examples2.feature
    # VARIANT 2: With active tags and userdata.
    Feature:
      Scenario Outline: Wow
        Given an employee "<name>"

        @use.with_stage=develop
        Examples: Araxas
          | name  | birthyear |
          | Alice |  1985     |
          | Bob   |  1975     |

        @use.with_stage=integration
        Examples:
          | name   | birthyear |
          | Charly |  1995     |

Select the ``Examples`` section now by using:

.. code-block:: shell

    # -- VARIANT 1: Use userdata
    behave -D stage=integration features/tagged_examples2.feature

    # -- VARIANT 2: Use stage mechanism
    behave --stage=integration features/tagged_examples2.feature


.. code-block:: python

    # -- FILE: features/environment.py
    from behave.tag_matcher import ActiveTagMatcher, setup_active_tag_values
    import sys

    # -- ACTIVE TAG SUPPORT: @use.with_{category}={value}, ...
    active_tag_value_provider = {
        "stage":   "develop",
    }
    active_tag_matcher = ActiveTagMatcher(active_tag_value_provider)

    # -- BEHAVE HOOKS:
    def before_all(context):
        userdata = context.config.userdata
        stage = context.config.stage or userdata.get("stage", "develop")
        userdata["stage"] = stage
        setup_active_tag_values(active_tag_value_provider, userdata)

    def before_scenario(context, scenario):
        if active_tag_matcher.should_exclude_with(scenario.effective_tags):
            sys.stdout.write("ACTIVE-TAG DISABLED: Scenario %s\n" % scenario.name)
            scenario.skip(active_tag_matcher.exclude_reason)




Gherkin Parser Improvements
-------------------------------------------------------------------------------

Escaped-Pipe Support in Tables
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

It is now possible to use the "|" (pipe) symbol in Gherkin tables by escaping it.
The pipe symbol is normally used as column separator in tables.

EXAMPLE:

.. code-block:: Gherkin

    Scenario: Use escaped-pipe symbol
      Given I use table data with:
        | name  | value |
        | alice | one\|two\|three\|four  |
      Then table data for "alice" is "one|two|three|four"

.. seealso::

    * `issue.features/issue0302.feature`_ for details

.. _`issue.features/issue0302.feature`: https://github.com/behave/behave/blob/master/issue.features/issue0302.feature


Configuration Improvements
-------------------------------------------------------------------------------

Language Option
~~~~~~~~~~~~~~~

The interpretation of the ``language-tag`` comment in feature files (Gherkin)
and the configuration ``lang`` option on command-line and in the configuration file
changed slightly.

If a ``language-tag`` is used in a feature file,
it is now prefered over the command-line/configuration file settings.
This is especially useful when your feature files use multiple spoken languages
(in different files).

EXAMPLE:

.. code-block:: Gherkin

    # -- FILE: features/french_1.feature
    # language: fr
    Fonctionnalité: Alice
        ...

.. code-block:: ini

    # -- FILE: behave.ini
    [behave]
    lang = de       # Default (spoken) language to use: German
    ...

.. note::

    The feature object contains now a ``language`` attribute that contains
    the information which language was used during Gherkin parsing.


Default Tags
~~~~~~~~~~~~

It is now possible to define ``default tags`` in the configuration file.
``Default tags`` are used when you do not specify tags on the command-line.

EXAMPLE:

.. code-block:: ini

    # -- FILE: behave.ini
    # Exclude/skip any feature/scenario with @xfail or @not_implemented tags
    [behave]
    default_tags = not (@xfail or @not_implemented)
    ...



Runner Improvements
-------------------------------------------------------------------------------

Hook Errors cause Failures
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The behaviour of hook errors, meaning uncaught exceptions while processing hooks,
is changed in this release. The new behaviour causes the entity (test-run, feature, scenario),
for which the hook is executed, to fail.
In addition, a hook error in a ``before_all()``, ``before_feature()``,
``before_scenario()``, and ``before_tag()`` hook causes its corresponding entity
to be skipped.

.. seealso::

    * `features/runner.hook_errors.feature`_ for the detailled specification

.. _`features/runner.hook_errors.feature`: https://github.com/behave/behave/blob/master/features/runner.hook_errors.feature


Option: Continue after Failed Step in a Scenario
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This behaviour is sometimes desired, when you want to see what happens in the
remaining steps of a scenario.

EXAMPLE:

.. code-block:: python

    # -- FILE: features/environment.py
    from behave.model import Scenario

    def before_all(context):
        userdata = context.config.userdata
        continue_after_failed = userdata.getbool("runner.continue_after_failed_step", False)
        Scenario.continue_after_failed_step = continue_after_failed

.. code-block:: shell

    # -- ENABLE OPTION: Use userdata on command-line
    behave -D runner.continue_after_failed_step=true features/

.. note::

    A failing step normally causes correlated failures in most of the following steps.
    Therefore, this behaviour is normally not desired.

.. seealso::

    * `features/runner.continue_after_failed_step.feature`_ for the detailled specification

.. _`features/runner.continue_after_failed_step.feature`: https://github.com/behave/behave/blob/master/features/runner.continue_after_failed_step.feature


Testing asyncio Frameworks
-------------------------------------------------------------------------------

:Since:  behave 1.2.6.dev0

The following support was added to simplify testing asynchronuous
framework and protocols that are based on :mod:`asyncio` module
(since Python 3.4).

There are basically two use cases:

* async-steps (with event_loop.run_until_complete() semantics)
* async-dispatch step(s) with async-collect step(s) later on


Async-steps
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

It is now possible to use ``async-steps`` in ``behave``.
An async-step is basically a coroutine as step-implementation for behave.
The async-step is wrapped into an ``event_loop.run_until_complete()`` call
by using the ``@async_run_until_complete`` step-decorator.

This avoids another layer of indirection that would otherwise be necessary,
to use the coroutine.

A simple example for the implementation of the async-steps is shown for:

* Python 3.5 with new ``async``/``await`` keywords
* Python 3.4 with ``@asyncio.coroutine`` decorator and ``yield from`` keyword

.. literalinclude:: ../examples/async_step/features/steps/_async_steps35.py
    :language: python
    :prepend:
        # -- FILE: features/steps/async_steps35.py


.. literalinclude:: ../examples/async_step/features/steps/_async_steps34.py
    :language: python
    :prepend:
        # -- FILE: features/steps/async_steps34.py

When you use the async-step from above in a feature file and run it with behave:

.. literalinclude:: ../examples/async_step/testrun_example.async_run.txt
    :language: gherkin
    :prepend:
        # -- TEST-RUN OUTPUT:
        $ behave -f plain features/async_run.feature

.. hidden:

    .. literalinclude:: ../examples/async_step/features/async_run.feature
        :language: gherkin
        :prepend: # -- FILE: features/async_run.feature

.. note::

    The async-step is wrapped with an ``event_loop.run_until_complete()`` call.
    As the timings show, it actually needs approximatly 0.3 seconds to run.




Async-dispatch and async-collect
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The other use case with testing async frameworks is that

* you dispatch one or more async-calls
* you collect (and verify) the results of the async-calls later-on

A simple example of this approach is shown in the following feature file:

.. literalinclude:: ../examples/async_step/features/async_dispatch.feature
    :language: gherkin
    :prepend: # -- FILE: features/async_dispatch.feature

When you run this feature file:

.. literalinclude:: ../examples/async_step/testrun_example.async_dispatch.txt
    :language: gherkin
    :prepend:
        # -- TEST-RUN OUTPUT:
        $ behave -f plain features/async_dispatch.feature

.. note::

    The final async-collect step needs approx. 0.2 seconds until the two
    dispatched async-tasks have finished.
    In contrast, the async-dispatch steps basically need no time at all.

    An :class:`AsyncContext` object is used on the context,
    to hold the event loop information and the async-tasks that are of interest.

The implementation of the steps from above:

.. literalinclude:: ../examples/async_step/features/steps/async_dispatch_steps.py
    :language: gherkin
    :prepend:
        # -- FILE: features/steps/async_dispatch_steps.py
        # REQUIRES: Python 3.4 or newer


Context-based Cleanups
-------------------------------------------------------------------------------

It is now possible to register cleanup functions with the context object.
This functionality is normally used in:

* hooks (:func:`before_all()`, :func:`before_feature()`, :func:`before_scenario()`, ...)
* step implementations
* ...

.. code-block:: python

    # -- SIGNATURE: Context.add_cleanup(cleanup_func, *args, **kwargs)
    # CLEANUP CALL EXAMPLES:
    context.add_cleanup(cleanup0)                       # CALLS LATER: cleanup0()
    context.add_cleanup(cleanup1, 1, 2)                 # CALLS LATER: cleanup1(1, 2)
    context.add_cleanup(cleanup2, name="Alice")         # CALLS LATER: cleanup2(name="Alice")
    context.add_cleanup(cleanup3, 1, 2, name="Bob")     # CALLS LATER: cleanup3(1, 2, name="Bob")

The registered cleanup will be performed when the context layer is removed.
This depends on the the context layer when the cleanup function was registered
(test-run, feature, scenario).

Example:

.. code-block:: python

    # -- FILE: features/environment.py
    def before_all(context):
        context.add_cleanup(cleanup_me)
        # -- ON CLEANUP: Calls cleanup_me()
        # Called after test-run.

    def before_tag(context, tag):
        if tag == "foo":
            context.foo = setup_foo()
            context.add_cleanup(cleanup_foo, context.foo)
            # -- ON CLEANUP: Calls cleanup_foo(context.foo)
            # CASE scenario tag: cleanup_foo() will be called after this scenario.
            # CASE feature  tag: cleanup_foo() will be called after this feature.

.. seealso::

    For more details, see `features/runner.context_cleanup.feature`_ .

.. _`features/runner.context_cleanup.feature`: https://github.com/behave/behave/blob/master/features/runner.context_cleanup.feature


Fixtures
-------------------------------------------------------------------------------

Fixtures simplify setup/cleanup tasks that are often needed for testing.

Providing a Fixture
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    # -- FILE: behave4my_project/fixtures.py  (or in: features/environment.py)
    from behave import fixture
    from somewhere.browser.firefox import FirefoxBrowser

    # -- FIXTURE-VARIANT 1: Use generator-function
    @fixture
    def browser_firefox(context, timeout=30, **kwargs):
        # -- SETUP-FIXTURE PART:
        context.browser = FirefoxBrowser(timeout, **kwargs)
        yield context.browser
        # -- CLEANUP-FIXTURE PART:
        context.browser.shutdown()

Using a Fixture
~~~~~~~~~~~~~~~

.. code-block:: Gherkin

    # -- FILE: features/use_fixture1.feature
    Feature: Use Fixture on Scenario Level

        @fixture.browser.firefox
        Scenario: Use Web Browser Firefox
            Given I load web page "https://somewhere.web"
            ...
        # -- AFTER-SCENARIO: Cleanup fixture.browser.firefox

.. code-block:: python

    # -- FILE: features/environment.py
    from behave import use_fixture
    from behave4my_project.fixtures import browser_firefox

    def before_tag(context, tag):
        if tag == "fixture.browser.firefox":
            use_fixture(browser_firefox, context, timeout=10)


.. seealso::

    * :ref:`docid.fixtures` description for details
    * `features/fixture.feature`_

.. _`features/fixture.feature`: https://github.com/behave/behave/blob/master/features/fixture.feature
