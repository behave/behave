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
import contextlib
import difflib
import os
import shutil
from behave import given, when, then, step, matchers # pylint: disable=no-name-in-module
from hamcrest import assert_that, equal_to, is_not
from behave4cmd0 import command_shell, command_util, pathutil, textutil
from behave4cmd0.pathutil import posixpath_normpath
from behave4cmd0.command_shell_proc import \
    TextProcessor, BehaveWinCommandOutputProcessor
# NOT-USED: from hamcrest import contains_string


# -----------------------------------------------------------------------------
# INIT:
# -----------------------------------------------------------------------------
matchers.register_type(int=int)
DEBUG = False
file_contents_normalizer = None
if BehaveWinCommandOutputProcessor.enabled:
    file_contents_normalizer = TextProcessor(BehaveWinCommandOutputProcessor())


# -----------------------------------------------------------------------------
# UTILITIES:
# -----------------------------------------------------------------------------
@contextlib.contextmanager
def on_assert_failed_print_details(actual, expected):
    """
    Print text details in case of assertation failed errors.

    .. sourcecode:: python

        with on_assert_failed_print_details(actual_text, expected_text):
            assert actual == expected
    """
    try:
        yield
    except AssertionError:
        # diff = difflib.unified_diff(expected.splitlines(), actual.splitlines(),
        #                            "expected", "actual")
        diff = difflib.ndiff(expected.splitlines(), actual.splitlines())
        diff_text = u"\n".join(diff)
        print(u"DIFF (+ ACTUAL, - EXPECTED):\n{0}\n".format(diff_text))
        if DEBUG:
            print(u"expected:\n{0}\n".format(expected))
            print(u"actual:\n{0}\n".format(actual))
        raise

@contextlib.contextmanager
def on_error_print_details(actual, expected):
    """
    Print text details in case of assertation failed errors.

    .. sourcecode:: python

        with on_error_print_details(actual_text, expected_text):
            ... # Do something
    """
    try:
        yield
    except Exception:
        diff = difflib.ndiff(expected.splitlines(), actual.splitlines())
        diff_text = u"\n".join(diff)
        print(u"DIFF (+ ACTUAL, - EXPECTED):\n{0}\n".format(diff_text))
        if DEBUG:
            print(u"expected:\n{0}\n".format(expected))
            print(u"actual:\n{0}".format(actual))
        raise

# -----------------------------------------------------------------------------
# STEPS: WORKING DIR
# -----------------------------------------------------------------------------
@given(u'a new working directory')
def step_a_new_working_directory(context):
    """Creates a new, empty working directory."""
    command_util.ensure_context_attribute_exists(context, "workdir", None)
    # MAYBE: command_util.ensure_workdir_not_exists(context)
    command_util.ensure_workdir_exists(context)
    # OOPS:
    shutil.rmtree(context.workdir, ignore_errors=True)
    command_util.ensure_workdir_exists(context)

@given(u'I use the current directory as working directory')
def step_use_curdir_as_working_directory(context):
    """
    Uses the current directory as working directory
    """
    context.workdir = os.path.abspath(".")
    command_util.ensure_workdir_exists(context)

@step(u'I use the directory "{directory}" as working directory')
def step_use_directory_as_working_directory(context, directory):
    """Uses the directory as new working directory"""
    command_util.ensure_context_attribute_exists(context, "workdir", None)
    current_workdir = context.workdir
    if not current_workdir:
        current_workdir = os.getcwd()

    if not os.path.isabs(directory):
        new_workdir = os.path.join(current_workdir, directory)
        exists_relto_current_dir = os.path.isdir(directory)
        exists_relto_current_workdir = os.path.isdir(new_workdir)
        if exists_relto_current_workdir or not exists_relto_current_dir:
            # -- PREFER: Relative to current workdir
            workdir = new_workdir
        else:
            assert exists_relto_current_workdir
            workdir = directory
        workdir = os.path.abspath(workdir)

    context.workdir = workdir
    command_util.ensure_workdir_exists(context)

# -----------------------------------------------------------------------------
# STEPS: Create files with contents
# -----------------------------------------------------------------------------
@given(u'a file named "{filename}" and encoding="{encoding}" with')
def step_a_file_named_filename_and_encoding_with(context, filename, encoding):
    """Creates a textual file with the content provided as docstring."""
    __encoding_is_valid = True
    assert context.text is not None, "ENSURE: multiline text is provided."
    assert not os.path.isabs(filename)
    assert __encoding_is_valid
    command_util.ensure_workdir_exists(context)
    filename2 = os.path.join(context.workdir, filename)
    pathutil.create_textfile_with_contents(filename2, context.text, encoding)


@given(u'a file named "{filename}" with')
def step_a_file_named_filename_with(context, filename):
    """Creates a textual file with the content provided as docstring."""
    step_a_file_named_filename_and_encoding_with(context, filename, "UTF-8")

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
    pathutil.create_textfile_with_contents(filename2, "")


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
    expected_text = text
    if "{__WORKDIR__}" in expected_text or "{__CWD__}" in expected_text:
        expected_text = textutil.template_substitute(text,
             __WORKDIR__ = posixpath_normpath(context.workdir),
             __CWD__     = posixpath_normpath(os.getcwd())
        )
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
    expected_text = text
    if "{__WORKDIR__}" in text or "{__CWD__}" in text:
        expected_text = textutil.template_substitute(text,
             __WORKDIR__ = posixpath_normpath(context.workdir),
             __CWD__     = posixpath_normpath(os.getcwd())
        )
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
    expected_text = text
    if "{__WORKDIR__}" in expected_text or "{__CWD__}" in expected_text:
        expected_text = textutil.template_substitute(text,
             __WORKDIR__ = posixpath_normpath(context.workdir),
             __CWD__     = posixpath_normpath(os.getcwd())
        )
    actual_output = context.command_result.output
    with on_assert_failed_print_details(actual_output, expected_text):
        textutil.assert_normtext_should_contain_multiple_times(actual_output,
                                                               expected_text,
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
    expected_text = text
    if "{__WORKDIR__}" in text or "{__CWD__}" in text:
        expected_text = textutil.template_substitute(text,
             __WORKDIR__ = posixpath_normpath(context.workdir),
             __CWD__     = posixpath_normpath(os.getcwd())
        )
    actual_output  = context.command_result.output
    textutil.assert_text_should_contain_exactly(actual_output, expected_text)


@then(u'the command output should not contain exactly "{text}"')
def step_command_output_should_not_contain_exactly_text(context, text):
    expected_text = text
    if "{__WORKDIR__}" in text or "{__CWD__}" in text:
        expected_text = textutil.template_substitute(text,
             __WORKDIR__ = posixpath_normpath(context.workdir),
             __CWD__     = posixpath_normpath(os.getcwd())
        )
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
    step_command_output_should_not_contain_text(context, context.text.strip())

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
    step_command_output_should_contain_text_multiple_times(context,
                                                           context.text, count)

@then(u'the command output should contain exactly')
def step_command_output_should_contain_exactly_with_multiline_text(context):
    assert context.text is not None, "REQUIRE: multi-line text"
    step_command_output_should_contain_exactly_text(context, context.text)


@then(u'the command output should not contain exactly')
def step_command_output_should_contain_not_exactly_with_multiline_text(context):
    assert context.text is not None, "REQUIRE: multi-line text"
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

@given(u'I ensure that the directory "{directory}" exists')
def step_given_ensure_that_the_directory_exists(context, directory):
    path_ = directory
    if not os.path.isabs(directory):
        path_ = os.path.join(context.workdir, os.path.normpath(directory))
    if not os.path.isdir(path_):
        os.makedirs(path_)
    assert_that(os.path.isdir(path_))

@given(u'I ensure that the directory "{directory}" does not exist')
def step_given_the_directory_should_not_exist(context, directory):
    step_remove_directory(context, directory)

@given(u'a directory named "{path}"')
def step_directory_named_dirname(context, path):
    assert context.workdir, "REQUIRE: context.workdir"
    path_ = os.path.join(context.workdir, os.path.normpath(path))
    if not os.path.exists(path_):
        os.makedirs(path_)
    assert os.path.isdir(path_)

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

@step(u'the directory "{directory}" exists')
def step_directory_exists(context, directory):
    """
    Verifies that a directory exists.

    .. code-block:: gherkin

        Given the directory "abc.txt" exists
         When the directory "abc.txt" exists
    """
    step_the_directory_should_exist(context, directory)

@step(u'the directory "{directory}" does not exist')
def step_directory_named_does_not_exist(context, directory):
    """
    Verifies that a directory does not exist.

    .. code-block:: gherkin

        Given the directory "abc/" does not exist
         When the directory "abc/" does not exist
    """
    step_the_directory_should_not_exist(context, directory)

# -----------------------------------------------------------------------------
# FILE STEPS:
# -----------------------------------------------------------------------------
@step(u'a file named "{filename}" exists')
def step_file_named_filename_exists(context, filename):
    """
    Verifies that a file with this filename exists.

    .. code-block:: gherkin

        Given a file named "abc.txt" exists
         When a file named "abc.txt" exists
    """
    step_file_named_filename_should_exist(context, filename)

@step(u'a file named "{filename}" does not exist')
@step(u'the file named "{filename}" does not exist')
def step_file_named_filename_does_not_exist(context, filename):
    """
    Verifies that a file with this filename does not exist.

    .. code-block:: gherkin

        Given a file named "abc.txt" does not exist
         When a file named "abc.txt" does not exist
    """
    step_file_named_filename_should_not_exist(context, filename)

@then(u'a file named "{filename}" should exist')
def step_file_named_filename_should_exist(context, filename):
    command_util.ensure_workdir_exists(context)
    filename_ = pathutil.realpath_with_context(filename, context)
    assert_that(os.path.exists(filename_) and os.path.isfile(filename_))

@then(u'a file named "{filename}" should not exist')
def step_file_named_filename_should_not_exist(context, filename):
    command_util.ensure_workdir_exists(context)
    filename_ = pathutil.realpath_with_context(filename, context)
    assert_that(not os.path.exists(filename_))

@step(u'I remove the file "{filename}"')
def step_remove_file(context, filename):
    path_ = filename
    if not os.path.isabs(filename):
        path_ = os.path.join(context.workdir, os.path.normpath(filename))
    if os.path.exists(path_) and os.path.isfile(path_):
        os.remove(path_)
    assert_that(not os.path.isfile(path_))


# -----------------------------------------------------------------------------
# STEPS FOR FILE CONTENTS:
# -----------------------------------------------------------------------------
@then(u'the file "{filename}" should contain "{text}"')
def step_file_should_contain_text(context, filename, text):
    expected_text = text
    if "{__WORKDIR__}" in text or "{__CWD__}" in text:
        expected_text = textutil.template_substitute(text,
            __WORKDIR__ = posixpath_normpath(context.workdir),
            __CWD__     = posixpath_normpath(os.getcwd())
        )
    file_contents = pathutil.read_file_contents(filename, context=context)
    file_contents = file_contents.rstrip()
    if file_contents_normalizer:
        # -- HACK: Inject TextProcessor as text normalizer
        file_contents = file_contents_normalizer(file_contents)
    with on_assert_failed_print_details(file_contents, expected_text):
        textutil.assert_normtext_should_contain(file_contents, expected_text)


@then(u'the file "{filename}" should not contain "{text}"')
def step_file_should_not_contain_text(context, filename, text):
    file_contents = pathutil.read_file_contents(filename, context=context)
    file_contents = file_contents.rstrip()
    textutil.assert_normtext_should_not_contain(file_contents, text)
    # DISABLED: assert_that(file_contents, is_not(contains_string(text)))


@then(u'the file "{filename}" should contain')
def step_file_should_contain_multiline_text(context, filename):
    assert context.text is not None, "REQUIRE: multiline text"
    step_file_should_contain_text(context, filename, context.text)


@then(u'the file "{filename}" should not contain')
def step_file_should_not_contain_multiline_text(context, filename):
    assert context.text is not None, "REQUIRE: multiline text"
    step_file_should_not_contain_text(context, filename, context.text)


# -----------------------------------------------------------------------------
# ENVIRONMENT VARIABLES
# -----------------------------------------------------------------------------
@step(u'I set the environment variable "{env_name}" to "{env_value}"')
def step_I_set_the_environment_variable_to(context, env_name, env_value):
    if not hasattr(context, "environ"):
        context.environ = {}
    context.environ[env_name] = env_value
    os.environ[env_name] = env_value

@step(u'I remove the environment variable "{env_name}"')
def step_I_remove_the_environment_variable(context, env_name):
    if not hasattr(context, "environ"):
        context.environ = {}
    context.environ[env_name] = ""
    os.environ[env_name] = ""
    del context.environ[env_name]
    del os.environ[env_name]
