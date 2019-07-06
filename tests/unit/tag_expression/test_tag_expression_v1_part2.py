# -*- coding: utf-8 -*-
"""
Alternative approach to test TagExpression by testing all possible combinations.

REQUIRES: Python >= 2.6, because itertools.combinations() is used.
"""

from __future__ import absolute_import
import itertools
from six.moves import range
import pytest
from behave.tag_expression import TagExpression


has_combinations = hasattr(itertools, "combinations")
if has_combinations:
    # -- REQUIRE: itertools.combinations
    # SINCE: Python 2.6

    def all_combinations(items):
        variants = []
        for n in range(len(items)+1):
            variants.extend(itertools.combinations(items, n))
        return variants

    NO_TAGS = "__NO_TAGS__"
    def make_tags_line(tags):
        """
        Convert into tags-line as in feature file.
        """
        if tags:
            return "@" + " @".join(tags)
        return NO_TAGS


    TestCase = object
    # ----------------------------------------------------------------------------
    # TEST: all_combinations() test helper
    # ----------------------------------------------------------------------------
    class TestAllCombinations(TestCase):
        def test_all_combinations_with_2values(self):
            items = "@one @two".split()
            expected = [
                (),
                ('@one',),
                ('@two',),
                ('@one', '@two'),
            ]
            actual = all_combinations(items)
            assert actual == expected
            assert len(actual) == 4

        def test_all_combinations_with_3values(self):
            items = "@one @two @three".split()
            expected = [
                (),
                ('@one',),
                ('@two',),
                ('@three',),
                ('@one', '@two'),
                ('@one', '@three'),
                ('@two', '@three'),
                ('@one', '@two', '@three'),
            ]
            actual = all_combinations(items)
            assert actual == expected
            assert len(actual) == 8


    # ----------------------------------------------------------------------------
    # COMPLICATED TESTS FOR: TagExpression logic
    # ----------------------------------------------------------------------------
    class TagExpressionTestCase(TestCase):

        def assert_tag_expression_matches(self, tag_expression,
                                          tag_combinations, expected):
            matched = [ make_tags_line(c) for c in tag_combinations
                                if tag_expression.check(c) ]
            assert matched == expected

        def assert_tag_expression_mismatches(self, tag_expression,
                                            tag_combinations, expected):
            mismatched = [ make_tags_line(c) for c in tag_combinations
                                if not tag_expression.check(c) ]
            assert mismatched == expected


    class TestTagExpressionWith1Term(TagExpressionTestCase):
        """
        ALL_COMBINATIONS[4] with: @foo @other
            self.NO_TAGS,
            "@foo", "@other",
            "@foo @other",
        """
        tags = ("foo", "other")
        tag_combinations = all_combinations(tags)

        def test_matches__foo(self):
            tag_expression = TagExpression(["@foo"])
            expected = [
                # -- WITH 0 tags: None
                "@foo",
                "@foo @other",
            ]
            self.assert_tag_expression_matches(tag_expression,
                                               self.tag_combinations, expected)

        def test_matches__not_foo(self):
            tag_expression = TagExpression(["-@foo"])
            expected = [
                NO_TAGS,
                "@other",
            ]
            self.assert_tag_expression_matches(tag_expression,
                                               self.tag_combinations, expected)

    class TestTagExpressionWith2Terms(TagExpressionTestCase):
        """
        ALL_COMBINATIONS[8] with: @foo @bar @other
            self.NO_TAGS,
            "@foo", "@bar", "@other",
            "@foo @bar", "@foo @other", "@bar @other",
            "@foo @bar @other",
        """
        tags = ("foo", "bar", "other")
        tag_combinations = all_combinations(tags)

        # -- LOGICAL-OR CASES:
        def test_matches__foo_or_bar(self):
            tag_expression = TagExpression(["@foo,@bar"])
            expected = [
                # -- WITH 0 tags: None
                "@foo", "@bar",
                "@foo @bar", "@foo @other", "@bar @other",
                "@foo @bar @other",
            ]
            self.assert_tag_expression_matches(tag_expression,
                                               self.tag_combinations, expected)

        def test_matches__foo_or_not_bar(self):
            tag_expression = TagExpression(["@foo,-@bar"])
            expected = [
                NO_TAGS,
                "@foo", "@other",
                "@foo @bar", "@foo @other",
                "@foo @bar @other",
            ]
            self.assert_tag_expression_matches(tag_expression,
                                               self.tag_combinations, expected)

        def test_matches__not_foo_or_not_bar(self):
            tag_expression = TagExpression(["-@foo,-@bar"])
            expected = [
                NO_TAGS,
                "@foo", "@bar", "@other",
                "@foo @other", "@bar @other",
            ]
            self.assert_tag_expression_matches(tag_expression,
                                               self.tag_combinations, expected)

        # -- LOGICAL-AND CASES:
        def test_matches__foo_and_bar(self):
            tag_expression = TagExpression(["@foo", "@bar"])
            expected = [
                # -- WITH 0 tags: None
                # -- WITH 1 tag:  None
                "@foo @bar",
                "@foo @bar @other",
            ]
            self.assert_tag_expression_matches(tag_expression,
                                               self.tag_combinations, expected)

        def test_matches__foo_and_not_bar(self):
            tag_expression = TagExpression(["@foo", "-@bar"])
            expected = [
                # -- WITH 0 tags: None
                # -- WITH 1 tag:  None
                "@foo",
                "@foo @other",
                # -- WITH 3 tag:  None
            ]
            self.assert_tag_expression_matches(tag_expression,
                                               self.tag_combinations, expected)

        def test_matches__not_foo_and_not_bar(self):
            tag_expression = TagExpression(["-@foo", "-@bar"])
            expected = [
                NO_TAGS,
                "@other",
                # -- WITH 2 tag:  None
                # -- WITH 3 tag:  None
            ]
            self.assert_tag_expression_matches(tag_expression,
                                               self.tag_combinations, expected)


    class TestTagExpressionWith3Terms(TagExpressionTestCase):
        """
        ALL_COMBINATIONS[16] with: @foo @bar @zap @other
            self.NO_TAGS,
            "@foo", "@bar", "@zap", "@other",
            "@foo @bar", "@foo @zap", "@foo @other",
            "@bar @zap", "@bar @other",
            "@zap @other",
            "@foo @bar @zap", "@foo @bar @other", "@foo @zap @other",
            "@bar @zap @other",
            "@foo @bar @zap @other",
        """
        tags = ("foo", "bar", "zap", "other")
        tag_combinations = all_combinations(tags)

        # -- LOGICAL-OR CASES:
        def test_matches__foo_or_bar_or_zap(self):
            tag_expression = TagExpression(["@foo,@bar,@zap"])
            matched = [
                # -- WITH 0 tags: None
                # -- WITH 1 tag:
                "@foo", "@bar", "@zap",
                # -- WITH 2 tags:
                "@foo @bar", "@foo @zap", "@foo @other",
                "@bar @zap", "@bar @other",
                "@zap @other",
                # -- WITH 3 tags:
                "@foo @bar @zap", "@foo @bar @other", "@foo @zap @other",
                "@bar @zap @other",
                # -- WITH 4 tags:
                "@foo @bar @zap @other",
            ]
            self.assert_tag_expression_matches(tag_expression,
                                               self.tag_combinations, matched)

            mismatched = [
                # -- WITH 0 tags:
                NO_TAGS,
                # -- WITH 1 tag:
                "@other",
                # -- WITH 2 tags: None
                # -- WITH 3 tags: None
                # -- WITH 4 tags: None
            ]
            self.assert_tag_expression_mismatches(tag_expression,
                                               self.tag_combinations, mismatched)

        def test_matches__foo_or_not_bar_or_zap(self):
            tag_expression = TagExpression(["@foo,-@bar,@zap"])
            matched = [
                # -- WITH 0 tags:
                NO_TAGS,
                # -- WITH 1 tag:
                "@foo", "@zap", "@other",
                # -- WITH 2 tags:
                "@foo @bar", "@foo @zap", "@foo @other",
                "@bar @zap",
                "@zap @other",
                # -- WITH 3 tags:
                "@foo @bar @zap", "@foo @bar @other", "@foo @zap @other",
                "@bar @zap @other",
                # -- WITH 4 tags:
                "@foo @bar @zap @other",
            ]
            self.assert_tag_expression_matches(tag_expression,
                                               self.tag_combinations, matched)

            mismatched = [
                # -- WITH 0 tags: None
                # -- WITH 1 tag:
                "@bar",
                # -- WITH 2 tags:
                "@bar @other",
                # -- WITH 3 tags: None
                # -- WITH 4 tags: None
            ]
            self.assert_tag_expression_mismatches(tag_expression,
                                               self.tag_combinations, mismatched)


        def test_matches__foo_or_not_bar_or_not_zap(self):
            tag_expression = TagExpression(["foo,-@bar,-@zap"])
            matched = [
                # -- WITH 0 tags:
                NO_TAGS,
                # -- WITH 1 tag:
                "@foo", "@bar", "@zap", "@other",
                # -- WITH 2 tags:
                "@foo @bar", "@foo @zap", "@foo @other",
                "@bar @other",
                "@zap @other",
                # -- WITH 3 tags:
                "@foo @bar @zap", "@foo @bar @other", "@foo @zap @other",
                # -- WITH 4 tags:
                "@foo @bar @zap @other",
            ]
            self.assert_tag_expression_matches(tag_expression,
                                               self.tag_combinations, matched)

            mismatched = [
                # -- WITH 0 tags: None
                # -- WITH 1 tag: None
                # -- WITH 2 tags:
                "@bar @zap",
                # -- WITH 3 tags: None
                "@bar @zap @other",
                # -- WITH 4 tags: None
            ]
            self.assert_tag_expression_mismatches(tag_expression,
                                               self.tag_combinations, mismatched)

        def test_matches__not_foo_or_not_bar_or_not_zap(self):
            tag_expression = TagExpression(["-@foo,-@bar,-@zap"])
            matched = [
                # -- WITH 0 tags:
                NO_TAGS,
                # -- WITH 1 tag:
                "@foo", "@bar", "@zap", "@other",
                # -- WITH 2 tags:
                "@foo @bar", "@foo @zap", "@foo @other",
                "@bar @zap", "@bar @other",
                "@zap @other",
                # -- WITH 3 tags:
                "@foo @bar @other", "@foo @zap @other",
                "@bar @zap @other",
                # -- WITH 4 tags: None
            ]
            self.assert_tag_expression_matches(tag_expression,
                                               self.tag_combinations, matched)

            mismatched = [
                # -- WITH 0 tags: None
                # -- WITH 1 tag: None
                # -- WITH 2 tags:
                # -- WITH 3 tags:
                "@foo @bar @zap",
                # -- WITH 4 tags:
                "@foo @bar @zap @other",
            ]
            self.assert_tag_expression_mismatches(tag_expression,
                                               self.tag_combinations, mismatched)

        def test_matches__foo_and_bar_or_zap(self):
            tag_expression = TagExpression(["@foo", "@bar,@zap"])
            matched = [
                # -- WITH 0 tags:
                # -- WITH 1 tag:
                # -- WITH 2 tags:
                "@foo @bar", "@foo @zap",
                # -- WITH 3 tags:
                "@foo @bar @zap", "@foo @bar @other", "@foo @zap @other",
                # -- WITH 4 tags: None
                "@foo @bar @zap @other",
            ]
            self.assert_tag_expression_matches(tag_expression,
                                               self.tag_combinations, matched)

            mismatched = [
                # -- WITH 0 tags:
                NO_TAGS,
                # -- WITH 1 tag:
                "@foo", "@bar", "@zap", "@other",
                # -- WITH 2 tags:
                "@foo @other",
                "@bar @zap", "@bar @other",
                "@zap @other",
                # -- WITH 3 tags:
                "@bar @zap @other",
                # -- WITH 4 tags: None
            ]
            self.assert_tag_expression_mismatches(tag_expression,
                                               self.tag_combinations, mismatched)

        def test_matches__foo_and_bar_or_not_zap(self):
            tag_expression = TagExpression(["@foo", "@bar,-@zap"])
            matched = [
                # -- WITH 0 tags:
                # -- WITH 1 tag:
                "@foo",
                # -- WITH 2 tags:
                "@foo @bar", "@foo @other",
                # -- WITH 3 tags:
                "@foo @bar @zap", "@foo @bar @other",
                # -- WITH 4 tags: None
                "@foo @bar @zap @other",
            ]
            self.assert_tag_expression_matches(tag_expression,
                                               self.tag_combinations, matched)

            mismatched = [
                # -- WITH 0 tags:
                NO_TAGS,
                # -- WITH 1 tag:
                "@bar", "@zap", "@other",
                # -- WITH 2 tags:
                "@foo @zap",
                "@bar @zap", "@bar @other",
                "@zap @other",
                # -- WITH 3 tags:
                "@foo @zap @other",
                "@bar @zap @other",
                # -- WITH 4 tags: None
            ]
            self.assert_tag_expression_mismatches(tag_expression,
                                               self.tag_combinations, mismatched)

        def test_matches__foo_and_bar_and_zap(self):
            tag_expression = TagExpression(["@foo", "@bar", "@zap"])
            matched = [
                # -- WITH 0 tags:
                # -- WITH 1 tag:
                # -- WITH 2 tags:
                # -- WITH 3 tags:
                "@foo @bar @zap",
                # -- WITH 4 tags: None
                "@foo @bar @zap @other",
            ]
            self.assert_tag_expression_matches(tag_expression,
                                               self.tag_combinations, matched)

            mismatched = [
                # -- WITH 0 tags:
                NO_TAGS,
                # -- WITH 1 tag:
                "@foo", "@bar", "@zap", "@other",
                # -- WITH 2 tags:
                "@foo @bar", "@foo @zap", "@foo @other",
                "@bar @zap", "@bar @other",
                "@zap @other",
                # -- WITH 3 tags:
                "@foo @bar @other", "@foo @zap @other",
                "@bar @zap @other",
                # -- WITH 4 tags: None
            ]
            self.assert_tag_expression_mismatches(tag_expression,
                                               self.tag_combinations, mismatched)

        def test_matches__not_foo_and_not_bar_and_not_zap(self):
            tag_expression = TagExpression(["-@foo", "-@bar", "-@zap"])
            matched = [
                # -- WITH 0 tags:
                NO_TAGS,
                # -- WITH 1 tag:
                "@other",
                # -- WITH 2 tags:
                # -- WITH 3 tags:
                # -- WITH 4 tags: None
            ]
            self.assert_tag_expression_matches(tag_expression,
                                               self.tag_combinations, matched)

            mismatched = [
                # -- WITH 0 tags:
                # -- WITH 1 tag:
                "@foo", "@bar", "@zap",
                # -- WITH 2 tags:
                "@foo @bar", "@foo @zap", "@foo @other",
                "@bar @zap", "@bar @other",
                "@zap @other",
                # -- WITH 3 tags:
                "@foo @bar @zap",
                "@foo @bar @other", "@foo @zap @other",
                "@bar @zap @other",
                # -- WITH 4 tags: None
                "@foo @bar @zap @other",
            ]
            self.assert_tag_expression_mismatches(tag_expression,
                                               self.tag_combinations, mismatched)
