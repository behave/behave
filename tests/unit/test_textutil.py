# -*- coding: UTF-8 -*-
"""
Unit tests for :mod:`behave.textutil`.
"""

from __future__ import absolute_import, print_function
from behave.textutil import text, is_ascii_encoding, select_best_encoding
import pytest
import codecs
import six

# -----------------------------------------------------------------------------
# TEST SUPPORT:
# -----------------------------------------------------------------------------
class ConvertableToUnicode(object):
    """Class that can be converted into a unicode string.
    If parameter is a bytes-string, it is converted into unicode.

    .. code-block:: python

        obj1 = ConvertableToUnicode(u"Ärgernis")
        obj2 = ConvertableToUnicode(u"Ärgernis".encode("latin-1")

        # -- CASE Python2: string is a bytes-string
        text_value21 = unicode(obj1)
        text_value22 = unicode(obj2)

        # -- CASE Python3: string is a unicode-string
        text_value31 = str(obj1)
        text_value32 = str(obj2)
    """
    encoding = "utf-8"

    def __init__(self, text, encoding=None):
        self.text = text
        self.encoding = encoding or self.__class__.encoding

    def __str__(self):
        """Convert into a unicode string."""
        text = self.text
        if isinstance(text, six.binary_type):
            text = codecs.decode(text, self.encoding)
        return text

    if six.PY2:
        __unicode__ = __str__
        __str__ = lambda self: self.__unicode__().encode(self.encoding)

class ConvertableToString(object):
    encoding = "utf-8"

    def __init__(self, text, encoding=None):
        self.text = text
        self.encoding = encoding or self.__class__.encoding

    def __str__(self):
        text = self.text
        if isinstance(text, six.binary_type):
            text = codecs.decode(text, self.encoding)
        return text

    if six.PY2:
        __unicode__ = __str__

        def __str__(self):
            # MAYBE: self.__unicode__().encode(self.encoding)
            text = self.text
            if isinstance(text, six.text_type):
                text = codecs.encode(text, self.encoding)
            return text

class ConvertableToPy2String(object):
    encoding = "utf-8"

    def __init__(self, text, encoding=None):
        self.text = text
        self.encoding = encoding or self.__class__.encoding

    def __str__(self):
        text = self.text
        if six.PY2:
            if isinstance(text, six.text_type):
                text = codecs.encode(text, self.encoding)
        else:
            if isinstance(text, six.bytes_type):
                text = codecs.decode(text, self.encoding)
        return text

    if six.PY2:
        __unicode__ = __str__

        def __str__(self):
            # MAYBE: self.__unicode__().encode(self.encoding)
            text = self.text
            if isinstance(text, six.text_type):
                text = codecs.encode(text, self.encoding)
            return text

# def raise_exception(exception_class, *args):
#     raise exception_class(*args)
#
# def catch_raised_exception_and_return_as_text(exception_class, *args, **kwargs):
#     encoding = kwargs.pop("encoding", None)
#     try:
#         raise_exception(*args)
#     except Exception as e:
#         return text(e, encoding=encoding)


# -----------------------------------------------------------------------------
# TEST SUITE
# -----------------------------------------------------------------------------
xfail = pytest.mark.xfail
requires_python2 = pytest.mark.skipif(not six.PY2, reason="requires python2")

UNICODE_TEXT_VALUES1 = [u"Alice", u"Bob"]
UNICODE_TEXT_VALUES = [u"Café", u"100€ (Euro)", u"Frühaufsteher"]
BYTES_TEXT_TUPLES_WITH_UTF8_ENCODING = [
    (codecs.encode(_text, "utf-8"), _text) for _text in UNICODE_TEXT_VALUES
]


class TestTextConversion(object):
    """Unit tests for the :func:`behave.textutil.text()` function."""

    @pytest.mark.parametrize("value", UNICODE_TEXT_VALUES)
    def test_text__with_unicode_value(self, value):
        value_id = id(value)
        actual_text = text(value)
        assert actual_text == value
        assert id(actual_text) == value_id  # PARANOID check w/ unicode copy.

    @pytest.mark.parametrize("bytes_value, expected_text",
                             BYTES_TEXT_TUPLES_WITH_UTF8_ENCODING)
    def test_text__with_bytes_value(self, bytes_value, expected_text):
        actual_text = text(bytes_value)
        assert actual_text == expected_text


    @pytest.mark.parametrize("text_value, encoding", [
        (u"Ärgernis", "UTF-8"),
        (u"Übermut", "UTF-8"),
    ])
    def test_text__with_bytes_value_and_encoding(self, text_value, encoding):
        bytes_value = text_value.encode(encoding)
        assert isinstance(bytes_value, bytes)

        actual = text(bytes_value, encoding)
        assert isinstance(actual, six.text_type)
        assert actual == text_value

    def test_text__with_exception_traceback(self): pass

    @pytest.mark.parametrize("text_value", UNICODE_TEXT_VALUES)
    def test_text__with_object_convertable_to_unicode(self, text_value):
        obj = ConvertableToUnicode(text_value)
        actual_text = text(obj)
        assert actual_text == text_value
        assert isinstance(actual_text, six.text_type)

    # @pytest.mark.parametrize("expected, text_value, encoding", [
    #     (u"Ärgernis", u"Ärgernis".encode("UTF-8"), "UTF-8"),
    #     (u"Übermut",  u"Übermut".encode("latin-1"), "latin-1"),
    # ])
    # def test_text__with_object_convertable_to_unicode2(self, expected,
    #                                                    text_value, encoding):
    #     obj = ConvertableToUnicode(text_value, encoding)
    #     actual_text = text(obj)
    #     assert actual_text == expected
    #     assert isinstance(actual_text, six.text_type)

    @pytest.mark.parametrize("text_value", UNICODE_TEXT_VALUES)
    def test_text__with_object_convertable_to_string(self, text_value):
        obj = ConvertableToString(text_value)
        actual_text = text(obj)
        assert actual_text == text_value
        assert isinstance(actual_text, six.text_type)

    @xfail
    @requires_python2
    @pytest.mark.parametrize("text_value", UNICODE_TEXT_VALUES)
    def test_text__with_object_convertable_to_py2string_only(self, text_value):
        class ConvertableToPy2String(object):
            """Lacks feature: convertable-to-unicode (only: to-string)"""
            def __init__(self, message=""):
                self.message = message or ""
                if self.message and isinstance(self.message, six.text_type):
                    self.message = self.message.encode("UTF-8")

            def __str__(self):
                # assert isinstance(self.message, str)
                return self.message

        obj = ConvertableToPy2String(text_value.encode("UTF-8"))
        actual = text(obj)
        print(u"actual: %s" % actual)
        print(u"text_value: %s" % text_value)
        assert actual == text_value


class TestObjectToTextConversion(object):
    """Unit tests for the :func:`behave.textutil.text()` function.
    Explore case with object-to-text conversion.
    """
    ENCODING = "UTF-8"

    # -- CASE: object=exception
    @pytest.mark.parametrize("message", [
        u"Ärgernis", u"Übermütig"
    ])
    def test_text__with_assert_failed_and_unicode_message(self, message):
        with pytest.raises(AssertionError) as e:
            assert False, message

        text2 = text(e)
        expected = u"AssertionError: %s" % message
        assert text2.endswith(expected)

    @requires_python2
    @pytest.mark.parametrize("message", [
        u"Ärgernis", u"Übermütig"
    ])
    def test_text__with_assert_failed_and_bytes_message(self, message):
        # -- ONLY PYTHON2: Use case makes no sense for Python 3.
        bytes_message = message.encode(self.ENCODING)
        with pytest.raises(AssertionError) as e:
            assert False, bytes_message

        text2 = text(e)
        expected = u"AssertionError: %s" % message
        assert text2.endswith(expected)

    @pytest.mark.parametrize("exception_class, message", [
        (AssertionError, u"Ärgernis"),
        (RuntimeError, u"Übermütig"),
    ])
    def test_text__with_raised_exception_and_unicode_message(self,
                                                             exception_class,
                                                             message):
        with pytest.raises(exception_class) as e:
            raise exception_class(message)

        text2 = text(e)
        expected = u"%s: %s" % (exception_class.__name__, message)
        assert isinstance(text2, six.text_type)
        assert text2.endswith(expected)

    @requires_python2
    @pytest.mark.parametrize("exception_class, message", [
        (AssertionError, u"Ärgernis"),
        (RuntimeError, u"Übermütig"),
    ])
    def test_text__with_raised_exception_and_bytes_message(self, exception_class,
                                                           message):
        # -- ONLY PYTHON2: Use case makes no sense for Python 3.
        bytes_message = message.encode(self.ENCODING)
        with pytest.raises(exception_class) as e:
            raise exception_class(bytes_message)

        text2 = text(e)
        unicode_message = bytes_message.decode(self.ENCODING)
        expected = u"%s: %s" % (exception_class.__name__, unicode_message)
        assert isinstance(text2, six.text_type)
        assert text2.endswith(expected)
        # -- DIAGNOSTICS:
        print(u"text2: "+ text2)
        print(u"expected: " + expected)
