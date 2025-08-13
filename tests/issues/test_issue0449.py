# ruff: noqa: E501
"""
SIMILAR: #453
NOTE: traceback2 (backport for Python2) solves the problem.

Either Exception text (as summary) or traceback python line shows
special characters correctly.

.. code-block:: python

    from behave import *
    from hamcrest.core import assert_that, equal_to

    @step("Russian text")
    def foo(stop):
        assert_that(False, equal_to(True), "Всё очень плохо") # cyrillic

And I also have UTF-8 as my console charset. Running this code leads to
"ASSERT FAILED: 'ascii' codec can't encode characters in position 0-5: ordinal not in range(128)" error.

That is because behave.textutil.text returns str(e) where 'e' is exception (https://github.com/behave/behave/blob/master/behave/textutil.py#L83).

Changing line 83 to str(value) solves this issue.
"""

import traceback
from behave.textutil import text
from hamcrest.core import assert_that, equal_to
from hamcrest.library import contains_string
import pytest


def foo():
    assert_that(False, equal_to(True), "Всё очень плохо")  # cyrillic

@pytest.mark.parametrize("encoding", [None, "UTF-8", "unicode_escape"])
def test_issue(encoding):
    _expected = "Всё очень плохо"
    try:
        foo()
    except Exception:
        text2 = traceback.format_exc()

    text3 = text(text2, encoding)
    print("EXCEPTION-TEXT: %s" % text3)
    print("text2: "+ text2)
    assert_that(text3, contains_string("AssertionError: Всё очень плохо"))


