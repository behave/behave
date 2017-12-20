# -*- coding: UTF-8 -*-
"""
SIMILAR: #453
NOTE: traceback2 (backport for Python2) solves the problem.

Either Exception text (as summary) or traceback python line shows
special characters correctly.

.. code-block:: python

    # -*- coding=utf-8 -*-
    from behave import *
    from hamcrest.core import assert_that, equal_to

    @step("Russian text")
    def foo(stop):
        assert_that(False, equal_to(True), u"Всё очень плохо") # cyrillic

And I also have UTF-8 as my console charset. Running this code leads to
"Assertion Failed: 'ascii' codec can't encode characters in position 0-5: ordinal not in range(128)" error.

That is becase behave.textutil.text returns six.text_type(e) where 'e' is exception (https://github.com/behave/behave/blob/master/behave/textutil.py#L83).

Changing line 83 to six.text_type(value) solves this issue.
"""

from __future__ import print_function
from behave.textutil import text
from hamcrest.core import assert_that, equal_to
from hamcrest.library import contains_string
import six
import pytest
if six.PY2:
    import traceback2 as traceback
else:
    import traceback


def foo():
    assert_that(False, equal_to(True), u"Всё очень плохо")  # cyrillic

@pytest.mark.parametrize("encoding", [None, "UTF-8", "unicode_escape"])
def test_issue(encoding):
    expected = u"Всё очень плохо"
    try:
        foo()
    except Exception as e:
        text2 = traceback.format_exc()

    text3 = text(text2, encoding)
    print(u"EXCEPTION-TEXT: %s" % text3)
    print(u"text2: "+ text2)
    assert_that(text3, contains_string(u"AssertionError: Всё очень плохо"))


