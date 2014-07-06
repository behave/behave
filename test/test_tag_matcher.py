# -*- coding: utf-8 -*-

from behave.tag_matcher import *
from mock import Mock
from unittest import TestCase


class TestOnlyWithCategoryTagMatcher(TestCase):
    TagMatcher = OnlyWithCategoryTagMatcher

    def setUp(self):
        category = "xxx"
        self.tag_matcher = OnlyWithCategoryTagMatcher(category, "alice")
        self.active_tag = self.TagMatcher.make_category_tag(category, "alice")
        self.similar_tag = self.TagMatcher.make_category_tag(category, "alice2")
        self.other_tag = self.TagMatcher.make_category_tag(category, "other")
        self.category = category

    def test_should_exclude_with__returns_false_with_active_tag(self):
        tags = [ self.active_tag ]
        self.assertEqual(False, self.tag_matcher.should_exclude_with(tags))

    def test_should_exclude_with__returns_false_with_active_tag_and_more(self):
        test_patterns = [
            ([ self.active_tag, self.other_tag ], "CASE: first"),
            ([ self.other_tag, self.active_tag ], "CASE: last"),
            ([ "foo", self.active_tag, self.other_tag, "bar" ], "CASE: middle"),
        ]
        for tags, case in test_patterns:
            self.assertEqual(False, self.tag_matcher.should_exclude_with(tags),
                             "%s: tags=%s" % (case, tags))

    def test_should_exclude_with__returns_true_with_other_tag(self):
        tags = [ self.other_tag ]
        self.assertEqual(True, self.tag_matcher.should_exclude_with(tags))

    def test_should_exclude_with__returns_true_with_other_tag_and_more(self):
        test_patterns = [
            ([ self.other_tag, "foo" ], "CASE: first"),
            ([ "foo", self.other_tag ], "CASE: last"),
            ([ "foo", self.other_tag, "bar" ], "CASE: middle"),
        ]
        for tags, case in test_patterns:
            self.assertEqual(True, self.tag_matcher.should_exclude_with(tags),
                             "%s: tags=%s" % (case, tags))

    def test_should_exclude_with__returns_true_with_similar_tag(self):
        tags = [ self.similar_tag ]
        self.assertEqual(True, self.tag_matcher.should_exclude_with(tags))

    def test_should_exclude_with__returns_true_with_similar_and_more(self):
        test_patterns = [
            ([ self.similar_tag, "foo" ], "CASE: first"),
            ([ "foo", self.similar_tag ], "CASE: last"),
            ([ "foo", self.similar_tag, "bar" ], "CASE: middle"),
        ]
        for tags, case in test_patterns:
            self.assertEqual(True, self.tag_matcher.should_exclude_with(tags),
                             "%s: tags=%s" % (case, tags))

    def test_should_exclude_with__returns_false_without_category_tag(self):
        test_patterns = [
            ([ ],           "CASE: No tags"),
            ([ "foo" ],     "CASE: One tag"),
            ([ "foo", "bar" ], "CASE: Two tags"),
        ]
        for tags, case in test_patterns:
            self.assertEqual(False, self.tag_matcher.should_exclude_with(tags),
                             "%s: tags=%s" % (case, tags))

    def test_should_run_with__negates_result_of_should_exclude_with(self):
        test_patterns = [
            ([ ],                   "CASE: No tags"),
            ([ "foo" ],             "CASE: One non-category tag"),
            ([ "foo", "bar" ],      "CASE: Two non-category tags"),
            ([ self.active_tag ],   "CASE: active tag"),
            ([ self.active_tag, self.other_tag ],  "CASE: active and other tag"),
            ([ self.active_tag, "foo" ],    "CASE: active and foo tag"),
            ([ self.other_tag ],            "CASE: other tag"),
            ([ self.other_tag, "foo" ],     "CASE: other and foo tag"),
            ([ self.similar_tag ],          "CASE: similar tag"),
            ([ "foo", self.similar_tag ],   "CASE: foo and similar tag"),
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


class TestOnlyWithAnyCategoryTagMatcher(TestCase):
    TagMatcher = OnlyWithAnyCategoryTagMatcher

    def setUp(self):
        category_value_provider = {
            "foo": "alice",
            "bar": "BOB",
        }
        TagMatcher = OnlyWithCategoryTagMatcher
        self.tag_matcher = OnlyWithAnyCategoryTagMatcher(category_value_provider)
        self.category1_active_tag = TagMatcher.make_category_tag("foo", "alice")
        self.category1_similar_tag = TagMatcher.make_category_tag("foo", "alice2")
        self.category1_other_tag = TagMatcher.make_category_tag("foo", "bob")
        self.category2_active_tag = TagMatcher.make_category_tag("bar", "BOB")
        self.category2_similar_tag = TagMatcher.make_category_tag("bar", "BOB2")
        self.category2_other_tag = TagMatcher.make_category_tag("bar", "CHARLY")
        self.unknown_category_tag = TagMatcher.make_category_tag("UNKNOWN", "one")

    def test_should_exclude_with__returns_false_with_active_tag(self):
        tags1 = [ self.category1_active_tag ]
        tags2 = [ self.category2_active_tag ]
        self.assertEqual(False, self.tag_matcher.should_exclude_with(tags1))
        self.assertEqual(False, self.tag_matcher.should_exclude_with(tags2))

    def test_should_exclude_with__returns_false_with_active_tag_and_more(self):
        test_patterns = [
            ([ self.category1_active_tag, self.category1_other_tag ], "CASE: first"),
            ([ self.category1_other_tag, self.category1_active_tag ], "CASE: last"),
            ([ "foo", self.category1_active_tag, self.category1_other_tag, "bar" ], "CASE: middle"),
        ]
        for tags, case in test_patterns:
            self.assertEqual(False, self.tag_matcher.should_exclude_with(tags),
                             "%s: tags=%s" % (case, tags))

    def test_should_exclude_with__returns_true_with_other_tag(self):
        tags = [ self.category1_other_tag ]
        self.assertEqual(True, self.tag_matcher.should_exclude_with(tags))

    def test_should_exclude_with__returns_true_with_other_tag_and_more(self):
        test_patterns = [
            ([ self.category1_other_tag, "foo" ], "CASE: first"),
            ([ "foo", self.category1_other_tag ], "CASE: last"),
            ([ "foo", self.category1_other_tag, "bar" ], "CASE: middle"),
        ]
        for tags, case in test_patterns:
            self.assertEqual(True, self.tag_matcher.should_exclude_with(tags),
                             "%s: tags=%s" % (case, tags))

    def test_should_exclude_with__returns_true_with_similar_tag(self):
        tags = [ self.category1_similar_tag ]
        self.assertEqual(True, self.tag_matcher.should_exclude_with(tags))

    def test_should_exclude_with__returns_true_with_similar_and_more(self):
        test_patterns = [
            ([ self.category1_similar_tag, "foo" ], "CASE: first"),
            ([ "foo", self.category1_similar_tag ], "CASE: last"),
            ([ "foo", self.category1_similar_tag, "bar" ], "CASE: middle"),
        ]
        for tags, case in test_patterns:
            self.assertEqual(True, self.tag_matcher.should_exclude_with(tags),
                             "%s: tags=%s" % (case, tags))

    def test_should_exclude_with__returns_false_without_category_tag(self):
        test_patterns = [
            ([ ],           "CASE: No tags"),
            ([ "foo" ],     "CASE: One tag"),
            ([ "foo", "bar" ], "CASE: Two tags"),
        ]
        for tags, case in test_patterns:
            self.assertEqual(False, self.tag_matcher.should_exclude_with(tags),
                             "%s: tags=%s" % (case, tags))

    def test_should_exclude_with__returns_false_with_unknown_category_tag(self):
        """Tags from unknown categories, not supported by category_value_provider,
        should not be excluded.
        """
        tags = [ self.unknown_category_tag ]
        self.assertEqual("only.with_UNKNOWN=one", self.unknown_category_tag)
        self.assertEqual(None, self.tag_matcher.category_value_provider.get("UNKNOWN"))
        self.assertEqual(False, self.tag_matcher.should_exclude_with(tags))

    def test_should_exclude_with__combinations_of_2_categories(self):
        test_patterns = [
            ("CASE 00: 2 inactive category tags", True,
             [ self.category1_other_tag, self.category2_other_tag]),
            ("CASE 01: inactive and active category tags", True,
             [ self.category1_other_tag, self.category2_active_tag]),
            ("CASE 10: active and inactive category tags", True,
             [ self.category1_active_tag, self.category2_other_tag]),
            ("CASE 11: 2 active category tags", False,  # -- SHOULD-RUN
             [ self.category1_active_tag, self.category2_active_tag]),
            # -- SPECIAL CASE: With unknown category
            ("CASE 0x: inactive and unknown category tags", True,
             [ self.category1_other_tag, self.unknown_category_tag]),
            ("CASE 1x: active and unknown category tags", False,  # SHOULD-RUN
             [ self.category1_active_tag, self.unknown_category_tag]),
        ]
        for case, expected, tags in test_patterns:
            actual_result = self.tag_matcher.should_exclude_with(tags)
            self.assertEqual(expected, actual_result,
                             "%s: tags=%s" % (case, tags))

    def test_should_run_with__negates_result_of_should_exclude_with(self):
        test_patterns = [
            ([ ],                   "CASE: No tags"),
            ([ "foo" ],             "CASE: One non-category tag"),
            ([ "foo", "bar" ],      "CASE: Two non-category tags"),
            ([ self.category1_active_tag ],   "CASE: active tag"),
            ([ self.category1_active_tag, self.category1_other_tag ],  "CASE: active and other tag"),
            ([ self.category1_active_tag, "foo" ],    "CASE: active and foo tag"),
            ([ self.category1_other_tag ],            "CASE: other tag"),
            ([ self.category1_other_tag, "foo" ],     "CASE: other and foo tag"),
            ([ self.category1_similar_tag ],          "CASE: similar tag"),
            ([ "foo", self.category1_similar_tag ],   "CASE: foo and similar tag"),
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
            ("CASE: with foo",  ["foo", "bar"]),
            ("CASE: with foo2", ["foozy", "foo", "bar"]),
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
            ("CASE: without foo",   ["fool", "bar"]),
            ("CASE: without foo2",  ["foozy", "bar"]),
        ]
        for case, tags in test_patterns:
            actual_result = self.ctag_matcher.should_exclude_with(tags)
            self.assertEqual(False, actual_result,
                             "%s: tags=%s" % (case, tags))

            actual_true_count = self.count_tag_matcher_with_result(
                                    self.ctag_matcher.tag_matchers, tags, True)
            self.assertEqual(0, actual_true_count)
