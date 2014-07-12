Noteworthy in Version 1.2.5
==============================================================================

.. index::
    single: ScenarioOutline; name annotation
    pair:   ScenarioOutline; file location

Scenario Outline: Better represent Example/Row
-------------------------------------------------------------------------------

:Since:  behave 1.2.5a1
:Covers: Name annotation, file location

A scenario outline basically a parametrized scenario template.
It represents a macro/script that is executed for a data-driven set of examples
(parametrized data). Therefore, a scenario outline generates several scenarios,
each representing one example/row combination.

.. code-block:: gherkin

    # -- file:features/xxx.feature
    Feature:
      Scenario Outline: Wow            # line 2
        Given an employee "<name>"

        Examples: Araxas
          | name  | birthyear |
          | Alice |  1985     |         # line 7
          | Bob   |  1975     |         # line 8

        Examples:
          | name   | birthyear |
          | Charly |  1995     |        # line 12


Up to now, the following scenarios were generated from the scenario outline:

.. code-block:: gherkin

    Scenario Outline: Wow          # features/xxx.feature:2
      Given an employee "Alice"

    Scenario Outline: Wow          # features/xxx.feature:2
      Given an employee "Bob"

    Scenario Outline: Wow          # features/xxx.feature:2
      Given an employee "Charly"

Note that  all generated scenarios had the:

  * same name (scenario_outline.name)
  * same file location (scenario_outline.file_location)

From now on, the generated scenarios better
represent the example/row combination within a scenario outline:

.. code-block:: gherkin

    Scenario Outline: Wow -- @1.1 Araxas  # features/xxx.feature:7
      Given an employee "Alice"

    Scenario Outline: Wow -- @1.2 Araxas  # features/xxx.feature:8
      Given an employee "Bob"

    Scenario Outline: Wow -- @2.1         # features/xxx.feature:12
      Given an employee "Charly"

Note that:

  * scenario name is now unique for any examples/row combination
  * scenario name optionally contains the examples (group) name (if one exists)
  * each scenario has a unique file location, based on the row's file location

Therefore, each generated scenario from a scenario outline can be selected
via its file location (and run on its own). In addition, if one fails,
it is now possible to rerun only the failing example/row combination(s).

The name annoations schema for the generated scenarios from above provides
the new default name annotation schema.
It can be adapted/overwritten in "behave.ini":

.. code-block:: ini

    # -- file:behave.ini
    [behave]
    scenario_outline_annotation_schema = {name} -- @{row.id} {examples.name}

    # -- REVERT TO: Old naming schema:
    # scenario_outline_annotation_schema = {name}


The following additional placeholders are provided within a
scenario outline to support this functionality.
They can be used anywhere within a scenario outline.

=============== ===============================================================
Placeholder     Description
=============== ===============================================================
examples.name   Refers name of the example group, may be an empty string.
examples.index  Index of the example group (range=1..N).
row.index       Index of the current row within an example group (range=1..R).
row.id          Shortcut for schema: "<examples.index>.<row.index>"
=============== ===============================================================


.. index::
    single: ScenarioOutline; name with placeholders

Scenario Outline: Name may contain Placeholders
-------------------------------------------------------------------------------

:Since: behave 1.2.5a1

A scenario outline can now use placeholders from example/rows in its name
or its examples name. When the scenarios a generated,
these placeholders will be replaced with the values of the example/row.

Up to now this behavior did only apply to steps of a scenario outline.

EXAMPLE:

.. code-block:: gherkin

    # -- file:features/xxx.feature
    Feature:
      Scenario Outline: Wow <name>-<birthyear>  # line 2
        Given an employee "<name>"

        Examples:
          | name  | birthyear |
          | Alice |  1985     |         # line 7
          | Bob   |  1975     |         # line 8

        Examples: Benares-<ID>
          | name   | birthyear | ID |
          | Charly |  1995     | 42 |   # line 12


This leads to the following generated scenarios,
one for each examples/row combination:

.. code-block:: gherkin

    Scenario Outline: Wow Alice-1985 -- @1.1         # features/xxx.feature:7
      Given an employee "Alice"

    Scenario Outline: Wow Bob-1975 -- @1.2           # features/xxx.feature:8
      Given an employee "Bob"

    Scenario Outline: Wow Charly-1885 -- @2.1 Benares-42 # features/xxx.feature:12
      Given an employee "Charly"

.. index::
    pair:   ScenarioOutline; tags with placeholders

Scenario Outline: Tags may contain Placeholders
-------------------------------------------------------------------------------

:Since: behave 1.2.5a1

Tags from a Scenario Outline are also part of the parametrized template.
Therefore, you may also use placeholders in the tags of a Scenario Outline.

.. note::

    * Placeholder names, that are used in tags, should not contain whitespace.
    * Placeholder values, that are used in tags, are transformed to contain
      no whitespace characters.


EXAMPLE:

.. code-block:: gherkin

    # -- file:features/xxx.feature
    Feature:

      @foo.group<examples.index>
      @foo.row<row.id>
      @foo.name.<name>
      Scenario Outline: Wow            # line 6
        Given an employee "<name>"

        Examples: Araxas
          | name  | birthyear |
          | Alice |  1985     |         # line 11
          | Bob   |  1975     |         # line 12

        Examples: Benares
          | name   | birthyear | ID |
          | Charly |  1995     | 42 |   # line 16


This leads to the following generated scenarios,
one for each examples/row combination:

.. code-block:: gherkin

    @foo.group1 @foo.row1.1 @foo.name.Alice
    Scenario Outline: Wow -- @1.1 Araxas   # features/xxx.feature:11
      Given an employee "Alice"

    @foo.group1 @foo.row1.2 @foo.name.Bob
    Scenario Outline: Wow -- @1.2 Araxas   # features/xxx.feature:12
      Given an employee "Bob"

    @foo.group2 @foo.row2.1 @foo.name.Charly
    Scenario Outline: Wow -- @2.1 Benares  # features/xxx.feature:16
      Given an employee "Charly"

.. index::
    single: ScenarioOutline; select-group-by-tag

It is now possible to run only the examples group "Araxas" (examples group 1)
by using the select-by-tag mechanism:

.. code-block:: sh

    $ behave --tags=@foo.group1 -f progress3 features/xxx.feature
    ...  # features/xxx.feature
      Wow -- @1.1 Araxas  .
      Wow -- @1.2 Araxas  .


.. index::
    single: ScenarioOutline; select-group-by-name

Scenario Outline: Run examples group via select-by-name
-------------------------------------------------------------------------------

:Since: behave 1.2.5a1

The improvements on unique generated scenario names for a scenario outline
(with name annotation) can now be used to run all rows of one examples group.

EXAMPLE:

.. code-block:: gherkin

    # -- file:features/xxx.feature
    Feature:
      Scenario Outline: Wow            # line 2
        Given an employee "<name>"

        Examples: Araxas
          | name  | birthyear |
          | Alice |  1985     |         # line 7
          | Bob   |  1975     |         # line 8

        Examples: Benares
          | name   | birthyear |
          | Charly |  1995     |        # line 12


This leads to the following generated scenarios (when the feature is executed):

.. code-block:: gherkin

    Scenario Outline: Wow -- @1.1 Araxas  # features/xxx.feature:7
      Given an employee "Alice"

    Scenario Outline: Wow -- @1.2 Araxas   # features/xxx.feature:8
      Given an employee "Bob"

    Scenario Outline: Wow -- @2.1 Benares  # features/xxx.feature:12
      Given an employee "Charly"


You can now run all rows of the "Araxas" examples (group)
by selecting it by name (name part or regular expression):

.. code-block:: sh

    $ behave --name=Araxas -f progress3 features/xxx.feature
    ...  # features/xxx.feature
      Wow -- @1.1 Araxas  .
      Wow -- @1.2 Araxas  .

    $ behave --name='-- @.* Araxas' -f progress3 features/xxx.feature
    ...  # features/xxx.feature
      Wow -- @1.1 Araxas  .
      Wow -- @1.2 Araxas  .


.. index::
    single: Scenario; exclude from test run
    pair:   Scenario; exclude from test run
    single: Feature; exclude from test run
    pair:   Feature; exclude from test run


Exclude Feature/Scenario at Runtime
-------------------------------------------------------------------------------

A test writer can now provide a runtime decision logic to exclude
a feature, scenario or scenario outline from a test run
within the following hooks:

  * ``before_feature()`` for a feature
  * ``before_scenario()`` for a scenario
  * step implementation (normally only: given step)

by using the ``skip()`` method before a feature or scenario is run.

.. code-block:: python

    # -- FILE: features/environment.py
    # EXAMPLE 1: Exclude scenario from run-set at runtime.
    import sys

    def should_exclude_scenario(scenario):
        # -- RUNTIME DECISION LOGIC: Will exclude
        #  * Scenario: Alice
        #  * Scenario: Alice in Wonderland
        #  * Scenario: Bob and Alice2
        return "Alice" in scenario.name

    def before_scenario(context, scenario):
        if should_exclude_scenario(scenario):
            scenario.skip()  #< EXCLUDE FROM RUN-SET.
            # -- OR WITH REASON:
            # reason = "RUNTIME-EXCLUDED"
            # scenario.skip(reason)

.. code-block:: python

    # -- FILE: features/steps/my_steps.py
    # EXAMPLE 2: Skip remaining steps in step implementation.
    from behave import given

    @given('the assumption "{assumption}" is met')
    def step_check_assumption(context, assumption):
        if not is_assumption_valid(assumption):
            # -- SKIP: Remaining steps in current scenario.
            context.scenario.skip("OOPS: Assumption not met")
            return

        # -- NORMAL CASE:
        ...



.. index::
    single: Active Tags
    pair:   @only.with_{category}; tag schema

Active Tags: Use "@only.with_{category}"
-------------------------------------------------------------------------------

The term **active tags** is used for tags where it is decided at runtime
if a tag is enabled or disabled. The runtime logic excludes then scenarios/features
with disabled tags.

Assuming you have the feature file where:

  * scenario "Alice" should only run when browser "Chrome" is used
  * scenario "Bob" should only run when browser "Safari" is used

.. code-block:: gherkin

    # -- FILE: features/alice.feature
    Feature:

        @only.with_browser=chrome
        Scenario: Alice (Run only with Browser Chrome)
            Given I do something
            ...

        @only.with_browser=safari
        Scenario: Bob (Run only with Browser Safari)
            Given I do something else
            ...


.. code-block:: python

    # -- FILE: features/environment.py
    # EXAMPLE: ACTIVE TAGS, exclude scenario from run-set at runtime.
    # NOTE: OnlyWithCategoryTagMatcher implements the runtime decision logic.
    from behave.tag_matcher import OnlyWithCategoryTagMatcher
    import os
    import sys

    active_tag_matcher = None

    def before_all(context):
        # -- SETUP ACTIVE-TAG MATCHER: For category="browser"
        global active_tag_matcher
        current_browser = os.environ.get("BEHAVE_BROWSER", "chrome")
        active_tag_matcher = OnlyWithCategoryTagMatcher("browser", current_browser)

    def before_scenario(context, scenario):
        # -- NOTE: scenario.effective_tags := scenario.tags + feature.tags
        if active_tag_matcher.should_exclude_with(scenario.effective_tags):
            # -- NOTE: Exclude any with @only.with_browser=<other_browser>
            scenario.skip(reason="DISABLED ACTIVE-TAG")

.. note::

    By using this mechanism, the ``@only.with_browser=*`` tags become
    **active tags**. The runtime decision logic decides when these tags
    are enabled or disabled (and uses them to exclude their scenario/feature).


.. index::
    single: Active Tags
    pair:   @only.with_{category}; tag schema

Active Tags: Use "@only.with_{category}" with Many Categories
-------------------------------------------------------------------------------

When you use many ``categories`` for active tags, it becomes unnecessary
complicated with the earlier described mechanism. In this case, you should use
the :class:`~behave.tag_matcher.OnlyWithAnyCategoryTagMatcher`.

Assuming you have scenarios with the following runtime conditions:

  * Run scenario Alice only on Windows OS
  * Run scenario Bob only with browser Chrome

.. code-block:: gherkin

    # -- FILE: features/alice.feature
    # TAG SCHEMA: @only.with_{category}={current_value}
    Feature:

      @only.with_os=win32
      Scenario: Alice (Run only on Windows)
        Given I do something
        ...

      @only.with_browser=chrome
      Scenario: Bob (Run only with Web-Browser Chrome)
        Given I do something else
        ...


.. code-block:: python

    # -- FILE: features/environment.py
    from behave.tag_matcher import OnlyWithAnyCategoryTagMatcher
    import sys

    # -- MATCHES ANY TAGS: @only.with_{category}={value}
    # NOTE: category_value_provider provides active values for categories.
    category_value_provider = {
        "browser": os.environ.get("BEHAVE_BROWSER", "chrome"),
        "os":      sys.platform,
    }
    active_tag_matcher = OnlyWithAnyCategoryTagMatcher(category_value_provider)

    def before_feature(context, feature):
        if active_tag_matcher.should_exclude_with(feature.tags):
            feature.skip(reason="DISABLED ACTIVE-TAG")

    def before_scenario(context, scenario):
        if active_tag_matcher.should_exclude_with(scenario.effective_tags):
            scenario.skip("DISABLED ACTIVE-TAG")


.. note::

    Unknown categories, missing in the ``category_value_provider`` are ignored.
