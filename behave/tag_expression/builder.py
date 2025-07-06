from __future__ import absolute_import
from enum import Enum
import six

from behave._types import require_type
# -- NEW TAG-EXPRESSIONSx v2 (cucumber-tag-expressions with extensions):
from .parser import TagExpressionParser, TagExpressionError
from .model import Matcher as _MatcherV2
# -- BACKWARD-COMPATIBLE SUPPORT:
# DEPRECATING: OLD-STYLE TAG-EXPRESSIONS (v1)
from .v1 import TagExpression as _TagExpressionV1


# -----------------------------------------------------------------------------
# CLASS: TagExpression Parsers
# -----------------------------------------------------------------------------
def _parse_tag_expression_v1(tag_expression_parts):
    """Parse old style tag-expressions and build a TagExpression object."""
    # -- HINT: DEPRECATING
    if isinstance(tag_expression_parts, six.string_types):
        tag_expression_parts = tag_expression_parts.split()
    elif not isinstance(tag_expression_parts, (list, tuple)):
        raise TypeError("EXPECTED: string, sequence<string>", tag_expression_parts)

    # print("_parse_tag_expression_v1: %s" % " ".join(tag_expression_parts))
    return _TagExpressionV1(tag_expression_parts)


def _parse_tag_expression_v2(text_or_seq):
    """
    Parse TagExpressions v2 (cucumber-tag-expressions) and
    build a TagExpression object.
    """
    text = text_or_seq
    if isinstance(text, (list, tuple)):
        # -- BACKWARD-COMPATIBLE: Sequence mode will be removed (DEPRECATING)
        # ASSUME: List of strings
        sequence = text_or_seq
        terms = ["({0})".format(term) for term in sequence]
        text = " and ".join(terms)
    elif not isinstance(text, six.string_types):
        raise TypeError("EXPECTED: string, sequence<string>", text)

    if "@" in text:
        # -- NORMALIZE: tag-expression text => Remove '@' tag decorators.
        text = text.replace("@", "")
    text = text.replace("  ", " ")
    # DIAG: print("_parse_tag_expression_v2: %s" % text)
    return TagExpressionParser.parse(text)


# -----------------------------------------------------------------------------
# CLASS: TagExpressionProtocol
# -----------------------------------------------------------------------------
class TagExpressionProtocol(Enum):
    """Used to specify which tag-expression versions to support:

    * AUTO_DETECT: Supports tag-expressions v2 and v1 (as compatibility mode)
    * STRICT: Supports only tag-expressions v2 (better diagnostics)

    NOTE:
    * Some errors are not caught in AUTO_DETECT mode.
    """
    __order__ = "V1, V2, AUTO_DETECT"
    V1 = (_parse_tag_expression_v1,)
    V2 = (_parse_tag_expression_v2,)
    AUTO_DETECT = (None,)  # -- AUTO-DETECT: V1 or V2

    # -- ALIASES: For backward compatibility.
    STRICT = V2
    DEFAULT = AUTO_DETECT

    def __init__(self, parse_func):
        self._parse_func = parse_func

    def parse(self, text_or_seq):
        """
        Parse a TagExpression as string (or sequence-of-strings)
        and return the TagExpression object.
        """
        parse_func = self._parse_func
        if self is self.AUTO_DETECT:
            parse_func = _select_tag_expression_parser4auto(text_or_seq)
        return parse_func(text_or_seq)

    # -- CLASS-SUPPORT:
    @classmethod
    def choices(cls):
        """Returns a list of TagExpressionProtocol enum-value names."""
        return [member.name.lower() for member in cls]

    @classmethod
    def from_name(cls, name):
        """Parse the Enum-name and return the Enum-Value."""
        name2 = name.upper()
        for member in cls:
            if name2 == member.name:
                return member

        # -- SPECIAL-CASE: ALIASES
        if name2 == "STRICT":
            return cls.STRICT

        # -- OTHERWISE:
        message = "{0} (expected: {1})".format(name, ", ".join(cls.choices()))
        raise ValueError(message)

    # -- SINGLETON FUNCTIONALITY:
    @classmethod
    def current(cls):
        """Return the currently selected protocol default value."""
        return getattr(cls, "_current", cls.DEFAULT)

    @classmethod
    def use(cls, member):
        """Specify which TagExpression protocol to use per default."""
        if isinstance(member, six.string_types):
            name = member
            member = cls.from_name(name)
        require_type(member, TagExpressionProtocol)
        setattr(cls, "_current", member)


# -----------------------------------------------------------------------------
# FUNCTIONS:
# -----------------------------------------------------------------------------
def make_tag_expression(text_or_seq, protocol=None):
    """
    Build a TagExpression object by parsing the tag-expression (as text).
    The current TagExpressionProtocol is used to parse the tag-expression.

    :param text_or_seq:
        Tag expression text(s) to parse (as string, sequence<string>).
    :param protocol:  TagExpressionProtocol value to use (or None).
        If None is used, the the current TagExpressionProtocol is used.
    :return: TagExpression object to use.
    """
    if protocol is None:
        protocol = TagExpressionProtocol.current()
    return protocol.parse(text_or_seq)


# -----------------------------------------------------------------------------
# SUPPORT CASE: TagExpressionProtocol.AUTO_DETECT
# -----------------------------------------------------------------------------
def _any_word_is_keyword(words, keywords):
    """Checks if any word is a keyword."""
    for keyword in keywords:
        for word in words:
            if keyword == word:
                return True
    return False


def _any_word_contains_keyword(words, keywords):
    for keyword in keywords:
        for word in words:
            if keyword in word:
                return True
    return False


def _any_word_contains_wildcards(words):
    """
    Checks if any word (as tag) contains wildcard(s) supported by TagExpression v2.

    :param words:   List of words/tags.
    :return: True, if any word contains wildcard(s).
    """
    return any([_MatcherV2.contains_wildcards(word) for word in words])


def _any_word_starts_with(words, prefixes):
    for prefix in prefixes:
        if any([w.startswith(prefix) for w in words]):
            return True
    return False


def _select_tag_expression_parser4auto(text_or_seq):
    """Select/Auto-detect which version of tag-expressions is used.

    :param text_or_seq: Tag expression text (as string, sequence<string>)
    :return: TagExpression parser to use (as function).
    """
    TAG_EXPRESSION_V1_NOT_PREFIXES = ["~", "-"]
    TAG_EXPRESSION_V1_OTHER_KEYWORDS = [","]
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
    contains_v1_prefixes = _any_word_starts_with(words, TAG_EXPRESSION_V1_NOT_PREFIXES)
    contains_v1_keywords = (_any_word_contains_keyword(words, TAG_EXPRESSION_V1_OTHER_KEYWORDS) or
                            # any((k in text) for k in TAG_EXPRESSION_V1_OTHER_KEYWORDS) or
                            contains_v1_prefixes)
    contains_v2_keywords = (_any_word_is_keyword(words, TAG_EXPRESSION_V2_KEYWORDS) or
                            _any_word_contains_wildcards(words))

    if contains_v1_prefixes and contains_v2_keywords:
        raise TagExpressionError("Contains TagExpression v2 and v1 NOT-PREFIX: %s" % text)

    if contains_v2_keywords:
        # -- USE: Use cucumber-tag-expressions
        return _parse_tag_expression_v2
    elif contains_v1_keywords or len(words) > 1:
        # -- CASE 1: "-@foo", "~@foo" (negated)
        # -- CASE 2: "@foo @bar"
        return _parse_tag_expression_v1

    # -- OTHERWISE: Use cucumber-tag-expressions -- One tag/term (CASE: "@foo")
    return _parse_tag_expression_v2
