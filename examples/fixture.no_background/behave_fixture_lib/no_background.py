# -*- coding: UTF-8 -*-
# RELATED-TO: #756
"""
Example code how to provide a behave fixture to disable the
background inheritance mechanism.

.. code-block:: gherkin

    # -- FILE: features/example.feature
    Feature: Show how @fixture.behave.override_background is used

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

.. code-block:: python

    # -- FILE: features/environment.py
    from behave_fixture_lib.override_background import behave_override_background
    from behave.fixture import use_fixture_by_tag

    # -- FIXTURE REGISTRY:
    fixture_registry = {
        "fixture.behave.no_background": behave_override_background,
    }

    def before_tag(context, tag):
        if tag.startswith("fixture."):
            return use_fixture_by_tag(tag, context, fixture_registry)

"""

from __future__ import absolute_import, print_function
from behave import fixture


# -----------------------------------------------------------------------------
# BEHAVE FIXTURES:
# -----------------------------------------------------------------------------
@fixture(name="fixture.behave.ono_background")
def behave_no_background(ctx):
    """Override the Background inherintance mechanism.
    If a Feature / Rule Background exists in a Feature,
    all contained Scenarios inherit the Background's steps.

    This fixture disables this mechanism.
    The tagged Gherkin element will no longer inherit the background steps.

    :param ctx: Context object to use (during a test run).
    """
    # -- SETUP-PART-ONLY: Disable background inheritance (for scenarios only).
    current_scenario = ctx.scenario
    if current_scenario:
        print("FIXTURE-HINT: DISABLE-BACKGROUND FOR: %s" % current_scenario.name)
        current_scenario.use_background = False


# -----------------------------------------------------------------------------
# MODULE SPECIFIC:
# -----------------------------------------------------------------------------
fixture_registry = {
    "fixture.behave.no_background": behave_no_background,
}
