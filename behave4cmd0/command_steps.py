# -*- coding -*-
"""
Provides step definitions to:

    * run commands, like behave
    * create textual files within a working directory

TODO:
  matcher that ignores empty lines and whitespace and has contains comparison
"""

from __future__ import print_function
from behave import given, when, then, step, matchers
import command_shell
import command_util
import os
import shutil
from hamcrest import assert_that, equal_to, is_not, contains_string

# -----------------------------------------------------------------------------
# INIT:
# -----------------------------------------------------------------------------
matchers.register_type(int=int)
DEBUG = True


# -----------------------------------------------------------------------------
# STEPS:
# -----------------------------------------------------------------------------
@given(u'a new working directory')
def step_a_new_working_directory(context):
    """
    Creates a new, empty working directory
    """
    command_util.ensure_context_attribute_exists(context, "workdir", None)
    command_util.ensure_workdir_exists(context)
    shutil.rmtree(context.workdir, ignore_errors=True)

@given(u'I use the current directory as working directory')
def step_use_curdir_as_working_directory(context):
    """
    Uses the current directory as working directory
    """
    context.workdir = os.path.abspath(".")
    command_util.ensure_workdir_exists(context)

@given(u'a file named "{filename}" with')
def step_a_file_named_filename_with(context, filename):
    """
    Creates a textual file with the content provided as docstring.
    """
    assert context.text is not None, "ENSURE: multiline text is provided."
    assert not os.path.isabs(filename)
    command_util.ensure_workdir_exists(context)
    filename2 = os.path.join(context.workdir, filename)
    command_util.create_textfile_with_contents(filename2, context.text)

    # -- SPECIAL CASE: For usage with behave steps.
    if filename.endswith(".feature"):
        command_util.ensure_context_attribute_exists(context, "features", [])
        context.features.append(filename)

@given(u'an empty file named "{filename}"')
def step_an_empty_file_named_filename(context, filename):
    """
    Creates an empty file.
    """
    assert not os.path.isabs(filename)
    command_util.ensure_workdir_exists(context)
    filename2 = os.path.join(context.workdir, filename)
    command_util.create_textfile_with_contents(filename2, "")

@when(u'I run "{command}"')
def step_i_run_command(context, command):
    """
    Run a command as subprocess, collect its output and returncode.
    """
    command_util.ensure_workdir_exists(context)
    context.command_result = command_shell.run(command, cwd=context.workdir)
    command_util.workdir_save_coverage_files(context.workdir)
    if False and DEBUG:
        print("XXX run_command: {0}".format(command))
        print("XXX run_command.outout {0}".format(context.command_result.output))


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
    assert_that(context.command_result.returncode, equal_to(0))

@then(u'it should fail')
def step_it_should_fail(context):
    assert_that(context.command_result.returncode, is_not(equal_to(0)))

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
    assert_that(context.command_result.returncode, equal_to(0))


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
    assert context.text is not None, "ENSURE: multiline text is provided."
    expected_output = context.text
    if "{__WORKDIR__}" in expected_output or "{__CWD__}" in expected_output:
        expected_output = context.text.format(
            __WORKDIR__ = command_util.posixpath_normpath(context.workdir),
            __CWD__     = command_util.posixpath_normpath(os.getcwd())
        )
    command_output  = context.command_result.output
    expected_output = command_util.text_normalize(expected_output.strip())
    actual_output   = command_util.text_normalize(command_output.strip())
    if DEBUG:
        print("expected:\n{0}".format(expected_output))
        print("actual:\n{0}".format(actual_output))
    assert_that(actual_output, contains_string(expected_output))

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
    #    expected_output = context.text.format(
    #        __WORKDIR__ = command_util.posixpath_normpath(context.workdir),
    #        __CWD__     = command_util.posixpath_normpath(os.getcwd())
    #    )
    #    command_output  = context.command_result.output
    #    expected_output = command_util.text_normalize(expected_output.strip())
    #    actual_output   = command_util.text_normalize(command_output.strip())
    #    if DEBUG:
    #        print("expected:\n{0}".format(expected_output))
    #        print("actual:\n{0}".format(actual_output))
    #    assert_that(actual_output, is_not(contains_string(expected_output)))
    assert context.text is not None, "ENSURE: multiline text is provided."
    step_command_output_should_not_contain_text(context, context.text.strip())

@then(u'the command output should contain "{text}"')
def step_command_output_should_contain_text(context, text):
    '''
    EXAMPLE:
        ...
        Then the command output should contain "TEXT"
    '''
    if "{__WORKDIR__}" in text or "{__CWD__}" in text:
        text = text.format(
            __WORKDIR__ = command_util.posixpath_normpath(context.workdir),
            __CWD__     = command_util.posixpath_normpath(os.getcwd())
        )
    command_output  = context.command_result.output
    expected_output = command_util.text_normalize(text)
    actual_output   = command_util.text_normalize(command_output.strip())
    if DEBUG:
        print("expected:\n{0}".format(expected_output))
        print("actual:\n{0}".format(actual_output))
    assert_that(actual_output, contains_string(expected_output))

@then(u'the command output should not contain "{text}"')
def step_command_output_should_not_contain_text(context, text):
    '''
    EXAMPLE:
        ...
        then the command output should not contain "TEXT"
    '''
    text = text.format(
        __WORKDIR__ = command_util.posixpath_normpath(context.workdir),
        __CWD__     = command_util.posixpath_normpath(os.getcwd())
    )
    command_output  = context.command_result.output
    expected_output = command_util.text_normalize(text)
    actual_output   = command_util.text_normalize(command_output.strip())
    if DEBUG:
        print("expected:\n{0}".format(expected_output))
        print("actual:\n{0}".format(actual_output))
    assert_that(actual_output, is_not(contains_string(expected_output)))

@then(u'the command output should contain exactly "{text}"')
def step_command_output_should_contain_exactly_text(context, text):
    """
    Verifies that the command output of the last command contains the
    expected text.

    .. code-block:: gherkin

        When I run "echo Hello"
        Then the command output should contain "Hello"
    """
    expected_text = text
    if "{__WORKDIR__}" in text or "{__CWD__}" in text:
        expected_text = text.format(
            __WORKDIR__ = posixpath_normpath(context.workdir),
            __CWD__     = posixpath_normpath(os.getcwd())
        )
    actual_output  = context.command_result.output
    assert_that(actual_output, contains_string(expected_text))
    # REAL: textutil.assert_text_should_contain_exactly(actual_output, expected_text)

@then(u'the command output should contain exactly')
def step_command_output_should_contain_exactly_with_multiline_text(context):
    assert context.text is not None, "ENSURE: multiline text is provided."
    step_command_output_should_contain_exactly_text(context, context.text)

@then(u'the command output should not contain exactly "{text}"')
def step_command_output_should_not_contain_exactly_text(context, text):
    expected_text = text
    if "{__WORKDIR__}" in text or "{__CWD__}" in text:
        expected_text = text.format(
            __WORKDIR__ = posixpath_normpath(context.workdir),
            __CWD__     = posixpath_normpath(os.getcwd())
        )
    actual_output  = context.command_result.output
    assert_that(actual_output, is_not(contains_string(expected_text)))

@then(u'the command output should not contain exactly')
def step_command_output_should_contain_not_exactly_with_multiline_text(context):
    assert context.text is not None, "ENSURE: multiline text is provided."
    step_command_output_should_not_contain_exactly_text(context, context.text)

# -----------------------------------------------------------------------------
# STEPS FOR: Directories
# -----------------------------------------------------------------------------
@step(u'I remove the directory "{directory}"')
def step_remove_directory(context, directory):
    path_ = directory
    if not os.path.isabs(directory):
        path_ = os.path.join(context.workdir, os.path.normpath(directory))
    if os.path.isdir(path_):
        shutil.rmtree(path_, ignore_errors=True)
    assert_that(not os.path.isdir(path_))

@given(u'I ensure that the directory "{directory}" does not exist')
def step_given_the_directory_should_not_exist(context, directory):
    step_remove_directory(directory)


@then(u'the directory "{directory}" should exist')
def step_the_directory_should_exist(context, directory):
    path_ = directory
    if not os.path.isabs(directory):
        path_ = os.path.join(context.workdir, os.path.normpath(directory))
    assert_that(os.path.isdir(path_))

@then(u'the directory "{directory}" should not exist')
def step_the_directory_should_not_exist(context, directory):
    path_ = directory
    if not os.path.isabs(directory):
        path_ = os.path.join(context.workdir, os.path.normpath(directory))
    assert_that(not os.path.isdir(path_))

# -----------------------------------------------------------------------------
# ENVIRONMENT VARIABLES
# -----------------------------------------------------------------------------
@step(u'I set the environment variable "{env_name}" to "{env_value}"')
def step_I_set_the_environment_variable_to(context, env_name, env_value):
    if not hasattr(context, "environ"):
        context.environ = {}
    context.environ[env_name] = env_value
    os.environ[env_name] = env_value

@step(u'I remove the environment variable {env_name}')
def step_I_remove_the_environment_variable(context, env_name):
    if not hasattr(context, "environ"):
        context.environ = {}
    context.environ[env_name] = ""
    os.environ[env_name] = ""
    del context.environ[env_name]
    del os.environ[env_name]

