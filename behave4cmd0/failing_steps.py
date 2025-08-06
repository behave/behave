# -*- coding: utf-8 -*-
"""
Generic failing steps.
Often needed in examples.

EXAMPLES:

    Given a step fails
    When  another step fails
    Then  a step fails

    Given ...
    When  ...
    Then  it should fail because "the person is unknown".
"""

from __future__ import absolute_import
from behave import step, then

# -----------------------------------------------------------------------------
# STEPS FOR: failing
# -----------------------------------------------------------------------------
@step('{word:w} step fails')
def step_fails(context, word):
    """Step that always fails, mostly needed in examples."""
    assert False, "EXPECT: Failing step"

@step('{word:w} step fails with "{message}"')
def step_fails_with_message(context, word, message):
    """Step that always fails, mostly needed in examples."""
    assert False, "FAILED: %s" % message

@step('{word:w} step fails with')
def step_fails_with_text(context, word):
    """Step that always fails, mostly needed in examples."""
    assert context.text is not None, "REQUIRE: text"
    step_fails_with_message(context, word, context.text)

@then('it should fail because "{reason}"')
def then_it_should_fail_because(context, reason):
    """Self documenting step that indicates why this step should fail."""
    assert False, "FAILED: %s" % reason

# @step('an error should fail because "{reason}"')
# def then_it_should_fail_because(context, reason):
#     """
#    Self documenting step that indicates why this step should fail.
#    """
#    assert False, reason
