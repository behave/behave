# -*- coding: UTF-8 -*-
# BASED-ON: cucumber/tag-expressions/python/tests/unit/test_model.py
# pylint: disable=bad-whitespace

from cucumber_tag_expressions.model import Literal
from cucumber_tag_expressions.model import And, Or,  Not, True_
import pytest


# -----------------------------------------------------------------------------
# TEST SUITE: Model Classes
# -----------------------------------------------------------------------------
class TestAndOperation(object):

    @pytest.mark.parametrize("expected, tags, case", [
        (False, [],             "no_tags"),
        (False, ["a"],          "one tag: a"),
        (False, ["b"],          "one tag: b"),
        (False, ["other"],      "one tag: other"),
        ( True, ["a", "b"],     "both tags"),
        ( True, ["b", "a"],     "both tags (reversed)"),
        (False, ["a", "b2"],    "two tags: a, b2 (similar)"),
        (False, ["a", "other"], "two tags: a, other"),
    ])
    def test_evaluate2(self, expected, tags, case):
        expression = And(Literal("a"), Literal("b"))
        assert expression.evaluate(tags) == expected

    @pytest.mark.parametrize("expected, tags, case", [
        (False, [],         "no_tags"),
        (False, ["a"],      "one tag: a"),
        (False, ["b"],      "one tag: b"),
        (False, ["other"],  "one tag: other"),
        (False, ["a", "b"], "two tags: a, b"),
        (False, ["a", "c"], "two tags: a, c"),
        (False, ["a", "other"],     "two tags: a, other"),
        ( True, ["a", "b", "c"],    "all tags: a, b, c"),
        (False, ["other", "b", "c"], "three tags: other, b, c"),
    ])
    def test_evaluate3(self, expected, tags, case):
        expression = And(Literal("a"), Literal("b"), Literal("c"))
        assert expression.evaluate(tags) == expected

    @pytest.mark.parametrize("expected, expression", [
        ("( a and b )",         And(Literal("a"), Literal("b"))),
        ("( a and b and c )",   And(Literal("a"), Literal("b"), Literal("c"))),
        ("( a )",               And(Literal("a"))),
    ])
    def test_convert_to_string(self, expected, expression):
        assert expected == str(expression)


class TestOrOperation(object):
    @pytest.mark.parametrize("expected, tags, case", [
        (False, [],         "no_tags"),
        ( True, ["a"],      "one tag: a"),
        ( True, ["b"],      "one tag: b"),
        (False, ["other"],  "one tag: other"),
        ( True, ["a", "b"], "both tags"),
        ( True, ["b", "a"], "both tags (reversed)"),    # CASE: Ordering
        ( True, ["a", "b2"],    "two tags: a, b2"),     # CASE: SIMILARITY
        ( True, ["a", "other"], "two tags: a, other"),
        (False, ["other1", "other2"], "two tags: other1, other2"),
    ])
    def test_evaluate2(self, expected, tags, case):
        expression = Or(Literal("a"), Literal("b"))
        assert expression.evaluate(tags) == expected

    @pytest.mark.parametrize("expected, tags, case", [
        (False, [],         "no_tags"),
        ( True, ["a"],      "one tag: a"),
        ( True, ["b"],      "one tag: b"),
        ( True, ["c"],      "one tag: c"),
        (False, ["other"],  "one tag: other"),
        ( True, ["a", "b"],     "two tags: a, b"),
        ( True, ["a", "c"],     "two tags: a, c"),
        ( True, ["a", "other"], "two tags: a, other"),
        ( True, ["a", "b", "c"],     "all tags"),
        ( True, ["other", "b", "c"], "three tags: other, b, c"),
        (False, ["other", "other2"], "two tahs: other1, other2"),
    ])
    def test_evaluate3(self, expected, tags, case):
        expression = Or(Literal("a"), Literal("b"), Literal("c"))
        assert expression.evaluate(tags) == expected


class TestNotOperation(object):
    @pytest.mark.parametrize("expected, tags, case", [
        ( True, [],         "no_tags"),
        (False, ["a"],      "one tag: a"),
        ( True, ["other"],  "one tag: other"),
        (False, ["a", "other"], "two tags: a, other"),
        (False, ["other", "a"], "two tags: other, a (reversed)"),
        ( True, ["other1", "other2"], "two tags: other1, other2"),
    ])
    def test_evaluate1(self, expected, tags, case):
        expression = Not(Literal("a"))
        assert expression.evaluate(tags) == expected


class TestTrueOperation(object):
    @pytest.mark.parametrize("expected, tags, case", [
        ( True, [],         "no_tags"),
        ( True, ["a"],      "one tag: a"),
        ( True, ["other"],  "one tag: other"),
    ])
    def test_evaluate1(self, expected, tags, case):
        expression = True_()
        assert expression.evaluate(tags) == expected


class TestComposedExpression(object):
    @pytest.mark.parametrize("expected, tags, case", [
        ( True, [],         "no_tags"),
        ( True, ["a"],      "one tag: a"),
        ( True, ["b"],      "one tag: b"),
        ( True, ["other"],  "one tag: other"),
        (False, ["a", "b"],     "two tags: a, b"),
        (False, ["b", "a"], "   two tags: b, a (ordering)"),
        ( True, ["a", "b2"],    "two tags: a, b2 (similar)"),
        ( True, ["a", "other"], "two tags: a, other"),
    ])
    def test_evaluate_not__a_and_b(self, expected, tags, case):
        expression = Not(And(Literal("a"), Literal("b")))
        assert expression.evaluate(tags) == expected

    @pytest.mark.parametrize("expected, tags, case", [
        ( True, [],         "no_tags"),
        (False, ["a"],      "one tag: a"),
        (False, ["b"],      "one tag: b"),
        ( True, ["other"],  "one tag: other"),
        (False, ["a", "b"],     "two tags: a, b"),
        (False, ["b", "a"],     "two tags: b, a (ordering)"),
        (False, ["a", "b2"],    "two tags: a, b2 (similar)"),
        (False, ["a", "other"], "two tags: other"),
    ])
    def test_evaluate_not__a_or_b(self, expected, tags, case):
        expression = Not(Or(Literal("a"), Literal("b")))
        assert expression.evaluate(tags) == expected

    @pytest.mark.parametrize("expected, tags, case", [
        ( True, [],         "no_tags"),
        (False, ["a"],      "one tag: a"),
        ( True, ["b"],      "one tag: b"),
        ( True, ["other"],  "one tag: other"),
        ( True, ["a", "b"],     "two tags: a, b"),
        ( True, ["b", "a"],     "two tags: b, a (ordering)"),
        (False, ["a", "other"], "two tags: a, other"),
    ])
    def test_evaluate_not_a_or_b(self, expected, tags, case):
        expression = Or(Not(Literal("a")), Literal("b"))
        assert expression.evaluate(tags) == expected

    @pytest.mark.parametrize("expected, tags, case", [
        ( True, [],         "no_tags"),
        ( True, ["a"],      "one tag: a"),
        ( True, ["b"],      "one tag: b"),
        ( True, ["other"],  "one tag: other"),
        (False, ["a", "b"], "two tags: a, b"),
        ( True, ["a", "other"], "two tags: a, other"),  # CASE: Other
        (False, ["b", "a"],     "two tags: b, a (ordering)"),
    ])
    def test_evaluate_not_a_or_not_b(self, expected, tags, case):
        expression = Or(Not(Literal("a")), Not(Literal("b")))
        assert expression.evaluate(tags) == expected
