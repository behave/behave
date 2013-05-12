# -*- coding: utf-8 -*-
"""
Passing steps.
Often needed in examples.

EXAMPLES:

    Given a step passes
    When  a step passes
    Then  a step passes.

    Given ...
    When  ...
    Then  it should pass because "the answer is correct".
"""

from behave import given, when, then, step

# -----------------------------------------------------------------------------
# STEPS FOR: passing
# -----------------------------------------------------------------------------
@step(u'a step passes')
def step_passes(context):
    """
    Step that always fails, mostly needed in examples.
    """
    pass

@then(u'it should pass because "{reason}"')
def then_it_should_pass_because(context, reason):
    """
    Self documenting step that indicates some reason.
    """
    pass

