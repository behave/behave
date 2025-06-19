from __future__ import absolute_import, print_function
import contextlib
import difflib
import os

from behave4cmd0 import textutil
from behave4cmd0.pathutil import posixpath_normpath


# -----------------------------------------------------------------------------
# CONSTANTS:
# -----------------------------------------------------------------------------
DEBUG = False


# -----------------------------------------------------------------------------
# UTILITY FUNCTIONS:
# -----------------------------------------------------------------------------
def print_differences(actual, expected):
    # diff = difflib.unified_diff(expected.splitlines(), actual.splitlines(),
    #                            "expected", "actual")
    diff = difflib.ndiff(expected.splitlines(), actual.splitlines())
    diff_text = u"\n".join(diff)
    print(u"DIFF (+ ACTUAL, - EXPECTED):\n{0}\n".format(diff_text))
    if DEBUG:
        print(u"expected:\n{0}\n".format(expected))
        print(u"actual:\n{0}\n".format(actual))


@contextlib.contextmanager
def on_assert_failed_print_details(actual, expected):
    """
    Print text details in case of assertion failed errors.

    .. sourcecode:: python

        with on_assert_failed_print_details(actual_text, expected_text):
            assert actual == expected
    """
    try:
        yield
    except AssertionError:
        print_differences(actual, expected)
        raise


@contextlib.contextmanager
def on_error_print_details(actual, expected):
    """
    Print text details in case of assertion failed errors.

    .. sourcecode:: python

        with on_error_print_details(actual_text, expected_text):
            ... # Do something
    """
    try:
        yield
    except Exception:
        print_differences(actual, expected)
        raise


def normalize_text_with_placeholders(ctx, text):
    expected_text = text
    if "{__WORKDIR__}" in expected_text or "{__CWD__}" in expected_text:
        expected_text = textutil.template_substitute(text,
            __WORKDIR__=posixpath_normpath(ctx.workdir),
            __CWD__=posixpath_normpath(os.getcwd())
        )
    return expected_text


def require_table(context, with_columns=None, columns_minsize=None):
    """
    Verifies that a table is provided (and has the expected table schema).
    Optional ensures that:

      * columns_minsize: Minimal number of table columns are provide
      * columns: Columns with required column names (headings) are provided

    :param context:
    :param with_columns:     List of required column names (optional).
    :param columns_minsize:  Minimal number of required columns (optional).
    :raise: AssertionError, on failure.
    """
    assert context.table is not None, "ENSURE: table is provided."
    if with_columns:
        table = context.table
        missing_columns = []
        for column_name in with_columns:
            if column_name not in table.headings:
                missing_columns.append(column_name)
        assert not missing_columns, \
            "REQUIRE-TABLE: Missing columns: %s" % ", ".join(missing_columns)
    if columns_minsize is not None:
        columns_size = len(context.table.headings)
        assert columns_minsize <= columns_size, \
            "REQUIRE-TABLE: Expect columns.size>=%s (but: columns.size=%s)" % \
            (columns_minsize, columns_size)
