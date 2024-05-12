# -*- coding: UTF-8 -*-
# pylint: disable=bad-whitespace

from __future__ import absolute_import
from behave.tag_expression.model import Literal, Matcher, Never
import pytest


# -----------------------------------------------------------------------------
# TEST SUITE: Model Class Extension(s)
# -----------------------------------------------------------------------------
# NOT-NEEDED: xfail = pytest.mark.xfail
class TestExpression(object):

    def test_check__can_be_used(self):
        tag_expression = Literal("foo")
        assert tag_expression.check(["foo"]) is True
        assert tag_expression.check(["other"]) is False


class TestMatcher(object):
    @pytest.mark.parametrize("expected, tag, case", [
        (True, "foo.bar", "startswith_1"),
        (True, "foo.bax", "startswith_2"),
        (True, "foo.",    "exact_match"),
        (False, "something.foo.bar", "not_starts_with"),
        (False, "foo_bar", "similar"),
    ])
    def test_evaluate_with_startswith_pattern(self, expected, tag, case):
        expression = Matcher("foo.*")
        assert expression.evaluate([tag]) == expected

    @pytest.mark.parametrize("expected, tag, case", [
        (True, "bar.foo", "endswith_1"),
        (True, "bax.foo", "endswith_2"),
        (True, ".foo",    "exact_match"),
        (False, "something.foo.bar", "not_endswith"),
        (False, "bar_foo", "similar"),
    ])
    def test_evaluate_with_endswith_pattern(self, expected, tag, case):
        expression = Matcher("*.foo")
        assert expression.evaluate([tag]) == expected

    @pytest.mark.parametrize("expected, tag, case", [
        (False, "bar.foo", "startwith_1"),
        (False, "foo.bax", "endswith_2"),
        (True, "bar.foo.bax", "contains"),
        (True, ".foo.",    "exact_match"),
        (False, "bar_foo.bax", "similar"),
    ])
    def test_evaluate_with_contains_pattern(self, expected, tag, case):
        expression = Matcher("*.foo.*")
        assert expression.evaluate([tag]) == expected

class TestNever(object):
    @pytest.mark.parametrize("tags, case", [
        ([], "no_tags"),
        (["foo", "bar"], "some tags"),
        (["foo", "other"], "some tags2"),
    ])
    def test_evaluate_returns_false(self, tags, case):
        expression = Never()
        assert expression.evaluate(tags) is False
