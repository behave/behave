# -- NEEDED-FOR: issue1252.feature
import os
import sys
from pathlib import Path
from behave import given, then, register_type
from behave.fixture import fixture, use_fixture
from behave.parameter_type import parse_unquoted_text
from behave4cmd0.pathutil import realpath_with_context
import chardet
from assertpy import assert_that


# -----------------------------------------------------------------------------
# TEST SUPPORT: Parameter Types for Steps
# -----------------------------------------------------------------------------
register_type(Unquoted=parse_unquoted_text)


# -----------------------------------------------------------------------------
# TEST SUPPORT: Fixtures
# -----------------------------------------------------------------------------
@fixture
def save_current_environment_variables_and_restore(ctx):
    current_env = os.environ.copy()
    def restore_environment_vars():
        os.environ.clear()
        os.environ.update(current_env)
    ctx.add_cleanup(restore_environment_vars)
    return


# -----------------------------------------------------------------------------
# TEST SUPPORT
# -----------------------------------------------------------------------------
def _setup_console_encoding_on_windows(encoding, language=None):
    encoding = encoding.lower()
    code_page = None
    if language is None:
        language = "en_US"
    if "utf-8" in encoding or encoding == "cp65001":
        code_page = "65001"
        encoding_value = "{language}.{encoding}".format(
            language=language, encoding=encoding
        )
        os.environ["LANG"] = encoding_value
        os.environ["PYTHONUTF8"] = "1"
    if encoding.startswith("windows-"):
        code_page = encoding.replace("windows-", "")
    elif encoding.startswith("cp"):
        code_page = encoding[2:]

    os.environ["PYTHONIOENCODING"] = encoding
    result = os.system("chcp {code_page}".format(code_page=code_page))
    assert_that(result).is_equal_to(0)


def _setup_console_encoding_on_posix(encoding, language=None):
    # if encoding == "cp65001":
    #    encoding = "utf-8"
    encoding_value = encoding
    if language is None:
        language = "en_US"
    if language:
        encoding_value = "{language}.{encoding}".format(
            language=language, encoding=encoding
        )

    os.environ["LANG"] = encoding_value
    os.environ["LC_ALL"] = encoding_value
    os.environ["LC_CTYPE"] = encoding_value
    os.environ["PYTHONIOENCODING"] = encoding


def select_setup_console_encoding():
    if sys.platform == "win32":
        return _setup_console_encoding_on_windows
    # -- OTHERWISE:
    return _setup_console_encoding_on_posix


# -----------------------------------------------------------------------------
# STEPS
# -----------------------------------------------------------------------------
@given(u'I setup the console encoding to "{encoding:Unquoted}" for language "{language:Unquoted}"')
def step_given_setup_console_encoding_to_with_language(ctx, encoding, language=None):
    use_fixture(save_current_environment_variables_and_restore, ctx)
    setup_console_encoding = select_setup_console_encoding()
    setup_console_encoding(encoding, language=language)


@given(u'I setup the console encoding to "{encoding:Unquoted}"')
def step_given_setup_console_encoding_to(ctx, encoding):
    step_given_setup_console_encoding_to_with_language(ctx, encoding)


@then(u'the chardet file encoding for "{filename}" should be "{encoding}"')
def step_chardet_file_encoding_should_be(ctx, filename, encoding):
    workdir_filename = realpath_with_context(filename, ctx)
    contents_as_bytes = Path(workdir_filename).read_bytes()
    actual_data = chardet.detect(contents_as_bytes)
    assert_that(actual_data["encoding"]).is_equal_to(encoding)
