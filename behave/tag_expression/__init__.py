# -*- coding: UTF-8 -*-
"""
Common module for tag-expressions:

* v1: old tag expressions (deprecating; superceeded by: cucumber-tag-expressions)
* v2: cucumber-tag-expressions

.. seealso::

    * https://docs.cucumber.io
    * https://docs.cucumber.io/cucumber/api/#tag-expressions
"""

from __future__ import absolute_import
import six
# -- NEW CUCUMBER TAG-EXPRESSIONS (v2):
from .parser import TagExpressionParser
# -- OLD-STYLE TAG-EXPRESSIONS (v1):
# HINT: BACKWARD-COMPATIBLE (deprecating)
from .v1 import TagExpression


# -----------------------------------------------------------------------------
# FUNCTIONS:
# -----------------------------------------------------------------------------
def make_tag_expression(tag_expression_text):
    """Build a TagExpression object by parsing the tag-expression (as text).

    :param tag_expression_text:     Tag expression text to parse (as string).
    :return: TagExpression object to use.
    """
    parse_tag_expression = select_tag_expression_parser(tag_expression_text)
    return parse_tag_expression(tag_expression_text)


def parse_tag_expression_v1(tag_expression_parts):
    """Parse old style tag-expressions and build a TagExpression object."""
    # -- HINT: DEPRECATING
    if isinstance(tag_expression_parts, six.string_types):
        tag_expression_parts = tag_expression_parts.split()
    # print("parse_tag_expression_v1: %s" % " ".join(tag_expression_parts))
    return TagExpression(tag_expression_parts)


def parse_tag_expression_v2(tag_expression_text):
    """Parse cucumber-tag-expressions and build a TagExpression object."""
    text = tag_expression_text
    if not isinstance(text, six.string_types):
        # -- ASSUME: List of strings
        assert isinstance(text, (list, tuple))
        text = " and ".join(text)

    if "@" in text:
        # -- NORMALIZE: tag-expression text => Remove '@' tag decorators.
        text = text.replace("@", "")
    text = text.replace("  ", " ")
    # print("parse_tag_expression_v2: %s" % text)
    return TagExpressionParser.parse(text)


def check_for_complete_keywords(words, keywords):
    for keyword in keywords:
        for word in words:
            if keyword == word:
                return True
    return False


def select_tag_expression_parser(tag_expression_text):
    """Select/Auto-detect which version of tag-expressions is used.

    :param tag_expression_text:  Tag expression text (as string)
    :return: TagExpression parser to use (as function).
    """
    TAG_EXPRESSION_V1_KEYWORDS = [
        "~", "-", ","
    ]
    TAG_EXPRESSION_V2_KEYWORDS = [
        "and", "or", "not", "(", ")"
    ]

    text = tag_expression_text
    if not isinstance(text, six.string_types):
        # -- ASSUME: List of strings
        assert isinstance(text, (list, tuple))
        text = " ".join(text)

    text = text.replace("(", " ( ").replace(")", " ) ")
    words = text.split()
    contains_v1_keywords = any([(k in text) for k in TAG_EXPRESSION_V1_KEYWORDS])
    contains_v2_keywords = check_for_complete_keywords(words, TAG_EXPRESSION_V2_KEYWORDS)
    # contains_v2_keywords = any([(k in text) for k in TAG_EXPRESSION_V2_KEYWORDS])
    # DIAG: print("XXX select_tag_expression_parser: v1=%r, v2=%r, words.size=%d (tags: %r)" % \
    # DIAG:      (contains_v1_keywords, contains_v2_keywords, len(words), text))
    if contains_v2_keywords:
        # -- USE: Use cucumber-tag-expressions
        return parse_tag_expression_v2
    elif contains_v1_keywords or len(words) > 1:
        # -- CASE 1: "-@foo", "~@foo" (negated)
        # -- CASE 2: "@foo @bar"
        return parse_tag_expression_v1

    # -- OTHERWISSE: Use cucumber-tag-expressions
    # CASE: "@foo" (1 tag)
    return parse_tag_expression_v2
