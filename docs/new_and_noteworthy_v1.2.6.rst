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

.. literalinclude:: ../examples/async_step/features/steps/async_steps35.py
    :language: python
    :prepend:
        # -- FILE: features/steps/async_steps35.py


.. literalinclude:: ../examples/async_step/features/steps/async_steps34.py
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

    The async-step is wrapped with an ``èvent_loop.run_until_complete()`` call.
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

