# -*- coding: UTF-8 -*-
# pylint: disable=bad-whitespace
# -- PARTIALLY BASED-ON: cucumber/tag-expressions/python/tests/functional/test_tag_expressions.py
"""
Functional tests for ``TagExpressionParser.parse()`` and ``Expression.evaluate()``.
"""

from __future__ import absolute_import, print_function
from behave.tag_expression.parser import \
    TagExpressionParser, TagExpressionError
import pytest


# -----------------------------------------------------------------------------
# TEST SUITE: TagExpressionParser.parse() and Expression.evaluate(tags) chain
# -----------------------------------------------------------------------------
# BASED-ON: cucumber/tag-expressions/python/tests/functional/test_tag_expressions.py
class TestTagExpression(object):
    # correct_test_data = [
    #     ("a and b", "( a and b )"),
    #     ("a or (b)", "( a or b )"),
    #     ("not   a", "not ( a )"),
    #     ("( a and b ) or ( c and d )", "( ( a and b ) or ( c and d ) )"),
    #     ("not a or b and not c or not d or e and f",
    #         "( ( ( not ( a ) or ( b and not ( c ) ) ) or not ( d ) ) or ( e and f ) )"),
    # ]
    # -- FROM: Java
    # {"a and b", "( a and b )"},
    # {"a or b", "( a or b )"},
    # {"not a", "not ( a )"},
    # {"( a and b ) or ( c and d )", "( ( a and b ) or ( c and d ) )"},
    # {"not a or b and not c or not d or e and f",
    #  "( ( ( not ( a ) or ( b and not ( c ) ) ) or not ( d ) ) or ( e and f ) )"},
    # {"not a\\(1\\) or b and not c or not d or e and f",
    #  "( ( ( not ( a\\(1\\) ) or ( b and not ( c ) ) ) or not ( d ) ) or ( e and f ) )"}

    @pytest.mark.parametrize("tag_expression_text, expected, tags, case", [
        ("",  True, [],            "no_tags"),
        ("",  True, ["a"],         "one tag: a"),
        ("",  True, ["other"],     "one tag: other"),
    ])
    def test_empty_expression_is_true(self, tag_expression_text, expected, tags, case):
        tag_expression = TagExpressionParser.parse(tag_expression_text)
        assert expected == tag_expression.evaluate(tags)


    @pytest.mark.parametrize("tag_expression_text, expected, tags, case", [
        ("not a", False, ["a", "other"], "two tags: a, other"),
        ("not a", False, ["a"],     "one tag: a"),
        ("not a",  True, ["other"], "one tag: other"),
        ("not a",  True, [],        "no_tags"),
    ])
    def test_not_operation(self, tag_expression_text, expected, tags, case):
        tag_expression = TagExpressionParser.parse(tag_expression_text)
        assert expected == tag_expression.evaluate(tags)


    def test_complex_example(self):
        tag_expression_text = "not @a or @b and not @c or not @d or @e and @f"
        tag_expression = TagExpressionParser.parse(tag_expression_text)
        assert False == tag_expression.evaluate("@a @c @d".split())

    def test_with_escaped_chars(self):
        # -- SOURCE: TagExpressionParserTest.java
        # Expression expr = parser.parse("((not @a\\(1\\) or @b\\(2\\)) and not @c\\(3\\) or not @d\\(4\\) or @e\\(5\\) and @f\\(6\\))");
        # assertFalse(expr.evaluate(asList("@a(1) @c(3) @d(4)".split(" "))));
        # assertTrue(expr.evaluate(asList("@b(2) @e(5) @f(6)".split(" "))));
        print("NOT-SUPPORTED-YET")

    @pytest.mark.parametrize("tag_part", ["not", "and", "or"])
    def test_fails_when_only_operators_are_used(self, tag_part):
        with pytest.raises(TagExpressionError):
            # -- EXAMPLE: text = "or or"
            text = "{part} {part}".format(part=tag_part)
            TagExpressionParser.parse(text)
    # -- JAVA-TESTS-END-HERE: TagExpressionParserTest.java


    @pytest.mark.parametrize("tag_expression_text, expected, tags, case", [
        ("a and b",  True, ["a", "b"],          "both tags"),
        ("a and b",  True, ["a", "b", "other"], "both tags and more"),
        ("a and b", False, ["a"],               "one tag: a"),
        ("a and b", False, ["b"],               "one tag: b"),
        ("a and b", False, ["other"],           "one tag: other"),
        ("a and b", False, [],                  "no_tags"),
    ])
    def test_and_operation(self, tag_expression_text, expected, tags, case):
        tag_expression = TagExpressionParser.parse(tag_expression_text)
        assert expected == tag_expression.evaluate(tags)

    @pytest.mark.parametrize("tag_expression_text, expected, tags, case", [
        ("a or b",  True, ["a", "b"],           "both tags"),
        ("a or b",  True, ["a", "b", "other"], "both tags and more"),
        ("a or b",  True, ["a"],        "one tag: a"),
        ("a or b",  True, ["b"],        "one tag: b"),
        ("a or b", False, ["other"],    "one tag: other"),
        ("a or b", False, [],           "no_tags"),
    ])
    def test_or_operation(self, tag_expression_text, expected, tags, case):
        tag_expression = TagExpressionParser.parse(tag_expression_text)
        assert expected == tag_expression.evaluate(tags)

    @pytest.mark.parametrize("tag_expression_text, expected, tags, case", [
        ("a",  True, ["a", "other"], "two tags: a, other"),
        ("a",  True, ["a"],         "one tag: a"),
        ("a", False, ["other"],     "one tag: other"),
        ("a", False, [],            "no_tags"),
    ])
    def test_literal(self, tag_expression_text, expected, tags, case):
        tag_expression = TagExpressionParser.parse(tag_expression_text)
        assert expected == tag_expression.evaluate(tags)

    # NOTE: CANDIDATE for property-based testing
    @pytest.mark.parametrize("tag_expression_text, expected, tags, case", [
        ("a and b",  True, ["a", "b"], "two tags: a, b"),
        ("a and b", False, ["a"],      "one tag: a"),
        ("a and b", False, [],         "no_tags"),
        ("a or b",   True, ["a", "b"],  "two tags: a, b"),
        ("a or b",   True, ["b"],       "one tag: b"),
        ("a or b",  False, [],          "no_tags"),
        ("a and b or c",  True, ["a", "b", "c"],     "three tags: a, b, c"),
        ("a and b or c",  True, ["a", "other", "c"], "three tags: a, other, c"),
        ("a and b or c",  True, ["a", "b", "other"], "three tags: a, b, other"),
        ("a and b or c",  True, ["a", "b"], "two tags: a, b"),
        ("a and b or c",  True, ["a", "c"], "two tags: a, c"),
        ("a and b or c", False, ["a"],      "one tag: a"),
        ("a and b or c",  True, ["c"],      "one tag: c"),
        ("a and b or c", False, [],         "not tags"),
    ])
    def test_not_not_expression_sameas_expression(self, tag_expression_text, expected, tags, case):
        not2_tag_expression_text = "not not "+ tag_expression_text
        tag_expression1 = TagExpressionParser.parse(tag_expression_text)
        tag_expression2 = TagExpressionParser.parse(not2_tag_expression_text)
        value1 = tag_expression1.evaluate(tags)
        value2 = tag_expression2.evaluate(tags)
        assert value1 == value2
        assert expected == value1


# -----------------------------------------------------------------------------
# TEST SUITE: TagExpressionParser Extension(s)
# -----------------------------------------------------------------------------
class TestTagExpressionExtension(object):
    """Extension of cucumber-tag-expressions to support tag-name-matching."""

    @pytest.mark.parametrize("tag_expression_text, expected, tags, case", [
        ("a.*",  False, [],         "no tags"),
        ("a.*",  True,  ["a.bar"],  "matching_tag"),
        ("a.*",  False, ["a_bar"],  "similar_not_matching_tag"),
        ("a.*",  False, ["A.bar"],  "case_insensitive"),
        ("a.*",  False, ["other"],  "other tag"),
        ("*.a",  False, [],         "no tags"),
        ("*.a",  True,  ["bar.a"],  "matching_tag"),
        ("*.a",  False, ["bar_a"],  "similar_not_matching_tag"),
        ("*.a",  False, ["other"],  "other tag"),
        ("*.a.*", False, [], "no tags"),
        ("*.a.*", True, ["bar.a.baz"], "matching_tag"),
        ("*.a.*", False, ["bar_a.baz"], "similar_not_matching_tag"),
        ("*.a.*", False, ["other"], "other tag"),
    ])
    def test_matcher(self, tag_expression_text, expected, tags, case):
        tag_expression = TagExpressionParser.parse(tag_expression_text)
        assert expected == tag_expression.evaluate(tags)

    @pytest.mark.parametrize("tag_expression_text, expected, tags, case", [
        ("not a.*",  True,  [],         "no tags"),
        ("not a.*",  False, ["a.bar"],  "matching_tag"),
        ("not a.*",  True,  ["a_bar"],  "similar_not_matching_tag"),
        ("not a.*",  True,  ["A.bar"],  "case_insensitive"),
        ("not a.*",  True,  ["other"],  "other tag"),
    ])
    def test_not_matcher(self, tag_expression_text, expected, tags, case):
        tag_expression = TagExpressionParser.parse(tag_expression_text)
        assert expected == tag_expression.evaluate(tags)
