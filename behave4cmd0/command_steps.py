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

import os
import re
import six

from behave import when, then, register_type # pylint: disable=no-name-in-module
from behave.active_tag.python import PYTHON_VERSION
from behave.parameter_type import parse_unquoted_text
from behave4cmd0 import command_shell, command_util, textutil
from behave4cmd0.step_util import (DEBUG,
    on_assert_failed_print_details, normalize_text_with_placeholders)
from hamcrest import assert_that, equal_to, is_not


# NOT-USED: from hamcrest import contains_string


# -----------------------------------------------------------------------------
# INIT:
# -----------------------------------------------------------------------------
register_type(int=int)
register_type(Unquoted=parse_unquoted_text)


# -----------------------------------------------------------------------------
# STEPS: Run commands
# -----------------------------------------------------------------------------
@when(u'I run "{command:Unquoted}" with locale="{locale_value:Unquoted}"')
@when(u'I run `{command}` with locale="{locale_value:Unquoted}"')
def step_i_run_command_with_locale(ctx, command, locale_value):
    """
    Run a command as subprocess with encoding and language,
    collect its output and return-code.
    """
    this_locale_value = locale_value
    this_language = locale_value
    this_encoding = None
    if "." in locale_value:
        this_language, this_encoding = locale_value.split(".", 1)

    env = os.environ.copy()
    env["LC_ALL"] = this_locale_value
    env["LC_CTYPE"] = this_locale_value
    env["lang"] = this_locale_value

    kwargs = dict(env=env, encoding=this_encoding, errors="replace")
    if PYTHON_VERSION >= (3, 7):
        kwargs["text"] = True

    step_i_run_command(ctx, command, **kwargs)


@when(u'I run "{command:Unquoted}" with encoding="{encoding:Unquoted}"')
@when(u'I run `{command}` with encoding="{encoding:Unquoted}"')
def step_i_run_command_with_encoding(ctx, command, encoding):
    """
    Run a command as subprocess with encoding,
    collect its output and return-code.
    """
    step_i_run_command(ctx, command, encoding=encoding)


@when(u'I run "{command:Unquoted}"')
@when(u'I run `{command}`')
def step_i_run_command(ctx, command, encoding=None, **kwargs):
    """
    Run a command as subprocess, collect its output and returncode.
    """
    command_util.ensure_workdir_exists(ctx)
    if six.PY3 and encoding is not None:
        # -- HINT: Python2 has no "encoding" parameter.
        kwargs["encoding"] = encoding
    ctx.command_result = command_shell.run(command,
                                           cwd=ctx.workdir,
                                           **kwargs)
    command_util.workdir_save_coverage_files(ctx.workdir)
    if False and DEBUG:
        print(u"run_command: {0}".format(command))
        print(u"run_command.output {0}".format(ctx.command_result.output))


@when(u'I successfully run "{command:Unquoted}"')
@when(u'I successfully run `{command}`')
def step_i_successfully_run_command(ctx, command):
    step_i_run_command(ctx, command)
    step_it_should_pass(ctx)


@then(u'it should fail with result "{result:int}"')
def step_it_should_fail_with_result(ctx, result):
    assert_that(ctx.command_result.returncode, equal_to(result))
    assert_that(result, is_not(equal_to(0)))


@then(u'the command should fail with returncode="{result:int}"')
def step_it_should_fail_with_returncode(ctx, result):
    assert_that(ctx.command_result.returncode, equal_to(result))
    assert_that(result, is_not(equal_to(0)))


@then(u'the command returncode is "{result:int}"')
def step_the_command_returncode_is(ctx, result):
    assert_that(ctx.command_result.returncode, equal_to(result))


@then(u'the command returncode is non-zero')
def step_the_command_returncode_is_nonzero(ctx):
    assert_that(ctx.command_result.returncode, is_not(equal_to(0)))


@then(u'it should pass')
def step_it_should_pass(ctx):
    assert_that(ctx.command_result.returncode, equal_to(0),
                ctx.command_result.output)


@then(u'it should fail')
def step_it_should_fail(ctx):
    assert_that(ctx.command_result.returncode, is_not(equal_to(0)),
                ctx.command_result.output)


@then(u'it should pass with')
@then(u'it should pass with:')
def step_it_should_pass_with(ctx):
    '''
    EXAMPLE:
        ...
        when I run "behave ..."
        then it should pass with:
            """
            TEXT
            """
    '''
    assert ctx.text is not None, "ENSURE: multiline text is provided."
    step_command_output_should_contain(ctx)
    assert_that(ctx.command_result.returncode, equal_to(0),
                ctx.command_result.output)


@then(u'it should fail with')
@then(u'it should fail with:')
def step_it_should_fail_with(ctx):
    '''
    EXAMPLE:
        ...
        when I run "behave ..."
        then it should fail with:
            """
            TEXT
            """
    '''
    assert ctx.text is not None, "ENSURE: multiline text is provided."
    step_command_output_should_contain(ctx)
    assert_that(ctx.command_result.returncode, is_not(equal_to(0)))


# -----------------------------------------------------------------------------
# STEPS FOR: Output Comparison
# -----------------------------------------------------------------------------
@then(u'the command output should contain "{text}"')
def step_command_output_should_contain_text(ctx, text):
    '''
    EXAMPLE:
        ...
        Then the command output should contain "TEXT"
    '''
    expected_text = normalize_text_with_placeholders(ctx, text)
    actual_output = ctx.command_result.output
    with on_assert_failed_print_details(actual_output, expected_text):
        textutil.assert_normtext_should_contain(actual_output, expected_text)


@then(u'the command output should not contain "{text}"')
def step_command_output_should_not_contain_text(ctx, text):
    '''
    EXAMPLE:
        ...
        then the command output should not contain "TEXT"
    '''
    expected_text = normalize_text_with_placeholders(ctx, text)
    actual_output  = ctx.command_result.output
    with on_assert_failed_print_details(actual_output, expected_text):
        textutil.assert_normtext_should_not_contain(actual_output, expected_text)


@then(u'the command output should contain "{text}" {count:d} times')
def step_command_output_should_contain_text_multiple_times(ctx, text, count):
    '''
    EXAMPLE:
        ...
        Then the command output should contain "TEXT" 3 times
    '''
    assert count >= 0
    expected_text = normalize_text_with_placeholders(ctx, text)
    actual_output = ctx.command_result.output
    expected_text_part = expected_text
    with on_assert_failed_print_details(actual_output, expected_text_part):
        textutil.assert_normtext_should_contain_multiple_times(actual_output,
                                                               expected_text_part,
                                                               count)


@then(u'the command output should contain exactly "{text}"')
def step_command_output_should_contain_exactly_text(ctx, text):
    """
    Verifies that the command output of the last command contains the
    expected text.

    .. code-block:: gherkin

        When I run "echo Hello"
        Then the command output should contain "Hello"
    """
    expected_text = normalize_text_with_placeholders(ctx, text)
    actual_output  = ctx.command_result.output
    textutil.assert_text_should_contain_exactly(actual_output, expected_text)


@then(u'the command output should not contain exactly "{text}"')
def step_command_output_should_not_contain_exactly_text(ctx, text):
    expected_text = normalize_text_with_placeholders(ctx, text)
    actual_output  = ctx.command_result.output
    textutil.assert_text_should_not_contain_exactly(actual_output, expected_text)


@then(u'the command output should contain')
@then(u'the command output should contain:')
def step_command_output_should_contain(ctx):
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
    assert ctx.text is not None, "REQUIRE: multi-line text"
    step_command_output_should_contain_text(ctx, ctx.text)


@then(u'the command output should not contain')
@then(u'the command output should not contain:')
def step_command_output_should_not_contain(ctx):
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
    assert ctx.text is not None, "REQUIRE: multi-line text"
    text = ctx.text.rstrip()
    step_command_output_should_not_contain_text(ctx, text)


@then(u'the command output should contain {count:d} times')
@then(u'the command output should contain {count:d} times:')
def step_command_output_should_contain_multiple_times(ctx, count):
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
    assert ctx.text is not None, "REQUIRE: multi-line text"
    text = ctx.text.rstrip()
    step_command_output_should_contain_text_multiple_times(ctx, text, count)


@then(u'the command output should contain exactly')
@then(u'the command output should contain exactly:')
def step_command_output_should_contain_exactly_with_multiline_text(ctx):
    assert ctx.text is not None, "REQUIRE: multi-line text"
    text = ctx.text.rstrip()
    step_command_output_should_contain_exactly_text(ctx, text)


@then(u'the command output should not contain exactly')
@then(u'the command output should not contain exactly:')
def step_command_output_should_contain_not_exactly_with_multiline_text(ctx):
    assert ctx.text is not None, "REQUIRE: multi-line text"
    text = ctx.text.rstrip()
    step_command_output_should_not_contain_exactly_text(ctx, text)


@then(u'the command output should be')
@then(u'the command output should be:')
def step_command_output_should_be(ctx):
    '''
    EXAMPLE:
        ...
        when I run "behave ..."
        then it should pass
        and  the command output should be:
            """
            TEXT
            """
    '''
    assert ctx.text is not None, "REQUIRE: multi-line text"
    expected_text = normalize_text_with_placeholders(ctx, ctx.text.strip())
    actual_output  = ctx.command_result.output.text.strip()
    textutil.assert_text_should_equal(actual_output, expected_text)


# -----------------------------------------------------------------------------
# STEP DEFINITIONS: command output should/should_not match
# -----------------------------------------------------------------------------
@then(u'the command output should match /{pattern}/')
@then(u'the command output should match "{pattern}"')
def step_command_output_should_match_pattern(ctx, pattern):
    """Verifies that command output matches the ``pattern``.

    :param pattern: Regular expression pattern to use (as string or compiled).

    .. code-block:: gherkin

        # -- STEP-SCHEMA: Then the command output should match /{pattern}/
        Scenario:
          When I run `echo Hello world`
          Then the command output should match /Hello \\w+/
    """
    # steputil.assert_attribute_exists(ctx, "command_result")
    regex_flags = (re.MULTILINE | re.UNICODE | re.DOTALL)
    compiled_pattern = re.compile(pattern, regex_flags)
    text = ctx.command_result.output.strip()
    printable_pattern = pattern.replace(r"\(", "(").replace(r"\)", ")")
    with on_assert_failed_print_details(text, printable_pattern):
        textutil.assert_text_should_match_pattern(text, compiled_pattern)


@then(u'the command output should not match /{pattern}/')
@then(u'the command output should not match "{pattern}"')
def step_command_output_should_not_match_pattern(ctx, pattern):
    # steputil.assert_attribute_exists(ctx, "command_result")
    text = ctx.command_result.output
    textutil.assert_text_should_not_match_pattern(text, pattern)


@then(u'the command output should match')
@then(u'the command output should match:')
def step_command_output_should_match_with_multiline_text(ctx):
    assert ctx.text is not None, "ENSURE: multiline text is provided."
    pattern = ctx.text
    step_command_output_should_match_pattern(ctx, pattern)


@then(u'the command output should not match')
@then(u'the command output should not match:')
def step_command_output_should_not_match_with_multiline_text(ctx):
    assert ctx.text is not None, "ENSURE: multiline text is provided."
    pattern = ctx.text
    step_command_output_should_not_match_pattern(ctx, pattern)
