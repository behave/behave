# ruff: noqa: E731
"""
Unit tests for :mod:`behave.textutil`.
"""

import codecs
import pytest
from behave.textutil import text


# -----------------------------------------------------------------------------
# TEST SUPPORT:
# -----------------------------------------------------------------------------
class ConvertableToUnicode:
    """Class that can be converted into a unicode string.
    If parameter is a bytes-string, it is converted into unicode.

    .. code-block:: python

        obj1 = ConvertableToUnicode("'Ärgernis")
        obj2 = ConvertableToUnicode("'Ärgernis".encode("latin-1")

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
        if isinstance(text, bytes):
            text = codecs.decode(text, self.encoding)
        return text


class ConvertableToString:
    encoding = "utf-8"

    def __init__(self, text, encoding=None):
        self.text = text
        self.encoding = encoding or self.__class__.encoding

    def __str__(self):
        text = self.text
        if isinstance(text, bytes):
            text = codecs.decode(text, self.encoding)
        return text


class ConvertableToPy2String:
    encoding = "utf-8"

    def __init__(self, text, encoding=None):
        self.text = text
        self.encoding = encoding or self.__class__.encoding

    def __str__(self):
        text = self.text
        if isinstance(text, bytes):
            text = codecs.decode(text, self.encoding)
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

UNICODE_TEXT_VALUES1 = [ "Alice", "Bob"]
UNICODE_TEXT_VALUES = [ "Café", "100€ (Euro)", "Frühaufsteher"]
BYTES_TEXT_TUPLES_WITH_UTF8_ENCODING = [
    (codecs.encode(_text, "utf-8"), _text) for _text in UNICODE_TEXT_VALUES
]


class TestTextConversion:
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
        ("'Ärgernis", "UTF-8"),
        ("'Übermut", "UTF-8"),
    ])
    def test_text__with_bytes_value_and_encoding(self, text_value, encoding):
        bytes_value = text_value.encode(encoding)
        assert isinstance(bytes_value, bytes)

        actual = text(bytes_value, encoding)
        assert isinstance(actual, str)
        assert actual == text_value

    def test_text__with_exception_traceback(self): pass

    @pytest.mark.parametrize("text_value", UNICODE_TEXT_VALUES)
    def test_text__with_object_convertable_to_unicode(self, text_value):
        obj = ConvertableToUnicode(text_value)
        actual_text = text(obj)
        assert actual_text == text_value
        assert isinstance(actual_text, str)

    # @pytest.mark.parametrize("expected, text_value, encoding", [
    #     ("'Ärgernis", "Ärgernis".encode("UTF-8"), "UTF-8"),
    #     ("'Übermut",  "Übermut".encode("latin-1"), "latin-1"),
    # ])
    # def test_text__with_object_convertable_to_unicode2(self, expected,
    #                                                    text_value, encoding):
    #     obj = ConvertableToUnicode(text_value, encoding)
    #     actual_text = text(obj)
    #     assert actual_text == expected
    #     assert isinstance(actual_text, str)

    @pytest.mark.parametrize("text_value", UNICODE_TEXT_VALUES)
    def test_text__with_object_convertable_to_string(self, text_value):
        obj = ConvertableToString(text_value)
        actual_text = text(obj)
        assert actual_text == text_value
        assert isinstance(actual_text, str)


class TestObjectToTextConversion:
    """Unit tests for the :func:`behave.textutil.text()` function.
    Explore case with object-to-text conversion.
    """
    ENCODING = "UTF-8"

    # -- CASE: object=exception
    @pytest.mark.parametrize("message", [
        "Ärgernis", "Übermütig"
    ])
    def test_text__with_assert_failed_and_unicode_message(self, message):
        with pytest.raises(AssertionError) as e:
            assert False, message

        # -- FOR: pytest < 5.0
        # expected = "AssertionError: %s" % message
        text2 = text(e.value)
        assert "AssertionError" in text(e)
        assert message in text2, "OOPS: text=%r" % text2

    @pytest.mark.parametrize("exception_class, message", [
        (AssertionError, "Ärgernis"),
        (RuntimeError, "Übermütig"),
    ])
    def test_text__with_raised_exception_and_unicode_message(self,
                                                             exception_class,
                                                             message):
        with pytest.raises(exception_class) as e:
            raise exception_class(message)

        # -- FOR: pytest < 5.0
        # expected = "AssertionError: %s" % message
        # expected = "%s: %s" % (exception_class.__name__, message)
        text2 = text(e.value)
        assert isinstance(text2, str)
        assert exception_class.__name__ in str(e)
        assert message in text2, "OOPS: text=%r" % text2
