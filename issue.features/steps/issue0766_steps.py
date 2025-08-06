# -*- coding: UTF-8 -*-

from __future__ import print_function
from behave import given


@given('a step with table data')
@given('a step with table data:')
def step_with_table_data(ctx):
    assert ctx.table is not None, "REQUIRE: step.table"


@given('a step with name="{name}"')
def step_with_name_param(ctx, name):
    print("name: {}".format(name))
