# -*- coding: utf-8 -*-

from __future__ import absolute_import
from behave.tag_matcher import *
from mock import Mock
from unittest import TestCase
import warnings
# -- REQUIRES: pytest
# import pytest


class Traits4ActiveTagMatcher(object):
    TagMatcher = ActiveTagMatcher
    value_provider = {
        "foo": "alice",
        "bar": "BOB",
    }

    category1_enabled_tag = TagMatcher.make_category_tag("foo", "alice")
    category1_disabled_tag = TagMatcher.make_category_tag("foo", "bob")
    category1_disabled_tag2 = TagMatcher.make_category_tag("foo", "charly")
    category1_similar_tag = TagMatcher.make_category_tag("foo", "alice2")
    category2_enabled_tag = TagMatcher.make_category_tag("bar", "BOB")
    category2_disabled_tag = TagMatcher.make_category_tag("bar", "CHARLY")
    category2_similar_tag = TagMatcher.make_category_tag("bar", "BOB2")
    unknown_category_tag = TagMatcher.make_category_tag("UNKNOWN", "one")

    # -- NEGATED TAGS:
    category1_not_enabled_tag = \
        TagMatcher.make_category_tag("foo", "alice", "not_active")
    category1_not_enabled_tag2 = \
        TagMatcher.make_category_tag("foo", "alice", "not")
    category1_not_disabled_tag = \
        TagMatcher.make_category_tag("foo", "bob", "not_active")
    category1_negated_similar_tag1 = \
        TagMatcher.make_category_tag("foo", "alice2", "not_active")


    active_tags1 = [
        category1_enabled_tag, category1_disabled_tag, category1_similar_tag,
        category1_not_enabled_tag, category1_not_enabled_tag2,
    ]
    active_tags2 = [
        category2_enabled_tag, category2_disabled_tag, category2_similar_tag,
    ]
    active_tags = active_tags1 + active_tags2

# -- REQUIRES: pytest
# class TestActiveTagMatcher2(object):
#     TagMatcher = ActiveTagMatcher
#     traits = Traits4ActiveTagMatcher
#
#     @classmethod
#     def make_tag_matcher(cls):
#         value_provider = {
#             "foo": "alice",
#             "bar": "BOB",
#         }
#         tag_matcher = cls.TagMatcher(value_provider)
#         return tag_matcher
#
#     @pytest.mark.parametrize("case, expected_len, tags", [
#         ("case: Two enabled tags", 2,
#          [traits.category1_enabled_tag, traits.category2_enabled_tag]),
#         ("case: Active enabled and normal tag", 1,
#          [traits.category1_enabled_tag,  "foo"]),
#         ("case: Active disabled and normal tag", 1,
#          [traits.category1_disabled_tag, "foo"]),
#         ("case: Normal and active negated tag", 1,
#          ["foo", traits.category1_not_enabled_tag]),
#         ("case: Two normal tags", 0,
#          ["foo", "bar"]),
#     ])
#     def test_select_active_tags__with_two_tags(self, case, expected_len, tags):
#         tag_matcher = self.make_tag_matcher()
#         selected = tag_matcher.select_active_tags(tags)
#         selected = list(selected)
#         assert len(selected) == expected_len, case
#
#     @pytest.mark.parametrize("case, expected, tags", [
#         # -- GROUP: With positive logic (non-negated tags)
#         ("case P00: 2 disabled tags", True,
#          [ traits.category1_disabled_tag, traits.category2_disabled_tag]),
#         ("case P01: disabled and enabled tag", True,
#          [ traits.category1_disabled_tag, traits.category2_enabled_tag]),
#         ("case P10: enabled and disabled tag", True,
#          [ traits.category1_enabled_tag, traits.category2_disabled_tag]),
#         ("case P11: 2 enabled tags", False,  # -- SHOULD-RUN
#          [ traits.category1_enabled_tag, traits.category2_enabled_tag]),
#         # -- GROUP: With negated tag
#         ("case N00: not-enabled and disabled tag", True,
#          [ traits.category1_not_enabled_tag, traits.category2_disabled_tag]),
#         ("case N01: not-enabled and enabled tag", True,
#          [ traits.category1_not_enabled_tag, traits.category2_enabled_tag]),
#         ("case N10: not-disabled and disabled tag", True,
#          [ traits.category1_not_disabled_tag, traits.category2_disabled_tag]),
#         ("case N11: not-disabled and enabled tag", False, # -- SHOULD-RUN
#          [ traits.category1_not_disabled_tag, traits.category2_enabled_tag]),
#         # -- GROUP: With unknown category
#         ("case U0x: disabled and unknown tag", True,
#          [ traits.category1_disabled_tag, traits.unknown_category_tag]),
#         ("case U1x: enabled and unknown tag", False,  # -- SHOULD-RUN
#          [ traits.category1_enabled_tag, traits.unknown_category_tag]),
#     ])
#     def test_should_exclude_with__combinations_of_2_categories(self, case, expected, tags):
#         tag_matcher = self.make_tag_matcher()
#         actual_result = tag_matcher.should_exclude_with(tags)
#         assert expected == actual_result, case
#
#     @pytest.mark.parametrize("case, expected, tags", [
#         # -- GROUP: With positive logic (non-negated tags)
#         ("case P00: 2 disabled tags", True,
#          [ traits.category1_disabled_tag, traits.category1_disabled_tag2]),
#         ("case P01: disabled and enabled tag", True,
#          [ traits.category1_disabled_tag, traits.category1_enabled_tag]),
#         ("case P10: enabled and disabled tag", True,
#          [ traits.category1_enabled_tag, traits.category1_disabled_tag]),
#         ("case P11: 2 enabled tags (same)", False,  # -- SHOULD-RUN
#          [ traits.category1_enabled_tag, traits.category1_enabled_tag]),
#         # -- GROUP: With negated tag
#         ("case N00: not-enabled and disabled tag", True,
#          [ traits.category1_not_enabled_tag, traits.category1_disabled_tag]),
#         ("case N01: not-enabled and enabled tag", True,
#          [ traits.category1_not_enabled_tag, traits.category1_enabled_tag]),
#         ("case N10: not-disabled and disabled tag", True,
#          [ traits.category1_not_disabled_tag, traits.category1_disabled_tag]),
#         ("case N11: not-disabled and enabled tag", False, # -- SHOULD-RUN
#          [ traits.category1_not_disabled_tag, traits.category1_enabled_tag]),
#     ])
#     def test_should_exclude_with__combinations_with_same_category(self,
#                                                         case, expected, tags):
#         tag_matcher = self.make_tag_matcher()
#         actual_result = tag_matcher.should_exclude_with(tags)
#         assert expected == actual_result, case


class TestActiveTagMatcher1(TestCase):
    TagMatcher = ActiveTagMatcher
    traits = Traits4ActiveTagMatcher

    @classmethod
    def make_tag_matcher(cls):
        tag_matcher = cls.TagMatcher(cls.traits.value_provider)
        return tag_matcher

    def setUp(self):
        self.tag_matcher = self.make_tag_matcher()

    def test_select_active_tags__basics(self):
        active_tag = "active.with_CATEGORY=VALUE"
        tags = ["foo", active_tag, "bar"]
        selected = list(self.tag_matcher.select_active_tags(tags))
        self.assertEqual(len(selected), 1)
        selected_tag, selected_match = selected[0]
        self.assertEqual(selected_tag, active_tag)

    def test_select_active_tags__matches_tag_parts(self):
        tags = ["active.with_CATEGORY=VALUE"]
        selected = list(self.tag_matcher.select_active_tags(tags))
        self.assertEqual(len(selected), 1)
        selected_tag, selected_match = selected[0]
        self.assertEqual(selected_match.group("prefix"), "active")
        self.assertEqual(selected_match.group("category"), "CATEGORY")
        self.assertEqual(selected_match.group("value"), "VALUE")

    def test_select_active_tags__finds_tag_with_any_valid_tag_prefix(self):
        TagMatcher = self.TagMatcher
        for tag_prefix in TagMatcher.tag_prefixes:
            tag = TagMatcher.make_category_tag("foo", "alice", tag_prefix)
            tags = [ tag ]
            selected = self.tag_matcher.select_active_tags(tags)
            selected = list(selected)
            self.assertEqual(len(selected), 1)
            selected_tag0 = selected[0][0]
            self.assertEqual(selected_tag0, tag)
            self.assertTrue(selected_tag0.startswith(tag_prefix))

    def test_select_active_tags__ignores_invalid_active_tags(self):
        invalid_active_tags = [
            ("foo.alice",               "case: Normal tag"),
            ("with_foo=alice",          "case: Subset of an active tag"),
            ("ACTIVE.with_foo.alice",   "case: Wrong tag_prefix (uppercase)"),
            ("only.with_foo.alice",     "case: Wrong value_separator"),
        ]
        for invalid_tag, case in invalid_active_tags:
            tags = [ invalid_tag ]
            selected = self.tag_matcher.select_active_tags(tags)
            selected = list(selected)
            self.assertEqual(len(selected), 0, case)

    def test_select_active_tags__with_two_tags(self):
        # XXX-JE-DUPLICATED:
        traits = self.traits
        test_patterns = [
            ("case: Two enabled tags",
             [traits.category1_enabled_tag, traits.category2_enabled_tag]),
            ("case: Active enabled and normal tag",
             [traits.category1_enabled_tag,  "foo"]),
            ("case: Active disabled and normal tag",
             [traits.category1_disabled_tag, "foo"]),
            ("case: Active negated and normal tag",
             [traits.category1_not_enabled_tag, "foo"]),
        ]
        for case, tags in test_patterns:
            selected = self.tag_matcher.select_active_tags(tags)
            selected = list(selected)
            self.assertTrue(len(selected) >= 1, case)


    def test_should_exclude_with__returns_false_with_enabled_tag(self):
        traits = self.traits
        tags1 = [ traits.category1_enabled_tag ]
        tags2 = [ traits.category2_enabled_tag ]
        self.assertEqual(False, self.tag_matcher.should_exclude_with(tags1))
        self.assertEqual(False, self.tag_matcher.should_exclude_with(tags2))

    def test_should_exclude_with__returns_false_with_disabled_tag_and_more(self):
        # -- NOTE: Need 1+ enabled active-tags of same category => ENABLED
        traits = self.traits
        test_patterns = [
            ([ traits.category1_enabled_tag, traits.category1_disabled_tag ], "case: first"),
            ([ traits.category1_disabled_tag, traits.category1_enabled_tag ], "case: last"),
            ([ "foo", traits.category1_enabled_tag, traits.category1_disabled_tag, "bar" ], "case: middle"),
        ]
        enabled = True  # EXPECTED
        for tags, case in test_patterns:
            self.assertEqual(not enabled, self.tag_matcher.should_exclude_with(tags),
                             "%s: tags=%s" % (case, tags))

    def test_should_exclude_with__returns_true_with_other_tag(self):
        traits = self.traits
        tags = [ traits.category1_disabled_tag ]
        self.assertEqual(True, self.tag_matcher.should_exclude_with(tags))

    def test_should_exclude_with__returns_true_with_other_tag_and_more(self):
        traits = self.traits
        test_patterns = [
            ([ traits.category1_disabled_tag, "foo" ], "case: first"),
            ([ "foo", traits.category1_disabled_tag ], "case: last"),
            ([ "foo", traits.category1_disabled_tag, "bar" ], "case: middle"),
        ]
        for tags, case in test_patterns:
            self.assertEqual(True, self.tag_matcher.should_exclude_with(tags),
                             "%s: tags=%s" % (case, tags))

    def test_should_exclude_with__returns_true_with_similar_tag(self):
        traits = self.traits
        tags = [ traits.category1_similar_tag ]
        self.assertEqual(True, self.tag_matcher.should_exclude_with(tags))

    def test_should_exclude_with__returns_true_with_similar_and_more(self):
        traits = self.traits
        test_patterns = [
            ([ traits.category1_similar_tag, "foo" ], "case: first"),
            ([ "foo", traits.category1_similar_tag ], "case: last"),
            ([ "foo", traits.category1_similar_tag, "bar" ], "case: middle"),
        ]
        for tags, case in test_patterns:
            self.assertEqual(True, self.tag_matcher.should_exclude_with(tags),
                             "%s: tags=%s" % (case, tags))

    def test_should_exclude_with__returns_false_without_category_tag(self):
        test_patterns = [
            ([ ],           "case: No tags"),
            ([ "foo" ],     "case: One tag"),
            ([ "foo", "bar" ], "case: Two tags"),
        ]
        for tags, case in test_patterns:
            self.assertEqual(False, self.tag_matcher.should_exclude_with(tags),
                             "%s: tags=%s" % (case, tags))

    def test_should_exclude_with__returns_false_with_unknown_category_tag(self):
        """Tags from unknown categories, not supported by value_provider,
        should not be excluded.
        """
        traits = self.traits
        tags = [ traits.unknown_category_tag ]
        self.assertEqual("active.with_UNKNOWN=one", traits.unknown_category_tag)
        self.assertEqual(None, self.tag_matcher.value_provider.get("UNKNOWN"))
        self.assertEqual(False, self.tag_matcher.should_exclude_with(tags))

    def test_should_exclude_with__combinations_of_2_categories(self):
        # XXX-JE-DUPLICATED:
        traits = self.traits
        test_patterns = [
            ("case P00: 2 disabled category tags", True,
             [ traits.category1_disabled_tag, traits.category2_disabled_tag]),
            ("case P01: disabled and enabled category tags", True,
             [ traits.category1_disabled_tag, traits.category2_enabled_tag]),
            ("case P10: enabled and disabled category tags", True,
             [ traits.category1_enabled_tag, traits.category2_disabled_tag]),
            ("case P11: 2 enabled category tags", False,  # -- SHOULD-RUN
             [ traits.category1_enabled_tag, traits.category2_enabled_tag]),
            # -- SPECIAL CASE: With negated category
            ("case N00: not-enabled and disabled category tags", True,
             [ traits.category1_not_enabled_tag, traits.category2_disabled_tag]),
            ("case N01: not-enabled and enabled category tags", True,
             [ traits.category1_not_enabled_tag, traits.category2_enabled_tag]),
            ("case N10: not-disabled and disabled category tags", True,
             [ traits.category1_not_disabled_tag, traits.category2_disabled_tag]),
            ("case N11: not-enabled and enabled category tags", False,  # -- SHOULD-RUN
             [ traits.category1_not_disabled_tag, traits.category2_enabled_tag]),
            # -- SPECIAL CASE: With unknown category
            ("case 0x: disabled and unknown category tags", True,
             [ traits.category1_disabled_tag, traits.unknown_category_tag]),
            ("case 1x: enabled and unknown category tags", False,  # SHOULD-RUN
             [ traits.category1_enabled_tag, traits.unknown_category_tag]),
        ]
        for case, expected, tags in test_patterns:
            actual_result = self.tag_matcher.should_exclude_with(tags)
            self.assertEqual(expected, actual_result,
                             "%s: tags=%s" % (case, tags))

    def test_should_run_with__negates_result_of_should_exclude_with(self):
        traits = self.traits
        test_patterns = [
            ([ ],                   "case: No tags"),
            ([ "foo" ],             "case: One non-category tag"),
            ([ "foo", "bar" ],      "case: Two non-category tags"),
            ([ traits.category1_enabled_tag ],   "case: enabled tag"),
            ([ traits.category1_enabled_tag, traits.category1_disabled_tag ],  "case: enabled and other tag"),
            ([ traits.category1_enabled_tag, "foo" ],    "case: enabled and foo tag"),
            ([ traits.category1_disabled_tag ],            "case: other tag"),
            ([ traits.category1_disabled_tag, "foo" ],     "case: other and foo tag"),
            ([ traits.category1_similar_tag ],          "case: similar tag"),
            ([ "foo", traits.category1_similar_tag ],   "case: foo and similar tag"),
        ]
        for tags, case in test_patterns:
            result1 = self.tag_matcher.should_run_with(tags)
            result2 = self.tag_matcher.should_exclude_with(tags)
            self.assertEqual(result1, not result2, "%s: tags=%s" % (case, tags))
            self.assertEqual(not result1, result2, "%s: tags=%s" % (case, tags))

class TestPredicateTagMatcher(TestCase):

    def test_exclude_with__mechanics(self):
        predicate_function_blueprint = lambda tags: False
        predicate_function = Mock(predicate_function_blueprint)
        predicate_function.return_value = True
        tag_matcher = PredicateTagMatcher(predicate_function)
        tags = [ "foo", "bar" ]
        self.assertEqual(True, tag_matcher.should_exclude_with(tags))
        predicate_function.assert_called_once_with(tags)
        self.assertEqual(True, predicate_function(tags))

    def test_should_exclude_with__returns_true_when_predicate_is_true(self):
        predicate_always_true = lambda tags: True
        tag_matcher1 = PredicateTagMatcher(predicate_always_true)
        tags = [ "foo", "bar" ]
        self.assertEqual(True, tag_matcher1.should_exclude_with(tags))
        self.assertEqual(True, predicate_always_true(tags))

    def test_should_exclude_with__returns_true_when_predicate_is_true2(self):
        # -- CASE: Use predicate function instead of lambda.
        def predicate_contains_foo(tags):
            return any(x == "foo" for x in tags)
        tag_matcher2 = PredicateTagMatcher(predicate_contains_foo)
        tags = [ "foo", "bar" ]
        self.assertEqual(True, tag_matcher2.should_exclude_with(tags))
        self.assertEqual(True, predicate_contains_foo(tags))

    def test_should_exclude_with__returns_false_when_predicate_is_false(self):
        predicate_always_false = lambda tags: False
        tag_matcher1 = PredicateTagMatcher(predicate_always_false)
        tags = [ "foo", "bar" ]
        self.assertEqual(False, tag_matcher1.should_exclude_with(tags))
        self.assertEqual(False, predicate_always_false(tags))

class TestPredicateTagMatcher(TestCase):

    def test_exclude_with__mechanics(self):
        predicate_function_blueprint = lambda tags: False
        predicate_function = Mock(predicate_function_blueprint)
        predicate_function.return_value = True
        tag_matcher = PredicateTagMatcher(predicate_function)
        tags = [ "foo", "bar" ]
        self.assertEqual(True, tag_matcher.should_exclude_with(tags))
        predicate_function.assert_called_once_with(tags)
        self.assertEqual(True, predicate_function(tags))

    def test_should_exclude_with__returns_true_when_predicate_is_true(self):
        predicate_always_true = lambda tags: True
        tag_matcher1 = PredicateTagMatcher(predicate_always_true)
        tags = [ "foo", "bar" ]
        self.assertEqual(True, tag_matcher1.should_exclude_with(tags))
        self.assertEqual(True, predicate_always_true(tags))

    def test_should_exclude_with__returns_true_when_predicate_is_true2(self):
        # -- CASE: Use predicate function instead of lambda.
        def predicate_contains_foo(tags):
            return any(x == "foo" for x in tags)
        tag_matcher2 = PredicateTagMatcher(predicate_contains_foo)
        tags = [ "foo", "bar" ]
        self.assertEqual(True, tag_matcher2.should_exclude_with(tags))
        self.assertEqual(True, predicate_contains_foo(tags))

    def test_should_exclude_with__returns_false_when_predicate_is_false(self):
        predicate_always_false = lambda tags: False
        tag_matcher1 = PredicateTagMatcher(predicate_always_false)
        tags = [ "foo", "bar" ]
        self.assertEqual(False, tag_matcher1.should_exclude_with(tags))
        self.assertEqual(False, predicate_always_false(tags))


class TestCompositeTagMatcher(TestCase):

    @staticmethod
    def count_tag_matcher_with_result(tag_matchers, tags, result_value):
        count = 0
        for tag_matcher in tag_matchers:
            current_result = tag_matcher.should_exclude_with(tags)
            if current_result == result_value:
                count += 1
        return count

    def setUp(self):
        predicate_false = lambda tags: False
        predicate_contains_foo = lambda tags: any(x == "foo" for x in tags)
        self.tag_matcher_false = PredicateTagMatcher(predicate_false)
        self.tag_matcher_foo = PredicateTagMatcher(predicate_contains_foo)
        tag_matchers = [
            self.tag_matcher_foo,
            self.tag_matcher_false
        ]
        self.ctag_matcher = CompositeTagMatcher(tag_matchers)

    def test_should_exclude_with__returns_true_when_any_tag_matcher_returns_true(self):
        test_patterns = [
            ("case: with foo",  ["foo", "bar"]),
            ("case: with foo2", ["foozy", "foo", "bar"]),
        ]
        for case, tags in test_patterns:
            actual_result = self.ctag_matcher.should_exclude_with(tags)
            self.assertEqual(True, actual_result,
                             "%s: tags=%s" % (case, tags))

            actual_true_count = self.count_tag_matcher_with_result(
                                self.ctag_matcher.tag_matchers, tags, True)
            self.assertEqual(1, actual_true_count)

    def test_should_exclude_with__returns_false_when_no_tag_matcher_return_true(self):
        test_patterns = [
            ("case: without foo",   ["fool", "bar"]),
            ("case: without foo2",  ["foozy", "bar"]),
        ]
        for case, tags in test_patterns:
            actual_result = self.ctag_matcher.should_exclude_with(tags)
            self.assertEqual(False, actual_result,
                             "%s: tags=%s" % (case, tags))

            actual_true_count = self.count_tag_matcher_with_result(
                                    self.ctag_matcher.tag_matchers, tags, True)
            self.assertEqual(0, actual_true_count)


# -----------------------------------------------------------------------------
# PROTOTYPING CLASSES (deprecating)
# -----------------------------------------------------------------------------
class TestOnlyWithCategoryTagMatcher(TestCase):
    TagMatcher = OnlyWithCategoryTagMatcher

    def setUp(self):
        category = "xxx"
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            self.tag_matcher = OnlyWithCategoryTagMatcher(category, "alice")
        self.enabled_tag = self.TagMatcher.make_category_tag(category, "alice")
        self.similar_tag = self.TagMatcher.make_category_tag(category, "alice2")
        self.other_tag = self.TagMatcher.make_category_tag(category, "other")
        self.category = category

    def test_should_exclude_with__returns_false_with_enabled_tag(self):
        tags = [ self.enabled_tag ]
        self.assertEqual(False, self.tag_matcher.should_exclude_with(tags))

    def test_should_exclude_with__returns_false_with_enabled_tag_and_more(self):
        test_patterns = [
            ([ self.enabled_tag, self.other_tag ], "case: first"),
            ([ self.other_tag, self.enabled_tag ], "case: last"),
            ([ "foo", self.enabled_tag, self.other_tag, "bar" ], "case: middle"),
        ]
        for tags, case in test_patterns:
            self.assertEqual(False, self.tag_matcher.should_exclude_with(tags),
                             "%s: tags=%s" % (case, tags))

    def test_should_exclude_with__returns_true_with_other_tag(self):
        tags = [ self.other_tag ]
        self.assertEqual(True, self.tag_matcher.should_exclude_with(tags))

    def test_should_exclude_with__returns_true_with_other_tag_and_more(self):
        test_patterns = [
            ([ self.other_tag, "foo" ], "case: first"),
            ([ "foo", self.other_tag ], "case: last"),
            ([ "foo", self.other_tag, "bar" ], "case: middle"),
        ]
        for tags, case in test_patterns:
            self.assertEqual(True, self.tag_matcher.should_exclude_with(tags),
                             "%s: tags=%s" % (case, tags))

    def test_should_exclude_with__returns_true_with_similar_tag(self):
        tags = [ self.similar_tag ]
        self.assertEqual(True, self.tag_matcher.should_exclude_with(tags))

    def test_should_exclude_with__returns_true_with_similar_and_more(self):
        test_patterns = [
            ([ self.similar_tag, "foo" ], "case: first"),
            ([ "foo", self.similar_tag ], "case: last"),
            ([ "foo", self.similar_tag, "bar" ], "case: middle"),
        ]
        for tags, case in test_patterns:
            self.assertEqual(True, self.tag_matcher.should_exclude_with(tags),
                             "%s: tags=%s" % (case, tags))

    def test_should_exclude_with__returns_false_without_category_tag(self):
        test_patterns = [
            ([ ],           "case: No tags"),
            ([ "foo" ],     "case: One tag"),
            ([ "foo", "bar" ], "case: Two tags"),
        ]
        for tags, case in test_patterns:
            self.assertEqual(False, self.tag_matcher.should_exclude_with(tags),
                             "%s: tags=%s" % (case, tags))

    def test_should_run_with__negates_result_of_should_exclude_with(self):
        test_patterns = [
            ([ ],                   "case: No tags"),
            ([ "foo" ],             "case: One non-category tag"),
            ([ "foo", "bar" ],      "case: Two non-category tags"),
            ([ self.enabled_tag ],   "case: enabled tag"),
            ([ self.enabled_tag, self.other_tag ],  "case: enabled and other tag"),
            ([ self.enabled_tag, "foo" ],    "case: enabled and foo tag"),
            ([ self.other_tag ],            "case: other tag"),
            ([ self.other_tag, "foo" ],     "case: other and foo tag"),
            ([ self.similar_tag ],          "case: similar tag"),
            ([ "foo", self.similar_tag ],   "case: foo and similar tag"),
        ]
        for tags, case in test_patterns:
            result1 = self.tag_matcher.should_run_with(tags)
            result2 = self.tag_matcher.should_exclude_with(tags)
            self.assertEqual(result1, not result2, "%s: tags=%s" % (case, tags))
            self.assertEqual(not result1, result2, "%s: tags=%s" % (case, tags))

    def test_make_category_tag__returns_category_tag_prefix_without_value(self):
        category = "xxx"
        tag1 = OnlyWithCategoryTagMatcher.make_category_tag(category)
        tag2 = OnlyWithCategoryTagMatcher.make_category_tag(category, None)
        tag3 = OnlyWithCategoryTagMatcher.make_category_tag(category, value=None)
        self.assertEqual("only.with_xxx=", tag1)
        self.assertEqual("only.with_xxx=", tag2)
        self.assertEqual("only.with_xxx=", tag3)
        self.assertTrue(tag1.startswith(OnlyWithCategoryTagMatcher.tag_prefix))

    def test_make_category_tag__returns_category_tag_with_value(self):
        category = "xxx"
        tag1 = OnlyWithCategoryTagMatcher.make_category_tag(category, "alice")
        tag2 = OnlyWithCategoryTagMatcher.make_category_tag(category, "bob")
        self.assertEqual("only.with_xxx=alice", tag1)
        self.assertEqual("only.with_xxx=bob", tag2)

    def test_make_category_tag__returns_category_tag_with_tag_prefix(self):
        my_tag_prefix = "ONLY_WITH."
        category = "xxx"
        TagMatcher = OnlyWithCategoryTagMatcher
        tag0 = TagMatcher.make_category_tag(category, tag_prefix=my_tag_prefix)
        tag1 = TagMatcher.make_category_tag(category, "alice", my_tag_prefix)
        tag2 = TagMatcher.make_category_tag(category, "bob", tag_prefix=my_tag_prefix)
        self.assertEqual("ONLY_WITH.xxx=", tag0)
        self.assertEqual("ONLY_WITH.xxx=alice", tag1)
        self.assertEqual("ONLY_WITH.xxx=bob", tag2)
        self.assertTrue(tag1.startswith(my_tag_prefix))

    def test_ctor__with_tag_prefix(self):
        tag_prefix = "ONLY_WITH."
        tag_matcher = OnlyWithCategoryTagMatcher("xxx", "alice", tag_prefix)

        tags = ["foo", "ONLY_WITH.xxx=foo", "only.with_xxx=bar", "bar"]
        actual_tags = tag_matcher.select_category_tags(tags)
        self.assertEqual(["ONLY_WITH.xxx=foo"], actual_tags)


class Traits4OnlyWithAnyCategoryTagMatcher(object):
    """Test data for OnlyWithAnyCategoryTagMatcher."""

    TagMatcher0 = OnlyWithCategoryTagMatcher
    TagMatcher = OnlyWithAnyCategoryTagMatcher
    category1_enabled_tag = TagMatcher0.make_category_tag("foo", "alice")
    category1_similar_tag = TagMatcher0.make_category_tag("foo", "alice2")
    category1_disabled_tag = TagMatcher0.make_category_tag("foo", "bob")
    category2_enabled_tag = TagMatcher0.make_category_tag("bar", "BOB")
    category2_similar_tag = TagMatcher0.make_category_tag("bar", "BOB2")
    category2_disabled_tag = TagMatcher0.make_category_tag("bar", "CHARLY")
    unknown_category_tag = TagMatcher0.make_category_tag("UNKNOWN", "one")


class TestOnlyWithAnyCategoryTagMatcher(TestCase):
    TagMatcher = OnlyWithAnyCategoryTagMatcher
    traits = Traits4OnlyWithAnyCategoryTagMatcher

    def setUp(self):
        value_provider = {
            "foo": "alice",
            "bar": "BOB",
        }
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            self.tag_matcher = self.TagMatcher(value_provider)

    # def test_deprecating_warning_is_issued(self):
    #     value_provider = {"foo": "alice"}
    #     with warnings.catch_warnings(record=True) as recorder:
    #         warnings.simplefilter("always", DeprecationWarning)
    #         tag_matcher = OnlyWithAnyCategoryTagMatcher(value_provider)
    #         self.assertEqual(len(recorder), 1)
    #         last_warning = recorder[-1]
    #         assert issubclass(last_warning.category, DeprecationWarning)
    #         assert "deprecated" in str(last_warning.message)

    def test_should_exclude_with__returns_false_with_enabled_tag(self):
        traits = self.traits
        tags1 = [ traits.category1_enabled_tag ]
        tags2 = [ traits.category2_enabled_tag ]
        self.assertEqual(False, self.tag_matcher.should_exclude_with(tags1))
        self.assertEqual(False, self.tag_matcher.should_exclude_with(tags2))

    def test_should_exclude_with__returns_false_with_enabled_tag_and_more(self):
        traits = self.traits
        test_patterns = [
            ([ traits.category1_enabled_tag, traits.category1_disabled_tag ], "case: first"),
            ([ traits.category1_disabled_tag, traits.category1_enabled_tag ], "case: last"),
            ([ "foo", traits.category1_enabled_tag, traits.category1_disabled_tag, "bar" ], "case: middle"),
        ]
        for tags, case in test_patterns:
            self.assertEqual(False, self.tag_matcher.should_exclude_with(tags),
                             "%s: tags=%s" % (case, tags))

    def test_should_exclude_with__returns_true_with_other_tag(self):
        traits = self.traits
        tags = [ traits.category1_disabled_tag ]
        self.assertEqual(True, self.tag_matcher.should_exclude_with(tags))

    def test_should_exclude_with__returns_true_with_other_tag_and_more(self):
        traits = self.traits
        test_patterns = [
            ([ traits.category1_disabled_tag, "foo" ], "case: first"),
            ([ "foo", traits.category1_disabled_tag ], "case: last"),
            ([ "foo", traits.category1_disabled_tag, "bar" ], "case: middle"),
        ]
        for tags, case in test_patterns:
            self.assertEqual(True, self.tag_matcher.should_exclude_with(tags),
                             "%s: tags=%s" % (case, tags))

    def test_should_exclude_with__returns_true_with_similar_tag(self):
        traits = self.traits
        tags = [ traits.category1_similar_tag ]
        self.assertEqual(True, self.tag_matcher.should_exclude_with(tags))

    def test_should_exclude_with__returns_true_with_similar_and_more(self):
        traits = self.traits
        test_patterns = [
            ([ traits.category1_similar_tag, "foo" ], "case: first"),
            ([ "foo", traits.category1_similar_tag ], "case: last"),
            ([ "foo", traits.category1_similar_tag, "bar" ], "case: middle"),
        ]
        for tags, case in test_patterns:
            self.assertEqual(True, self.tag_matcher.should_exclude_with(tags),
                             "%s: tags=%s" % (case, tags))

    def test_should_exclude_with__returns_false_without_category_tag(self):
        test_patterns = [
            ([ ],           "case: No tags"),
            ([ "foo" ],     "case: One tag"),
            ([ "foo", "bar" ], "case: Two tags"),
        ]
        for tags, case in test_patterns:
            self.assertEqual(False, self.tag_matcher.should_exclude_with(tags),
                             "%s: tags=%s" % (case, tags))

    def test_should_exclude_with__returns_false_with_unknown_category_tag(self):
        """Tags from unknown categories, not supported by value_provider,
        should not be excluded.
        """
        traits = self.traits
        tags = [ traits.unknown_category_tag ]
        self.assertEqual("only.with_UNKNOWN=one", traits.unknown_category_tag)
        self.assertEqual(None, self.tag_matcher.value_provider.get("UNKNOWN"))
        self.assertEqual(False, self.tag_matcher.should_exclude_with(tags))

    def test_should_exclude_with__combinations_of_2_categories(self):
        traits = self.traits
        test_patterns = [
            ("case 00: 2 disabled category tags", True,
             [ traits.category1_disabled_tag, traits.category2_disabled_tag]),
            ("case 01: disabled and enabled category tags", True,
             [ traits.category1_disabled_tag, traits.category2_enabled_tag]),
            ("case 10: enabled and disabled category tags", True,
             [ traits.category1_enabled_tag, traits.category2_disabled_tag]),
            ("case 11: 2 enabled category tags", False,  # -- SHOULD-RUN
             [ traits.category1_enabled_tag, traits.category2_enabled_tag]),
            # -- SPECIAL CASE: With unknown category
            ("case 0x: disabled and unknown category tags", True,
             [ traits.category1_disabled_tag, traits.unknown_category_tag]),
            ("case 1x: enabled and unknown category tags", False,  # SHOULD-RUN
             [ traits.category1_enabled_tag, traits.unknown_category_tag]),
        ]
        for case, expected, tags in test_patterns:
            actual_result = self.tag_matcher.should_exclude_with(tags)
            self.assertEqual(expected, actual_result,
                             "%s: tags=%s" % (case, tags))

    def test_should_run_with__negates_result_of_should_exclude_with(self):
        traits = self.traits
        test_patterns = [
            ([ ],                   "case: No tags"),
            ([ "foo" ],             "case: One non-category tag"),
            ([ "foo", "bar" ],      "case: Two non-category tags"),
            ([ traits.category1_enabled_tag ],   "case: enabled tag"),
            ([ traits.category1_enabled_tag, traits.category1_disabled_tag ],  "case: enabled and other tag"),
            ([ traits.category1_enabled_tag, "foo" ],    "case: enabled and foo tag"),
            ([ traits.category1_disabled_tag ],            "case: other tag"),
            ([ traits.category1_disabled_tag, "foo" ],     "case: other and foo tag"),
            ([ traits.category1_similar_tag ],          "case: similar tag"),
            ([ "foo", traits.category1_similar_tag ],   "case: foo and similar tag"),
        ]
        for tags, case in test_patterns:
            result1 = self.tag_matcher.should_run_with(tags)
            result2 = self.tag_matcher.should_exclude_with(tags)
            self.assertEqual(result1, not result2, "%s: tags=%s" % (case, tags))
            self.assertEqual(not result1, result2, "%s: tags=%s" % (case, tags))

