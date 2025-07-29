# -*- coding: UTF-8
"""
Behave steps for environment variables (process environment).
"""

from __future__ import absolute_import, print_function
import os
from behave import given, when, then, step, register_type
from behave.parameter_type import parse_unquoted_text
from hamcrest import assert_that, is_, is_not


# -----------------------------------------------------------------------------
# STEP PARAMETER TYPES
# -----------------------------------------------------------------------------
register_type(Unquoted=parse_unquoted_text)


# -----------------------------------------------------------------------------
# TEST SUPPORT
# -----------------------------------------------------------------------------
class ScopedEnvironment(object):
    """Store current environment variables and restore them afterwards."""
    def __init__(self, env=None):
        if env is None:
            env = os.environ.copy()
        self.initial_env = env
        self.restored = False

    def restore_environment(self):
        if not self.restored:
            os.environ.clear()
            os.environ.update(self.initial_env)
        self.restored = True


# -----------------------------------------------------------------------------
# STEPS FOR: ENVIRONMENT VARIABLES
# -----------------------------------------------------------------------------
@step(u'I set the environment variable "{env_name:Unquoted}" to "{env_value:Unquoted}"')
def step_I_set_the_environment_variable_to(ctx, env_name, env_value):
    if not hasattr(ctx, "environ"):
        ctx.environ = {}
    ctx.environ[env_name] = env_value
    os.environ[env_name] = env_value

@step(u'I set the following environment variables:"')
def step_I_set_environment_variables_with_table(ctx):
    from behave4cmd0.step_util import require_table
    require_table(ctx, with_columns=["name", "value"])
    scoped_environment = ScopedEnvironment()
    ctx.add_cleanup(scoped_environment.restore_environment)

    # -- SET ENVIRONMENT VARIABLES: From step.table
    for row in ctx.table.rows:
        name = row["name"]
        value = row["value"]
        os.environ[name] = value

@step(u'I inspect the following environment variables:')
def step_I_inspect_environment_variables_with_table(ctx):
    from behave4cmd0.step_util import require_table
    require_table(ctx, with_columns=["name"])
    value_index = ctx.table.ensure_column_exists("value")
    annotation_index = ctx.table.ensure_column_exists("Annotation")

    # -- INSPECT ENVIRONMENT VARIABLES: From step.table
    for row in ctx.table.rows:
        name = row["name"]
        expected_value = row["value"].strip()
        actual_value = os.environ.get(name, None)
        if not expected_value:
            row.cells[value_index] = actual_value or u"__UNDEFINED__"

        # -- ADD ANNOTATAION
        matched = (
            (expected_value and (expected_value == actual_value)) or
            (not expected_value and (
                (actual_value is None) or
                (expected_value != actual_value)
            ))
        )
        annotation = "MATCHED"
        if not matched:
            annotation = "MISMATCHED: {} != actual:{}".format(
                expected_value, actual_value
            )
        row.cells[annotation_index] = annotation


@step(u'I remove the environment variable "{env_name:Unquoted}"')
def step_I_remove_the_environment_variable(ctx, env_name):
    if not hasattr(ctx, "environ"):
        ctx.environ = {}
    ctx.environ[env_name] = ""
    os.environ[env_name] = ""
    del ctx.environ[env_name]
    del os.environ[env_name]


@given(u'the environment variable "{env_name:Unquoted}" exists')
@then(u'the environment variable "{env_name:Unquoted}" exists')
def step_the_environment_variable_exists(ctx, env_name):
    env_variable_value = os.environ.get(env_name)
    assert_that(env_variable_value, is_not(None))


@given(u'the environment variable "{env_name:Unquoted}" does not exist')
@then(u'the environment variable "{env_name:Unquoted}" does not exist')
def step_I_set_the_environment_variable_to(ctx, env_name):
    env_variable_value = os.environ.get(env_name)
    assert_that(env_variable_value, is_(None))
