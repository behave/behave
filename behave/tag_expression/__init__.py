# -*- coding: UTF-8 -*-
# pylint: disable=C0209
"""
Common module for tag-expressions:

* v1: old tag expressions (deprecating; superceeded by: cucumber-tag-expressions)
* v2: cucumber-tag-expressions

.. seealso::

    * https://docs.cucumber.io
    * https://docs.cucumber.io/cucumber/api/#tag-expressions
"""

from __future__ import absolute_import
from enum import Enum
import six
# -- NEW CUCUMBER TAG-EXPRESSIONS (v2):
from .parser import TagExpressionParser
from .model import Expression  # noqa: F401
# -- DEPRECATING: OLD-STYLE TAG-EXPRESSIONS (v1):
# BACKWARD-COMPATIBLE SUPPORT
from .v1 import TagExpression


# -----------------------------------------------------------------------------
# CLASS: TagExpressionProtocol
# -----------------------------------------------------------------------------
class TagExpressionProtocol(Enum):
    """Used to specify which tag-expression versions to support:

    * ANY: Supports tag-expressions v2 and v1 (as compatibility mode)
    * STRICT: Supports only tag-expressions v2 (better diagnostics)

    NOTE:
    * Some errors are not caught in ANY mode.
    """
    ANY = 1
    STRICT = 2

    @classmethod
    def default(cls):
        return cls.ANY

    @classmethod
    def choices(cls):
        return [member.name.lower() for member in cls]

    @classmethod
    def parse(cls, name):
        name2 = name.upper()
        for member in cls:
            if name2 == member.name:
                return member
        # -- OTHERWISE:
        message = "{0} (expected: {1})".format(name, ", ".join(cls.choices()))
        raise ValueError(message)

    def select_parser(self, tag_expression_text_or_seq):
        if self is self.STRICT:
            return parse_tag_expression_v2
        # -- CASE: TagExpressionProtocol.ANY
        return select_tag_expression_parser4any(tag_expression_text_or_seq)


    # -- SINGLETON FUNCTIONALITY:
    @classmethod
    def current(cls):
        """Return currently selected protocol instance."""
        return getattr(cls, "_current", cls.default())

    @classmethod
    def use(cls, member):
        """Specify which TagExpression protocol to use."""
        if isinstance(member, six.string_types):
            name = member
            member = cls.parse(name)
        assert isinstance(member, TagExpressionProtocol), "%s:%s" % (type(member), member)
        setattr(cls, "_current", member)



# -----------------------------------------------------------------------------
# FUNCTIONS:
# -----------------------------------------------------------------------------
def make_tag_expression(text_or_seq):
    """Build a TagExpression object by parsing the tag-expression (as text).

    :param text_or_seq:
        Tag expression text(s) to parse (as string, sequence<string>).
    :param protocol:  Tag-expression protocol to use.
    :return: TagExpression object to use.
    """
    parse_tag_expression = TagExpressionProtocol.current().select_parser(text_or_seq)
    return parse_tag_expression(text_or_seq)


def parse_tag_expression_v1(tag_expression_parts):
    """Parse old style tag-expressions and build a TagExpression object."""
    # -- HINT: DEPRECATING
    if isinstance(tag_expression_parts, six.string_types):
        tag_expression_parts = tag_expression_parts.split()
    elif not isinstance(tag_expression_parts, (list, tuple)):
        raise TypeError("EXPECTED: string, sequence<string>", tag_expression_parts)

    # print("parse_tag_expression_v1: %s" % " ".join(tag_expression_parts))
    return TagExpression(tag_expression_parts)


def parse_tag_expression_v2(text_or_seq):
    """Parse cucumber-tag-expressions and build a TagExpression object."""
    text = text_or_seq
    if isinstance(text, (list, tuple)):
        # -- ASSUME: List of strings
        sequence = text_or_seq
        terms = ["({0})".format(term) for term in sequence]
        text = " and ".join(terms)
    elif not isinstance(text, six.string_types):
        raise TypeError("EXPECTED: string, sequence<string>", text)

    if "@" in text:
        # -- NORMALIZE: tag-expression text => Remove '@' tag decorators.
        text = text.replace("@", "")
    text = text.replace("  ", " ")
    # DIAG: print("parse_tag_expression_v2: %s" % text)
    return TagExpressionParser.parse(text)


def is_any_equal_to_keyword(words, keywords):
    for keyword in keywords:
        for word in words:
            if keyword == word:
                return True
    return False


# -- CASE: TagExpressionProtocol.ANY
def select_tag_expression_parser4any(text_or_seq):
    """Select/Auto-detect which version of tag-expressions is used.

    :param text_or_seq: Tag expression text (as string, sequence<string>)
    :return: TagExpression parser to use (as function).
    """
    TAG_EXPRESSION_V1_KEYWORDS = [
        "~", "-", ","
    ]
    TAG_EXPRESSION_V2_KEYWORDS = [
        "and", "or", "not", "(", ")"
    ]

    text = text_or_seq
    if isinstance(text, (list, tuple)):
        # -- CASE: sequence<string> -- Sequence of tag_expression parts
        parts = text_or_seq
        text = " ".join(parts)
    elif not isinstance(text, six.string_types):
        raise TypeError("EXPECTED: string, sequence<string>", text)

    text = text.replace("(", " ( ").replace(")", " ) ")
    words = text.split()
    contains_v1_keywords = any((k in text) for k in TAG_EXPRESSION_V1_KEYWORDS)
    contains_v2_keywords = is_any_equal_to_keyword(words, TAG_EXPRESSION_V2_KEYWORDS)
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
