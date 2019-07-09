EXAMPLE: Disable Background Inheritance Mechanism for Scenario
===============================================================================

:RELATED-TO: #756

This example shows how the Background inheritance mechanism in Gherkin
can be disabled in ``behave``.

Parts of the recipe:

* features/example.feature (Feature file as example)
* features/environment.py (glue code and hooks for fixture-tag / fixture)
* behave_fixture_lib/no_background.py (fixture implementation, workhorse)


.. warning:: BEWARE: This shows you how can do it, not that you should do it

    BETTER:

    * Use Rules to group Scenarios, each with its own Background (in Gherkin v6)
    * Split Feature aspects into multiple feature files (if needed)
    * ... (see issue #756 above)


Explanation
------------------------------------------------------------------------

Example code how to provide a behave fixture to disable the
background inheritance mechanism by using a fixture / fixture-tag.
The fixture-tag "@fixture.behave.no_background" marks the
location in Gherkin (which Scenario) where the fixture should be used

.. code-block:: gherkin

    # -- FILE: features/example.feature
    Feature: Show how @fixture.behave.no_background is used

        Background:
          Given a background step

        Scenario: Alice
          When a step passes
          And note that "Background steps are executed here"

        @fixture.behave.no_background
        Scenario: Bob
          Given I need another scenario setup
          When another step passes
          And note that "NO-BACKGROUND STEPS are executed here"

When the feature is executed, you see that:

* First Scenario "Alice": Background steps are inherited and executed first.
* Second Scenario "Bob": No Background step is executed.

.. code-block:: sh

    $ ../../bin/behave -f plain features/example.feature
    Feature: Override the Background Inheritance Mechanism in some Scenarios
      Background:

      Scenario: Alice
        Given a background step passes ... passed
        When a step passes ... passed
        And note that "Background steps are executed here" ... passed
    FIXTURE-HINT: DISABLE-BACKGROUND FOR: Bob

      Scenario: Bob
        Given I need another scenario setup ... passed
        When another step passes ... passed
        And note that "NO-BACKGROUND STEPS are executed here" ... passed

    1 feature passed, 0 failed, 0 skipped
    2 scenarios passed, 0 failed, 0 skipped
    6 steps passed, 0 failed, 0 skipped, 0 undefined


The environment file provides the glue code that the fixture is called:

.. code-block:: python

    # -- FILE: features/environment.py
    from behave_fixture_lib.no_background import behave_no_background
    from behave.fixture import use_fixture_by_tag

    # -- FIXTURE REGISTRY:
    fixture_registry = {
        "fixture.behave.no_background": behave_no_background,
    }

    # -----------------------------------------------------------------------------
    # HOOKS:
    # -----------------------------------------------------------------------------
    def before_tag(context, tag):
        if tag.startswith("fixture."):
            return use_fixture_by_tag(tag, context, fixture_registry)


.. code-block:: python

    # -- FILE: behave_fixture_lib/no_background.py (fixture implementation)
    from behave import fixture

    @fixture(name="fixture.behave.no_background")
    def behave_no_background(ctx):
        # -- SETUP-PART-ONLY: Disable background inheritance (for scenarios only).
        current_scenario = ctx.scenario
        if current_scenario:
            print("FIXTURE-HINT: DISABLE-BACKGROUND FOR: %s" % current_scenario.name)
            current_scenario.use_background = False
