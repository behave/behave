# -*- coding: UTF-8 -*-
# -- FILE: features/steps/number_steps.py
"""
Step-functions for soft-assertion example.

STEPS:
    Given a minimum number value of "5"
    Then  the numbers "2" and "12" are in the valid range
    And   the number "4" is in the valid range
"""

from __future__ import print_function
from behave import given, then
from assertpy import assert_that, soft_assertions


# -----------------------------------------------------------------------------
# NUMBER STEPS (with soft-asserts)
# -----------------------------------------------------------------------------
@given(u'a minimum number value of "{min_value:d}"')
def step_given_min_number_value(ctx, min_value):
    ctx.min_number_value = min_value


@then(u'the number "{number:d}" is in the valid range')
def step_then_number_is_valid(ctx, number):
    assert_that(number).is_greater_than_or_equal_to(ctx.min_number_value)

@then(u'the numbers "{number1:d}" and "{number2:d}" are in the valid range')
@soft_assertions()
def step_then_numbers_are_valid(ctx, number1, number2):
    assert_that(number1).is_greater_than_or_equal_to(ctx.min_number_value)
    assert_that(number2).is_greater_than_or_equal_to(ctx.min_number_value)


@then(u'the positive number "{number:d}" is in the valid range')
def step_then_positive_number_is_valid(ctx, number):
    # -- ALTERNATIVE: Use ContextManager instead of disabled decorator above.
    with soft_assertions():
        assert_that(number).is_greater_than_or_equal_to(0)
        assert_that(number).is_greater_than_or_equal_to(ctx.min_number_value)
