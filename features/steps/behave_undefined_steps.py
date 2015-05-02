# -*- coding: UTF-8 -*-
"""
Provides step definitions for behave based on behave4cmd.

REQUIRES:
  * behave4cmd.steplib.output steps (command output from behave).
"""

from __future__ import absolute_import
from behave import then
from behave.runner_util import make_undefined_step_snippet


# -----------------------------------------------------------------------------
# UTILITY FUNCTIONS:
# -----------------------------------------------------------------------------
def text_indent(text, indent_size=0):
    prefix = " " * indent_size
    return prefix.join(text.splitlines(True))


# -----------------------------------------------------------------------------
# STEPS FOR: Undefined step definitions
# -----------------------------------------------------------------------------
@then(u'an undefined-step snippets section exists')
def step_undefined_step_snippets_section_exists(context):
    """
    Checks if an undefined-step snippet section is in behave command output.
    """
    context.execute_steps(u'''
        Then the command output should contain:
            """
            You can implement step definitions for undefined steps with these snippets:
            """
    ''')

@then(u'an undefined-step snippet should exist for "{step}"')
def step_undefined_step_snippet_should_exist_for(context, step):
    """
    Checks if an undefined-step snippet is provided for a step
    in behave command output (last command).

    EXAMPLE:
        Then an undefined-step snippet should exist for "Given an undefined step"
    """
    undefined_step_snippet  = make_undefined_step_snippet(step)
    context.execute_steps(u'''\
Then the command output should contain:
    """
    {undefined_step_snippet}
    """
    '''.format(undefined_step_snippet=text_indent(undefined_step_snippet, 4)))


@then(u'an undefined-step snippet should not exist for "{step}"')
def step_undefined_step_snippet_should_not_exist_for(context, step):
    """
    Checks if an undefined-step snippet is provided for a step
    in behave command output (last command).
    """
    undefined_step_snippet  = make_undefined_step_snippet(step)
    context.execute_steps(u'''\
Then the command output should not contain:
    """
    {undefined_step_snippet}
    """
    '''.format(undefined_step_snippet=text_indent(undefined_step_snippet, 4)))


@then(u'undefined-step snippets should exist for')
def step_undefined_step_snippets_should_exist_for_table(context):
    """
    Checks if undefined-step snippets are provided.

    EXAMPLE:
        Then undefined-step snippets should exist for:
            | Step |
            | When an undefined step is used |
            | Then another undefined step is used |
    """
    assert context.table, "REQUIRES: table"
    for row in context.table.rows:
        step = row["Step"]
        step_undefined_step_snippet_should_exist_for(context, step)


@then(u'undefined-step snippets should not exist for')
def step_undefined_step_snippets_should_not_exist_for_table(context):
    """
    Checks if undefined-step snippets are not provided.

    EXAMPLE:
        Then undefined-step snippets should not exist for:
            | Step |
            | When an known step is used |
            | Then another known step is used |
    """
    assert context.table, "REQUIRES: table"
    for row in context.table.rows:
        step = row["Step"]
        step_undefined_step_snippet_should_not_exist_for(context, step)
