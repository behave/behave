# -*- coding: UTF-8 -*-
"""
Tag expression v2 parser, based on :mod:`cucumber-tag-expressions`.

Extension(s):

* Supports matching of tag names, like: "@foo.* or @*.foo"


.. seealso::

    * https://docs.cucumber.io
    * https://docs.cucumber.io/cucumber/api/#tag-expressions
"""

from __future__ import absolute_import
from cucumber_tag_expressions.parser import (
    TagExpressionParser as _TagExpressionParser,
    # PROVIDE: Similar interface like: cucumber_tag_expressions.parser
    TagExpressionError
)
from cucumber_tag_expressions.model import Literal
from .model_ext import Matcher


class TagExpressionParser(_TagExpressionParser):
    """Extended TagExpressionParser to parse boolean tag-expressions.
    Extended TagExpressionParser supports matching tag names by name-patterns.

    TagExpressionParser supports boolean operations:

    * and (as binary operation:  a and b)
    * or  (as binary operation:  a or b)
    * not (as unary operation:   not a)

    In addition, parenthesis can be used to group expressions, like::

        a and (b or c)
        (a and not b) or (c and d)

    EXAMPLES:

    .. code-block:: python

        # -- UNARY OPTIONS
        text11 = "not foo" = "(not foo)"
        expression = TagExpressionParser.parse(text11)
        assert False == expression.evaluate(["foo"])
        assert True  == expression.evaluate(["other"])

        # -- BINARY OPERATIONS:
        text21 = "foo and bar" = "(foo and bar)"
        expression = TagExpressionParser.parse(text21)
        assert True  == expression.evaluate(["foo", "bar"])
        assert False == expression.evaluate(["foo"])
        assert False == expression.evaluate([])

        text22 = "foo or bar"  = "(foo or bar)"
        expression = TagExpressionParser.parse(text22)
        assert True  == expression.evaluate(["foo", "bar"])
        assert True  == expression.evaluate(["foo", "other"])
        assert False == expression.evaluate([])

        # -- TAG MATCHING EXTENSION: Match tag-parts with wildcards
        text31 = "foo.* or bar"  = "(foo.* or bar)"
        expression = TagExpressionParser.parse(text31)
        assert True  == expression.evaluate(["foo.bar", "bar"])
        assert True  == expression.evaluate(["other", "foo.more"])
        assert False == expression.evaluate([])


    .. note::

        Name wildcard expressions are based on :mod:`fnmatch`
        (File name pattern matching).

    .. seealso::

        * :class:`cucumber_tag_expressions.parser:TagExpressionParser`
        * https://docs.cucumber.io
        * https://docs.cucumber.io/cucumber/api/#tag-expressions
    """

    @classmethod
    def make_operand(cls, text):
        """Creates operand-object from parsed text."""
        if Matcher.contains_wildcards(text):
            # -- USE MATCHER: Text contains matcher-wildcards.
            return Matcher(text)
        else:
            return Literal(text)
