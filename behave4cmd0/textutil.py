# -*- coding -*-
"""
Provides some command utility functions.

TODO:
  matcher that ignores empty lines and whitespace and has contains comparison
"""

from __future__ import unicode_literals
from hamcrest import assert_that, is_not, equal_to, contains_string
# DISABLED: from behave4cmd.hamcrest_text import matches_regexp
import codecs

DEBUG = False

# -----------------------------------------------------------------------------
# CLASS: TextProxy
# -----------------------------------------------------------------------------
# class TextProxy(object):
#     """
#     Simplifies conversion between (Unicode) string and its byte representation.
#     Provides a ValueObject to store a string or its byte representation.
#     Afterwards you can explicitly access both representations by using:
#
#     EXAMPLE:
#
#     .. testcode::
#
#         from behave4cmd.textutil import TextProxy
#         message = TextProxy("Hello world", encoding="UTF-8")
#         assert message.data == "Hello world"  # -- RAW DATA access.
#         assert isinstance(message.text, basestring)
#         assert isinstance(message.bytes, bytes)
#         assert message == "Hello world"
#         assert len(message) == len(message.data) == 11
#     """
#     encoding_errors = "strict"
#     default_encoding = "UTF-8"
#
#     def __init__(self, data=None, encoding=None, errors=None):
#         self.encoding = encoding or self.default_encoding
#         self.errors = errors or self.encoding_errors
#         self.set(data)
#
#     def get(self):
#         return self.data
#
#     def set(self, data):
#         self.data = data or ""
#         self._text = None
#         self._bytes = None
#
#     def clear(self):
#         self.set(None)
#
#     @property
#     def text(self):
#         """Provide access to string-representation of the data."""
#         if self._text is None:
#             if isinstance(self.data, basestring):
#                 _text = self.data
#             elif isinstance(self.data, bytes):
#                 _text = codecs.decode(self.data, self.encoding, self.errors)
#             else:
#                 _text = str(self.data)
#             self._text = _text
#         assert isinstance(self._text, basestring)
#         return self._text
#
#     @property
#     def bytes(self):
#         """Provide access to byte-representation of the data."""
#         if self._bytes is None:
#             if isinstance(self.data, bytes) and not isinstance(self.data, str):
#                 self._bytes = self.data
#             else:
#                 text = self.data
#                 if not isinstance(text, basestring):
#                     text = unicode(text)
#                 assert isinstance(text, basestring)
#                 self._bytes = codecs.encode(text, self.encoding, self.errors)
#         assert isinstance(self._bytes, bytes)
#         return self._bytes
#
#     def __repr__(self):
#         """Textual representation of this object."""
#         data = self.data or ""
#         prefix = ""
#         if isinstance(data, bytes) and not isinstance(data, basestring):
#             prefix= u"b"
# #        str(self.text)
# #        str(self.encoding)
# #        str(prefix)
# #        _ =  u"<TextProxy data[size=%d]=x'x', encoding=x>" % len(self)
# #        _ = u"<TextProxy data[size=x]=%s'x', encoding=x>" % prefix
# #        _ = u"<TextProxy data[size=x]=x'%s', encoding=x>" % self.text
# #        _ = u"<TextProxy data[size=x]=x'x', encoding=%s>" % self.encoding
#         return u"<TextProxy data[size=%d]=%s'%s', encoding=%s>" %\
#                (len(self), prefix, self.text, self.encoding)
#
#     def __str__(self):
#         """Conversion into str() object."""
#         return self.text
#
#     def __bytes__(self):
#         """Conversion into bytes() object."""
#         return self.bytes
#
#     def __bool__(self):
#         """Conversion into a bool value, used for truth testing."""
#         return bool(self.data)
#
#     def __iter__(self):
#         """Conversion into an iterator."""
#         return iter(self.data)
#
#     def __contains__(self, item):
#         """Check if item is contained in raw data."""
#         if isinstance(item, basestring):
#             return item in self.text
#         elif isinstance(item, bytes):
#             return item in self.bytes
#         else:
#             return item in self.data
#
#     def __len__(self):
#         if self.data is None:
#             return 0
#         return len(self.data)
#
#     def __nonzero__(self):
#         return len(self) > 0
#
#     def __eq__(self, other):
#         if isinstance(other, basestring):
#             return self.text == other
#         elif isinstance(other, bytes):
#             return self.bytes == other
#         else:
#             return self.data == other
#
#     def __ne__(self, other):
#         return not (self == other)
#
# -----------------------------------------------------------------------------
# UTILITY FUNCTIONS:
# -----------------------------------------------------------------------------
def template_substitute(text, **kwargs):
    """
    Replace placeholders in text by using the data mapping.
    Other placeholders that is not represented by data is left untouched.

    :param text:   Text to search and replace placeholders.
    :param data:   Data mapping/dict for placeholder key and values.
    :return: Potentially modified text with replaced placeholders.
    """
    for name, value in kwargs.items():
        placeholder_pattern = "{%s}" % name
        if placeholder_pattern in text:
            text = text.replace(placeholder_pattern, value)
    return text


def text_remove_empty_lines(text):
    """
    Whitespace normalization:

      - Strip empty lines
      - Strip trailing whitespace
    """
    lines = [ line.rstrip()  for line in text.splitlines()  if line.strip() ]
    return "\n".join(lines)

def text_normalize(text):
    """
    Whitespace normalization:

      - Strip empty lines
      - Strip leading whitespace  in a line
      - Strip trailing whitespace in a line
      - Normalize line endings
    """
    # if not isinstance(text, str):
    if isinstance(text, bytes):
        # -- MAYBE: command.ouput => bytes, encoded stream output.
        text = codecs.decode(text)
    lines = [ line.strip()  for line in text.splitlines()  if line.strip() ]
    return "\n".join(lines)

# -----------------------------------------------------------------------------
# ASSERTIONS:
# -----------------------------------------------------------------------------
def assert_text_should_equal(actual_text, expected_text):
    assert_that(actual_text, equal_to(expected_text))

def assert_text_should_not_equal(actual_text, expected_text):
    assert_that(actual_text, is_not(equal_to(expected_text)))

def assert_text_should_contain_exactly(text, expected_part):
    assert_that(text, contains_string(expected_part))

def assert_text_should_not_contain_exactly(text, expected_part):
    assert_that(text, is_not(contains_string(expected_part)))

def assert_text_should_contain(text, expected_part):
    assert_that(text, contains_string(expected_part))

def assert_text_should_not_contain(text, unexpected_part):
    assert_that(text, is_not(contains_string(unexpected_part)))

def assert_normtext_should_equal(actual_text, expected_text):
    expected_text2 = text_normalize(expected_text.strip())
    actual_text2   = text_normalize(actual_text.strip())
    assert_that(actual_text2, equal_to(expected_text2))

def assert_normtext_should_not_equal(actual_text, expected_text):
    expected_text2 = text_normalize(expected_text.strip())
    actual_text2   = text_normalize(actual_text.strip())
    assert_that(actual_text2, is_not(equal_to(expected_text2)))

def assert_normtext_should_contain(text, expected_part):
    expected_part2 = text_normalize(expected_part)
    actual_text    = text_normalize(text.strip())
    if DEBUG:
        print("expected:\n{0}".format(expected_part2))
        print("actual:\n{0}".format(actual_text))
    assert_text_should_contain(actual_text, expected_part2)

def assert_normtext_should_not_contain(text, unexpected_part):
    unexpected_part2 = text_normalize(unexpected_part)
    actual_text      = text_normalize(text.strip())
    if DEBUG:
        print("expected:\n{0}".format(unexpected_part2))
        print("actual:\n{0}".format(actual_text))
    assert_text_should_not_contain(actual_text, unexpected_part2)


# def assert_text_should_match_pattern(text, pattern):
#     """
#     Assert that the :attr:`text` matches the regular expression :attr:`pattern`.
#
#     :param text: Multi-line text (as string).
#     :param pattern: Regular expression pattern (as string, compiled regexp).
#     :raise: AssertionError, if text matches not the pattern.
#     """
#     assert_that(text, matches_regexp(pattern))
#
# def assert_text_should_not_match_pattern(text, pattern):
#     """
#     Assert that the :attr:`text` matches not the regular expression
#     :attr:`pattern`.
#
#     :param text: Multi-line text (as string).
#     :param pattern: Regular expression pattern (as string, compiled regexp).
#     :raise: AssertionError, if text matches the pattern.
#     """
#     assert_that(text, is_not(matches_regexp(pattern)))
#
# -----------------------------------------------------------------------------
# MAIN:
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    import doctest
    doctest.testmod()
