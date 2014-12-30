# -*- coding: utf-8 -*-
"""
Provides some utility functions related to text processing.
"""

from __future__ import absolute_import
import six
import sys


def make_indentation(indent_size, part=u" "):
    """
    Creates an indentation prefix string of the given size.
    """
    return indent_size * part


def indent(text, prefix):
    """
    Indent text or a number of text lines (with newline).

    :param lines:  Text lines to indent (as string or list of strings).
    :param prefix: Line prefix to use (as string).
    :return: Indented text (as unicode string).
    """
    lines = text
    newline = u""
    if isinstance(text, six.string_types):
        lines = text.splitlines(True)
    elif lines and not lines[0].endswith("\n"):
        # -- TEXT LINES: Without trailing new-line.
        newline = u"\n"
    # XXX return newline.join([prefix + six.text_type(line, errors="replace")
    return newline.join([prefix + six.text_type(line)  for line in lines])


def compute_words_maxsize(words):
    """
    Compute the maximum word size from a list of words (or strings).

    :param words: List of words (or strings) to use.
    :return: Maximum size of all words.
    """
    max_size = 0
    for word in words:
        if len(word) > max_size:
            max_size = len(word)
    return max_size


# -- MAYBE: def text(value, encoding=None, errors=None):
def text(value, encoding=None, errors=None):
    """Convert into a unicode string.

    :param value:  Value to convert into a unicode string (bytes, str, object).
    :return: Unicode string
    """
    if encoding is None:
        encoding = "unicode-escape"
    if errors is None:
        errors = "replace"

    if isinstance(value, six.text_type):
        # -- PASS-THROUGH UNICODE (efficiency):
        return value
    elif isinstance(value, six.binary_type):
        return six.text_type(value, encoding, errors)
    elif isinstance(value, bytes):
        # -- MAYBE: filename, path, etc.
        try:
            return value.decode(sys.getfilesystemencoding())
        except UnicodeError:
            return value.decode("utf-8", "replace")
    else:
        # -- CONVERT OBJECT TO TEXT:
        try:
            if six.PY2:
                data = str(value)
                text = six.text_type(data, "unicode-escape", "replace")
            else:
                text = six.text_type(value)
        except UnicodeError as e:
            text = six.text_type(e)
        return text
