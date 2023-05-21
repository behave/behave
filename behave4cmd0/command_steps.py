# -*- coding: UTF-8 -*-
# pylint: disable=invalid-name, bad-continuation, bad-whitespace
"""
Provides step definitions to:

    * run commands, like behave
    * create textual files within a working directory

TODO:
  matcher that ignores empty lines and whitespace and has contains comparison
"""

from __future__ import absolute_import, print_function

from behave import when, then, matchers # pylint: disable=no-name-in-module
from behave4cmd0 import command_shell, command_util, textutil
from behave4cmd0.step_util import (DEBUG,
    on_assert_failed_print_details, normalize_text_with_placeholders)
from hamcrest import assert_that, equal_to, is_not


# NOT-USED: from hamcrest import contains_string


# -----------------------------------------------------------------------------
# INIT:
# -----------------------------------------------------------------------------
matchers.register_type(int=int)


# -----------------------------------------------------------------------------
# STEPS: Run commands
# -----------------------------------------------------------------------------
@when(u'I run "{command}"')
@when(u'I run `{command}`')
def step_i_run_command(context, command):
    """
    Run a command as subprocess, collect its output and returncode.
    """
    command_util.ensure_workdir_exists(context)
    context.command_result = command_shell.run(command, cwd=context.workdir)
    command_util.workdir_save_coverage_files(context.workdir)
    if False and DEBUG:
        print(u"run_command: {0}".format(command))
        print(u"run_command.output {0}".format(context.command_result.output))


@when(u'I successfully run "{command}"')
@when(u'I successfully run `{command}`')
def step_i_successfully_run_command(context, command):
    step_i_run_command(context, command)
    step_it_should_pass(context)


@then(u'it should fail with result "{result:int}"')
def step_it_should_fail_with_result(context, result):
    assert_that(context.command_result.returncode, equal_to(result))
    assert_that(result, is_not(equal_to(0)))


@then(u'the command should fail with returncode="{result:int}"')
def step_it_should_fail_with_returncode(context, result):
    assert_that(context.command_result.returncode, equal_to(result))
    assert_that(result, is_not(equal_to(0)))


@then(u'the command returncode is "{result:int}"')
def step_the_command_returncode_is(context, result):
    assert_that(context.command_result.returncode, equal_to(result))


@then(u'the command returncode is non-zero')
def step_the_command_returncode_is_nonzero(context):
    assert_that(context.command_result.returncode, is_not(equal_to(0)))


@then(u'it should pass')
def step_it_should_pass(context):
    assert_that(context.command_result.returncode, equal_to(0),
                context.command_result.output)


@then(u'it should fail')
def step_it_should_fail(context):
    assert_that(context.command_result.returncode, is_not(equal_to(0)),
                context.command_result.output)


@then(u'it should pass with')
def step_it_should_pass_with(context):
    '''
    EXAMPLE:
        ...
        when I run "behave ..."
        then it should pass with:
            """
            TEXT
            """
    '''
    assert context.text is not None, "ENSURE: multiline text is provided."
    step_command_output_should_contain(context)
    assert_that(context.command_result.returncode, equal_to(0),
                context.command_result.output)


@then(u'it should fail with')
def step_it_should_fail_with(context):
    '''
    EXAMPLE:
        ...
        when I run "behave ..."
        then it should fail with:
            """
            TEXT
            """
    '''
    assert context.text is not None, "ENSURE: multiline text is provided."
    step_command_output_should_contain(context)
    assert_that(context.command_result.returncode, is_not(equal_to(0)))


# -----------------------------------------------------------------------------
# STEPS FOR: Output Comparison
# -----------------------------------------------------------------------------
@then(u'the command output should contain "{text}"')
def step_command_output_should_contain_text(context, text):
    '''
    EXAMPLE:
        ...
        Then the command output should contain "TEXT"
    '''
    expected_text = normalize_text_with_placeholders(context, text)
    actual_output = context.command_result.output
    with on_assert_failed_print_details(actual_output, expected_text):
        textutil.assert_normtext_should_contain(actual_output, expected_text)




@then(u'the command output should not contain "{text}"')
def step_command_output_should_not_contain_text(context, text):
    '''
    EXAMPLE:
        ...
        then the command output should not contain "TEXT"
    '''
    expected_text = normalize_text_with_placeholders(context, text)
    actual_output  = context.command_result.output
    with on_assert_failed_print_details(actual_output, expected_text):
        textutil.assert_normtext_should_not_contain(actual_output, expected_text)


@then(u'the command output should contain "{text}" {count:d} times')
def step_command_output_should_contain_text_multiple_times(context, text, count):
    '''
    EXAMPLE:
        ...
        Then the command output should contain "TEXT" 3 times
    '''
    assert count >= 0
    expected_text = normalize_text_with_placeholders(context, text)
    actual_output = context.command_result.output
    expected_text_part = expected_text
    with on_assert_failed_print_details(actual_output, expected_text_part):
        textutil.assert_normtext_should_contain_multiple_times(actual_output,
                                                               expected_text_part,
                                                               count)


@then(u'the command output should contain exactly "{text}"')
def step_command_output_should_contain_exactly_text(context, text):
    """
    Verifies that the command output of the last command contains the
    expected text.

    .. code-block:: gherkin

        When I run "echo Hello"
        Then the command output should contain "Hello"
    """
    expected_text = normalize_text_with_placeholders(context, text)
    actual_output  = context.command_result.output
    textutil.assert_text_should_contain_exactly(actual_output, expected_text)


@then(u'the command output should not contain exactly "{text}"')
def step_command_output_should_not_contain_exactly_text(context, text):
    expected_text = normalize_text_with_placeholders(context, text)
    actual_output  = context.command_result.output
    textutil.assert_text_should_not_contain_exactly(actual_output, expected_text)


@then(u'the command output should contain')
def step_command_output_should_contain(context):
    '''
    EXAMPLE:
        ...
        when I run "behave ..."
        then it should pass
        and  the command output should contain:
            """
            TEXT
            """
    '''
    assert context.text is not None, "REQUIRE: multi-line text"
    step_command_output_should_contain_text(context, context.text)


@then(u'the command output should not contain')
def step_command_output_should_not_contain(context):
    '''
    EXAMPLE:
        ...
        when I run "behave ..."
        then it should pass
        and  the command output should not contain:
            """
            TEXT
            """
    '''
    assert context.text is not None, "REQUIRE: multi-line text"
    text = context.text.rstrip()
    step_command_output_should_not_contain_text(context, text)


@then(u'the command output should contain {count:d} times')
def step_command_output_should_contain_multiple_times(context, count):
    '''
    EXAMPLE:
        ...
        when I run "behave ..."
        then it should pass
        and  the command output should contain 2 times:
            """
            TEXT
            """
    '''
    assert context.text is not None, "REQUIRE: multi-line text"
    text = context.text.rstrip()
    step_command_output_should_contain_text_multiple_times(context, text, count)


@then(u'the command output should contain exactly')
def step_command_output_should_contain_exactly_with_multiline_text(context):
    assert context.text is not None, "REQUIRE: multi-line text"
    text = context.text.rstrip()
    step_command_output_should_contain_exactly_text(context, text)


@then(u'the command output should not contain exactly')
def step_command_output_should_contain_not_exactly_with_multiline_text(context):
    assert context.text is not None, "REQUIRE: multi-line text"
    text = context.text.rstrip()
    step_command_output_should_not_contain_exactly_text(context, text)


# -----------------------------------------------------------------------------
# STEP DEFINITIONS: command output should/should_not match
# -----------------------------------------------------------------------------
@then(u'the command output should match /{pattern}/')
@then(u'the command output should match "{pattern}"')
def step_command_output_should_match_pattern(context, pattern):
    """Verifies that command output matches the ``pattern``.

    :param pattern: Regular expression pattern to use (as string or compiled).

    .. code-block:: gherkin

        # -- STEP-SCHEMA: Then the command output should match /{pattern}/
        Scenario:
          When I run `echo Hello world`
          Then the command output should match /Hello \\w+/
    """
    # steputil.assert_attribute_exists(context, "command_result")
    text = context.command_result.output.strip()
    textutil.assert_text_should_match_pattern(text, pattern)

@then(u'the command output should not match /{pattern}/')
@then(u'the command output should not match "{pattern}"')
def step_command_output_should_not_match_pattern(context, pattern):
    # steputil.assert_attribute_exists(context, "command_result")
    text = context.command_result.output
    textutil.assert_text_should_not_match_pattern(text, pattern)

@then(u'the command output should match')
def step_command_output_should_match_with_multiline_text(context):
    assert context.text is not None, "ENSURE: multiline text is provided."
    pattern = context.text
    step_command_output_should_match_pattern(context, pattern)

@then(u'the command output should not match')
def step_command_output_should_not_match_with_multiline_text(context):
    assert context.text is not None, "ENSURE: multiline text is provided."
    pattern = context.text
    step_command_output_should_not_match_pattern(context, pattern)
