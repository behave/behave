
from __future__ import absolute_import, print_function
import codecs
import os
import os.path
import shutil
from behave import given, then, step, register_type
from behave.parameter_type import parse_path_as_text, parse_unquoted_text
from behave4cmd0 import command_util, pathutil, textutil
from behave4cmd0.step_util import (
    normalize_text_with_placeholders,
    on_assert_failed_print_details,
    require_table,
)
from behave4cmd0.command_shell_proc import (
    TextProcessor, BehaveWinCommandOutputProcessor
)
from hamcrest import assert_that, has_items
# PREPARED: from behave4cmd0.pathutil import posixpath_normpath


file_contents_normalizer = None
if BehaveWinCommandOutputProcessor.enabled:
    file_contents_normalizer = TextProcessor(BehaveWinCommandOutputProcessor())


def is_encoding_valid(encoding):
    try:
        return bool(codecs.lookup(encoding))
    except LookupError:
        return False

# -----------------------------------------------------------------------------
# MODULE INIT
# -----------------------------------------------------------------------------
# PREPARED: register_type(Path=parse_path)
register_type(Path=parse_path_as_text)
register_type(Unquoted=parse_unquoted_text)


# -----------------------------------------------------------------------------
# STEPS FOR: Directories
# -----------------------------------------------------------------------------
@step(u'I remove the directory "{directory:Path}"')
def step_remove_directory(context, directory):
    path_ = directory
    if not os.path.isabs(directory):
        path_ = os.path.join(context.workdir, os.path.normpath(directory))
    if os.path.isdir(path_):
        shutil.rmtree(path_, ignore_errors=True)
    assert_that(not os.path.isdir(path_))


@given(u'I ensure that the directory "{directory:Path}" exists')
def step_given_ensure_that_the_directory_exists(context, directory):
    path_ = directory
    if not os.path.isabs(directory):
        path_ = os.path.join(context.workdir, os.path.normpath(directory))
    if not os.path.isdir(path_):
        os.makedirs(path_)
    assert_that(os.path.isdir(path_))


@given(u'I ensure that the directory "{directory:Path}" does not exist')
def step_given_the_directory_should_not_exist(context, directory):
    step_remove_directory(context, directory)


@given(u'a directory named "{path:Path}"')
def step_directory_named_dirname(context, path):
    assert context.workdir, "REQUIRE: context.workdir"
    path_ = os.path.join(context.workdir, os.path.normpath(path))
    if not os.path.exists(path_):
        os.makedirs(path_)
    assert os.path.isdir(path_)


@given(u'the directory "{directory:Path}" should exist')
@then(u'the directory "{directory:Path}" should exist')
def step_the_directory_should_exist(context, directory):
    path_ = directory
    if not os.path.isabs(directory):
        path_ = os.path.join(context.workdir, os.path.normpath(directory))
    assert_that(os.path.isdir(path_))


@given(u'the directory "{directory:Path}" should not exist')
@then(u'the directory "{directory:Path}" should not exist')
def step_the_directory_should_not_exist(context, directory):
    path_ = directory
    if not os.path.isabs(directory):
        path_ = os.path.join(context.workdir, os.path.normpath(directory))
    assert_that(not os.path.isdir(path_))


@step(u'the directory "{directory:Path}" exists')
def step_directory_exists(context, directory):
    """
    Verifies that a directory exists.

    .. code-block:: gherkin

        Given the directory "abc.txt" exists
         When the directory "abc.txt" exists
    """
    step_the_directory_should_exist(context, directory)


@step(u'the directory "{directory:Path}" does not exist')
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
@step(u'a file named "{filename:Path}" exists')
@step(u'the file named "{filename:Path}" exists')
def step_file_named_filename_exists(context, filename):
    """
    Verifies that a file with this filename exists.

    .. code-block:: gherkin

        Given a file named "abc.txt" exists
         When a file named "abc.txt" exists
    """
    step_file_named_filename_should_exist(context, filename)


@step(u'a file named "{filename:Path}" does not exist')
@step(u'the file named "{filename:Path}" does not exist')
def step_file_named_filename_does_not_exist(context, filename):
    """
    Verifies that a file with this filename does not exist.

    .. code-block:: gherkin

        Given a file named "abc.txt" does not exist
         When a file named "abc.txt" does not exist
    """
    step_file_named_filename_should_not_exist(context, filename)


@given(u'a file named "{filename:Path}" should exist')
@then(u'a file named "{filename:Path}" should exist')
def step_file_named_filename_should_exist(context, filename):
    command_util.ensure_workdir_exists(context)
    filename_ = pathutil.realpath_with_context(filename, context)
    assert_that(os.path.exists(filename_) and os.path.isfile(filename_))


@given(u'a file named "{filename:Path}" should not exist')
@then(u'a file named "{filename:Path}" should not exist')
def step_file_named_filename_should_not_exist(context, filename):
    command_util.ensure_workdir_exists(context)
    filename_ = pathutil.realpath_with_context(filename, context)
    assert_that(not os.path.exists(filename_))


@then(u'the following files should exist')
def step_the_following_files_should_exist_with_table(context):
    """
    Verifies that a list of files exist.

    .. code-block:: gherkin

        Then the following files should exist:
            | filename: |
            | lorem/ipsum/dolor |
            | lorem/ipsum/amet  |
    """
    # assert context.table, "ENSURE: table with 1 column is provided."
    require_table(context, columns_minsize=1)
    filenames = [row[0] for row in context.table.rows]
    existing_files = []
    for filename in filenames:
        filename_ = pathutil.realpath_with_context(filename, context)
        if os.path.exists(filename_) and os.path.isfile(filename_):
            existing_files.append(filename)
    # assert_that(existing_files, contains(*filenames))
    assert_that(existing_files, has_items(*filenames))


@then(u'the following files should not exist')
def step_the_following_files_should_not_exist_with_table(context):
    """
    Verifies that a list of files do not exist.

    .. code-block:: gherkin

        Then the following files should not exist:
            | filename: |
            | lorem/ipsum/amet  |
    """
    # assert context.table, "ENSURE: table with 1 column is provided."
    require_table(context, columns_minsize=1)
    filenames = [row[0] for row in context.table.rows]
    non_existing_files = []
    for filename in filenames:
        filename_ = pathutil.realpath_with_context(filename, context)
        if not os.path.exists(filename_) or os.path.isdir(filename_):
            non_existing_files.append(filename)
    # assert_that(non_existing_files, contains(*filenames))
    assert_that(non_existing_files, has_items(*filenames))

@step(u'the following files exist')
def step_the_following_files_exist_with_table(context):
    """
    Verifies that a list of files exist.

    .. code-block:: gherkin

        Given the following files exist:
            | filename: |
            | lorem/ipsum/dolor |
            | lorem/ipsum/amet  |
    """
    step_the_following_files_should_exist_with_table(context)

@step(u'the following files do not exist')
def step_the_following_files_do_not_exist_with_table(context):
    """
    Verifies that a list of files exist.

    .. code-block:: gherkin

        Given the following files do not exist:
            | filename: |
            | lorem/ipsum/dolor |
            | lorem/ipsum/amet  |
    """
    step_the_following_files_should_not_exist_with_table(context)


# -----------------------------------------------------------------------------
# STEPS FOR EXISTING FILES WITH FILE CONTENTS:
# -----------------------------------------------------------------------------
@then(u'the file "{filename:Path}" with encoding="{encoding:Unquoted}" should contain "{text}"')
def step_file_with_encoding_should_contain_text(context, filename, encoding, text):
    expected_text = normalize_text_with_placeholders(context, text)
    file_contents = pathutil.read_file_contents(filename, encoding=encoding,
                                                context=context)
    file_contents = file_contents.rstrip()
    if file_contents_normalizer:
        # -- HACK: Inject TextProcessor as text normalizer
        file_contents = file_contents_normalizer(file_contents)
    with on_assert_failed_print_details(file_contents, expected_text):
        textutil.assert_normtext_should_contain(file_contents, expected_text)


@then(u'the file "{filename:Path}" with encoding="{encoding:Unquoted}" should not contain "{text}"')
def step_file_with_encoding_should_not_contain_text(context, filename, encoding, text):
    expected_text = normalize_text_with_placeholders(context, text)
    file_contents = pathutil.read_file_contents(filename, encoding=encoding,
                                                context=context)
    file_contents = file_contents.rstrip()

    with on_assert_failed_print_details(file_contents, expected_text):
        textutil.assert_normtext_should_not_contain(file_contents, expected_text)


@then(u'the file "{filename:Path}" with encoding="{encoding:Unquoted}" should contain:')
def step_file_with_encoding_should_contain_multiline_text(context, filename, encoding):
    assert context.text is not None, "REQUIRE: multiline text"
    step_file_with_encoding_should_contain_text(context, filename,
                                                encoding, context.text)


@then(u'the file "{filename:Path}" with encoding="{encoding:Unquoted}" should not contain:')
def step_file_with_encoding_should_not_contain_multiline_text(context, filename, encoding):
    assert context.text is not None, "REQUIRE: multiline text"
    step_file_with_encoding_should_not_contain_text(context, filename,
                                                    encoding, context.text)


@then(u'the file "{filename:Path}" should contain "{text}"')
def step_file_should_contain_text(context, filename, text):
    expected_text = normalize_text_with_placeholders(context, text)
    file_contents = pathutil.read_file_contents(filename, context=context)
    file_contents = file_contents.rstrip()
    if file_contents_normalizer:
        # -- HACK: Inject TextProcessor as text normalizer
        file_contents = file_contents_normalizer(file_contents)
    with on_assert_failed_print_details(file_contents, expected_text):
        textutil.assert_normtext_should_contain(file_contents, expected_text)


@then(u'the file "{filename:Path}" should not contain "{text}"')
def step_file_should_not_contain_text(context, filename, text):
    expected_text = normalize_text_with_placeholders(context, text)
    file_contents = pathutil.read_file_contents(filename, context=context)
    file_contents = file_contents.rstrip()

    with on_assert_failed_print_details(file_contents, expected_text):
        textutil.assert_normtext_should_not_contain(file_contents, expected_text)
    # DISABLED: assert_that(file_contents, is_not(contains_string(text)))


@then(u'the file "{filename:Path}" should contain')
@then(u'the file "{filename}" should contain:')
def step_file_should_contain_multiline_text(context, filename):
    assert context.text is not None, "REQUIRE: multiline text"
    step_file_should_contain_text(context, filename, context.text)


@then(u'the file "{filename:Path}" should not contain')
@then(u'the file "{filename:Path}" should not contain:')
def step_file_should_not_contain_multiline_text(context, filename):
    assert context.text is not None, "REQUIRE: multiline text"
    step_file_should_not_contain_text(context, filename, context.text)


# -----------------------------------------------------------------------------
# STEPS FOR CREATING FILES WITH FILE CONTENTS:
# -----------------------------------------------------------------------------
@given(u'a file named "{filename:Path}" using encoding="{encoding:Unquoted}" with')
@given(u'a file named "{filename:Path}" using encoding="{encoding:Unquoted}" with:')
def step_a_file_named_filename_and_encoding_with(context, filename, encoding):
    """Creates a textual file with the content provided as docstring."""
    assert context.text is not None, "ENSURE: multiline text is provided."
    assert not os.path.isabs(filename)
    assert is_encoding_valid(encoding), "INVALID: encoding=%s;" % encoding
    command_util.ensure_workdir_exists(context)
    filename2 = os.path.join(context.workdir, filename)
    pathutil.create_textfile_with_contents(filename2, context.text, encoding)


@given(u'a file named "{filename:Path}" with')
@given(u'a file named "{filename:Path}" with:')
def step_a_file_named_filename_with(context, filename):
    """Creates a textual file with the content provided as docstring."""
    step_a_file_named_filename_and_encoding_with(context, filename, "UTF-8")

    # -- SPECIAL CASE: For usage with behave steps.
    if filename.endswith(".feature"):
        command_util.ensure_context_attribute_exists(context, "features", [])
        context.features.append(filename)


@given(u'an empty file named "{filename:Path}"')
def step_an_empty_file_named_filename(context, filename):
    """
    Creates an empty file.
    """
    assert not os.path.isabs(filename)
    command_util.ensure_workdir_exists(context)
    filename2 = os.path.join(context.workdir, filename)
    pathutil.create_textfile_with_contents(filename2, "")


@step(u'I remove the file "{filename:Path}"')
@step(u'I remove the file named "{filename:Path}"')
def step_remove_file(context, filename):
    path_ = filename
    if not os.path.isabs(filename):
        path_ = os.path.join(context.workdir, os.path.normpath(filename))
    if os.path.exists(path_) and os.path.isfile(path_):
        os.remove(path_)
    assert_that(not os.path.isfile(path_))
