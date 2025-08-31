# -- TAG-EXPRESSIONS v2 (cucumber-tag-expressions with extensions):
from enum import Enum
from behave._types import require_type
from .parser import TagExpressionParser


# -----------------------------------------------------------------------------
# CLASS: TagExpression Parsers
# -----------------------------------------------------------------------------
class TagExpressionUtil:
    @staticmethod
    def normalize_tag(tag_text):
        """Strip leading, optional tag-prefix '@' from tags."""
        if not tag_text.startswith("@"):
            return tag_text
        # -- OTHERWISE: Strip leading '@' tag-prefix.
        return tag_text.replace("@", "")

    @classmethod
    def normalize_many_tags(cls, tags):
        return [cls.normalize_tag(text) for text in tags]

    @staticmethod
    def normalize_tag_expression(tag_expression_text):
        """Strip leading, optional tag-prefix '@' from tags."""
        return tag_expression_text.replace("@", "")


def _parse_tag_expression_v2(text):
    """
    Parse TagExpressions v2 (cucumber-tag-expressions) and
    build a TagExpression object.
    """
    if not isinstance(text, str):
        raise TypeError(f"{text!r} (expected: string)")

    if ((text.startswith('"') and text.endswith('"')) or
        (text.startswith("'") and text.endswith("'"))):
        # -- STRIP: double-quotes and single-quotes
        text = text[1:-1]

    text = text.strip()
    if "@" in text:
        # -- NORMALIZE: tag-expression text => Remove '@' tag decorators.
        text = TagExpressionUtil.normalize_tag_expression(text)
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
    __order__ = "V2, AUTO_DETECT"
    V2 = (_parse_tag_expression_v2,)
    AUTO_DETECT = (None,)  # -- AUTO-DETECT: Only V2

    # -- ALIASES: For backward compatibility.
    DEFAULT = V2
    STRICT = V2

    def __init__(self, parse_func):
        self._parse_func = parse_func

    def parse(self, text_or_seq):
        """
        Parse a TagExpression as string (or sequence-of-strings)
        and return the TagExpression object.
        """
        parse_func = self._parse_func
        if self is self.AUTO_DETECT:
            parse_func = _parse_tag_expression_v2
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
        if isinstance(member, str):
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
