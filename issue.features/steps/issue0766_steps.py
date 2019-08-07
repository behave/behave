# -*- coding: UTF-8 -*-

from __future__ import print_function
from behave import given

@given(u'a step with table data')
def step_with_table_data(ctx):
    assert ctx.table is not None, "REQUIRE: step.table"

@given(u'a step with name="{name}"')
def step_with_table_data(ctx, name):
    print(u"name: {}".format(name))
