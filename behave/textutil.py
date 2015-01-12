# -*- coding: utf-8 -*-
"""
Provides some utility functions related to text processing.
"""


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
    if isinstance(text, basestring):
        lines = text.splitlines(True)
    elif lines and not lines[0].endswith("\n"):
        # -- TEXT LINES: Without trailing new-line.
        newline = u"\n"
    return newline.join([prefix + unicode(line) for line in lines])


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
