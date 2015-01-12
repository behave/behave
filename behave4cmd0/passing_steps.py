# -*- coding: utf-8 -*-
"""
Passing steps.
Often needed in examples.

EXAMPLES:

    Given a step passes
    When  another step passes
    Then  a step passes

    Given ...
    When  ...
    Then  it should pass because "the answer is correct".
"""

from behave import step, then

# -----------------------------------------------------------------------------
# STEPS FOR: passing
# -----------------------------------------------------------------------------
@step('{word:w} step passes')
def step_passes(context, word):
    """
    Step that always fails, mostly needed in examples.
    """
    pass

@then('it should pass because "{reason}"')
def then_it_should_pass_because(context, reason):
    """
    Self documenting step that indicates some reason.
    """
    pass

