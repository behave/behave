# ruff: noqa: F811
"""
Step implementations for tutorial example.
"""

from behave import given, when, then
from assertpy import assert_that


@given('we have behave installed')
def step_impl(context):
    pass


@when('we implement a test')
def step_impl(context):
    assert_that(True).is_not_equal_to(False)


@then('behave will test it for us!')
def step_impl(context):
    assert_that(context.failed).is_equal_to(False)
