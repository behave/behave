# ruff: noqa: F811
"""
Step implementations for tutorial example.
"""

from behave import given, when, then


@given('we have behave installed')
def step_impl(context):
    pass


@when('we implement a test')
def step_impl(context):
    assert True is not False


@then('behave will test it for us!')
def step_impl(context):
    assert not context.failed
