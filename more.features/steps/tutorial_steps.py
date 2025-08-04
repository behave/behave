# -*- coding: UTF-8 -*-
# ruff: noqa: F811
"""
Step implementations for tutorial example.
"""

from __future__ import absolute_import, print_function
from behave import given, when, then
from assertpy import assert_that


@given(u'we have behave installed')
def step_impl(context):
    pass


@when(u'we implement a test')
def step_impl(context):
    assert_that(True).is_not_equal_to(False)


@then(u'behave will test it for us!')
def step_impl(context):
    assert_that(context.failed).is_equal_to(False)
