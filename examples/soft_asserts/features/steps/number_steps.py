# -- FILE: features/steps/number_steps.py
"""
Step-functions for soft-assertion example.

STEPS:
    Given a minimum number value of "5"
    Then  the numbers "2" and "12" are in the valid range
    And   the number "4" is in the valid range
"""

from behave import given, then


# -----------------------------------------------------------------------------
# NUMBER STEPS (with soft-asserts)
# -----------------------------------------------------------------------------
@given('a minimum number value of "{min_value:d}"')
def step_given_min_number_value(ctx, min_value):
    ctx.min_number_value = min_value


@then('the number "{number:d}" is in the valid range')
def step_then_number_is_valid(ctx, number):
    assert number >= ctx.min_number_value

@then('the numbers "{number1:d}" and "{number2:d}" are in the valid range')
@soft_assertions()
def step_then_numbers_are_valid(ctx, number1, number2):
    assert number1 >= ctx.min_number_value
    assert number2 >= ctx.min_number_value


@then('the positive number "{number:d}" is in the valid range')
def step_then_positive_number_is_valid(ctx, number):
    assert number >= 0
    assert number >= ctx.min_number_value
