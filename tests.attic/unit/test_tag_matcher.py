# -----------------------------------------------------------------------------
# PROTOTYPING CLASSES (deprecating) -- Should no longer be used.
# -----------------------------------------------------------------------------

import warnings
from unittest import TestCase
from behave.attic.tag_matcher import \
    OnlyWithCategoryTagMatcher,  OnlyWithAnyCategoryTagMatcher


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
