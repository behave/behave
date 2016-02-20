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

