# -*- coding: UTF-8 -*-
"""
MAYBE: DUPLICATES: #449
NOTE: traceback2 (backport for Python2) solves the problem.

def foo(stop):
        raise Exception(u"по русски")

Result:

       File "features/steps/steps.py", line 8, in foo
          raise Exception(u"Ð¿Ð¾ Ñ�Ñ�Ñ�Ñ�ÐºÐ¸") <-- This is not
      Exception: по русски <-- This is OK

It happens here (https://github.com/behave/behave/blob/master/behave/model.py#L1299)
because traceback.format_exc() creates incorrect text.
You then convert it using _text() and result is also bad.

To fix it, you may take e.message which is correct and traceback.format_tb(sys.exc_info()[2])
which is also correct.
"""

from __future__ import print_function
from behave.textutil import text
from hamcrest.core import assert_that
from hamcrest.library import contains_string
import six
import pytest
if six.PY2:
    import traceback2 as traceback
else:
    import traceback


# -- XXX_JE_TEST_BALLOON:
try:
    import charset_normalizer
except ImportError:
    charset_normalizer = None


# -----------------------------------------------------------------------------
# TEST SUPPORT:
# -----------------------------------------------------------------------------
def problematic_step_impl(context):
    raise Exception(u"по русски")


# -----------------------------------------------------------------------------
# TEST SUITE:
# -----------------------------------------------------------------------------
@pytest.mark.parametrize("encoding", [None, "UTF-8", "unicode_escape"])
def test_issue(encoding):
    # ruff: noqa: E501
    """
    with encoding=UTF-8:
        File "/Users/jens/se/behave_main.unicode/tests/issues/test_issue0453.py", line 31, in problematic_step_impl
            raise Exception(u"по русски")
        Exception: \u043f\u043e \u0440\u0443\u0441\u0441\u043a\u0438

    with encoding=unicode_escape:
        File "/Users/jens/se/behave_main.unicode/tests/issues/test_issue0453.py", line 31, in problematic_step_impl
            raise Exception(u"Ð¿Ð¾ ÑÑÑÑÐºÐ¸")
        Exception: по русски
    """
    context = None
    text2 = b""
    _expected_text = u"по русски"
    try:
        problematic_step_impl(context)
    except Exception:
        text2 = traceback.format_exc()
        if charset_normalizer:
            if isinstance(text2, (bytes, bytearray)):
                charset_detector = charset_normalizer.from_bytes(text2)
            else:
                assert isinstance(text2, six.text_type)
                charset_detector = charset_normalizer.from_bytes(text2.encode())
            best_encoding = charset_detector.best().encoding
            print("CHARSET_DETECTOR.best.encoding=%s (encoding=%s)" %
                  (best_encoding, encoding))
            # DISABLED: encoding = best_encoding

    text3 = text(text2, encoding)
    print(u"EXCEPTION-TEXT: %s" % text3)
    assert_that(text3, contains_string(u'raise Exception(u"по русски"'))
    assert_that(text3, contains_string(u"Exception: по русски"))
