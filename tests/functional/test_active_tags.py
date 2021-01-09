# -*- coding: utf-8 -*-
"""
Functionals tests for active tag-matcher (mod:`behave.tag_matcher`).
"""

from __future__ import absolute_import, print_function
import pytest
from behave.tag_matcher import ActiveTagMatcher

# =============================================================================
# TEST DATA:
# =============================================================================
# VALUE_PROVIDER = {
#     "foo": "alice",
#     "bar": "BOB",
# }

# =============================================================================
# PYTEST FIXTURES:
# =============================================================================
# @pytest.fixture
# def active_tag_matcher():
#     tag_matcher = ActiveTagMatcher(VALUE_PROVIDER)
#     return tag_matcher


# =============================================================================
# TEST SUITE:
# =============================================================================
class TestActivateTags(object):
    VALUE_PROVIDER = {
        "foo": "Frank",
        "bar": "Bob",
        # "OTHER": "VALUE",
    }

    def check_should_run_with_active_tags(self, case, expected, tags):
        # -- tag_matcher.should_run_with(tags).result := expected
        case += " (tags: {tags})"
        tag_matcher = ActiveTagMatcher(self.VALUE_PROVIDER)
        actual_result1 = tag_matcher.should_run_with(tags)
        actual_result2 = tag_matcher.should_exclude_with(tags)
        assert expected == actual_result1, case.format(tags=tags)
        assert (not expected) == actual_result2

    @pytest.mark.parametrize("case, expected, tags", [
        ("use.with_foo=VALUE matches",     True, ["use.with_foo=Frank"]),
        ("use.with_foo=VALUE mismatches", False, ["use.with_foo=OTHER"]),
        ("not.with_foo=VALUE matches",    False, ["not.with_foo=Frank"]),
        ("not.with_foo=VALUE mismatches",  True, ["not.with_foo=OTHER"]),
        ("NO_TAGS", True, []),
    ])
    def test_one_tag_for_category1(self, case, expected, tags):
        self.check_should_run_with_active_tags(case, expected, tags)

    @pytest.mark.parametrize("case, expected, tags", [
        ("use.with_bar=Bob matches",       True, ["use.with_bar=Bob"]),
        ("use.with_bar=VALUE mismatches", False, ["use.with_bar=OTHER"]),
        ("not.with_bar=VALUE matches",    False, ["not.with_bar=Bob"]),
        ("not.with_bar=VALUE mismatches",  True, ["not.with_bar=OTHER"]),
    ])
    def test_one_tag_for_category2(self, case, expected, tags):
        self.check_should_run_with_active_tags(case, expected, tags)

    # @pytest.mark.parametrize("case, expected, tags", [
    #     ("use.with_OTHER=VALUE matches",     True, ["use.with_OTHER=VALUE"]),
    #     ("use.with_OTHER=VALUE mismatches", False, ["use.with_OTHER=OTHER"]),
    #     ("not.with_OTHER=VALUE matches",    False, ["not.with_OTHER=VALUE"]),
    #     ("not.with_OTHER=VALUE mismatches",  True, ["not.with_OTHER=OTHER"]),
    # ])
    # def test_one_tag_for_other_category(self, case, expected, tags):
    #     self.check_should_run_with_active_tags(case, expected, tags)

    @pytest.mark.parametrize("case, expected, tags", [
        ("2x use.with_foo=VALUE: one matches", True,
         ["use.with_foo=Frank", "use.with_foo=OTHER"]),
        ("2x not.with_foo=VALUE: one matches", False,
         ["not.with_foo=Frank", "not.with_foo=OTHER"]),
        ("1x use./not.with_foo=VALUE: use-matches", True,
         ["use.with_foo=Frank", "not.with_foo=OTHER"]),
        ("1x use./not.with_foo=VALUE: not-matches", False,
         ["not.with_foo=Frank", "use.with_foo=OTHER"]),
    ])
    def test_one_category_with_two_tags(self, case, expected, tags):
        self.check_should_run_with_active_tags(case, expected, tags)

    @pytest.mark.parametrize("case, expected, tags", [
        ("3x use.with_foo=VALUE: one matches", True,
         ["use.with_foo=Frank", "use.with_foo=OTHER_1", "use.with_foo=OTHER_2"]),
        ("3x not.with_foo=VALUE: one matches", False,
         ["not.with_foo=Frank", "not.with_foo=OTHER_1", "not.with_foo=OTHER_2"]),
        ("2x use.with_foo=VALUE: use-matches", True,
         ["use.with_foo=Frank", "use.with_foo=OTHER_1", "not.with_foo=OTHER_2"]),
        ("2x not.with_foo=VALUE: not-matches", False,
         ["not.with_foo=Frank", "not.with_foo=OTHER_1", "use.with_foo=OTHER_2"]),
        ("1x use.with_foo=VALUE: use-matches", True,
         ["use.with_foo=Frank", "not.with_foo=OTHER_1", "not.with_foo=OTHER_2"]),
        ("1x not.with_foo=VALUE: not-matches", False,
         ["not.with_foo=Frank", "use.with_foo=OTHER_1", "use.with_foo=OTHER_2"]),
    ])
    def test_one_category_with_three_tags(self, case, expected, tags):
        self.check_should_run_with_active_tags(case, expected, tags)

    @pytest.mark.parametrize("case, expected, tags", [
        # -- use.with_CATEGORY=VALUE
        ("use.with_... 2x matches",      True, ["use.with_foo=Frank", "use.with_bar=Bob"]),
        ("use.with_... 1x matches",     False, ["use.with_foo=Frank", "use.with_bar=OTHER"]),
        ("use.with_... 1x matches",     False, ["use.with_foo=OTHER", "use.with_bar=OTHER"]),
        ("use.with_... 1x matches",     False, ["use.with_foo=OTHER", "use.with_bar=Bob"]),
        ("use.with_... 0x matches",     False, ["use.with_foo=OTHER", "use.with_bar=OTHER"]),
        # -- not.with_CATEGORY=VALUE
        ("not.with_... 2x matches", False, ["not.with_foo=Frank", "not.with_bar=Bob"]),
        ("not.with_... 1x matches", False, ["not.with_foo=Frank", "not.with_bar=OTHER"]),
        ("not.with_... 1x matches", False, ["not.with_foo=OTHER", "not.with_bar=Bob"]),
        ("not.with_... 0x matches",  True, ["not.with_foo=OTHER", "not.with_bar=OTHER"]),
        # -- use.with_CATEGORY_1=VALUE_1, not.with_CATEGORY_2=VALUE_2
        ("use./not.with_... use-matches",  True, ["use.with_foo=Frank", "not.with_bar=OTHER"]),
        ("use./not.with_... not-matches", False, ["use.with_foo=OTHER", "not.with_bar=Bob"]),
        ("use./not.with_... 2x matches",  False, ["use.with_foo=Frank", "not.with_bar=Bob"]),
        ("use./not.with_... 0x matches",  False, ["use.with_foo=OTHER", "not.with_bar=OTHER"]),
    ])
    def test_two_categories_with_two_tags(self, case, expected, tags):
        self.check_should_run_with_active_tags(case, expected, tags)

    @pytest.mark.parametrize("case, expected, tags", [
        # -- use.with_CATEGORY=VALUE
        ("use.with_... 2x matches",      True, ["use.with_foo=Frank", "use.with_foo=OTHER", "use.with_bar=Bob"]),
        ("use.with_... 1x matches",     False, ["use.with_foo=Frank", "use.with_foo=OTHER", "use.with_bar=OTHER"]),
        ("use.with_... 1x matches",     False, ["use.with_foo=OTHER", "use.with_foo=Frank", "use.with_bar=OTHER"]),
        ("use.with_... 1x matches",     False, ["use.with_foo=OTHER", "use.with_foo=OTHER2", "use.with_bar=Bob"]),
        ("use.with_... 0x matches",     False, ["use.with_foo=OTHER", "use.with_bar=OTHER2", "use.with_bar=OTHER"]),
        # -- not.with_CATEGORY=VALUE
        ("not.with_... 2x matches", False, ["not.with_foo=Frank", "not.with_foo=OTHER", "not.with_bar=Bob"]),
        ("not.with_... 1x matches", False, ["not.with_foo=Frank", "not.with_foo=OTHER", "not.with_bar=OTHER"]),
        ("not.with_... 1x matches", False, ["not.with_foo=OTHER", "not.with_foo=OTHER2", "not.with_bar=Bob"]),
        ("not.with_... 0x matches",  True, ["not.with_foo=OTHER", "not.with_foo=OTHER2", "not.with_bar=OTHER"]),
        # -- use.with_CATEGORY_1=VALUE_1, not.with_CATEGORY_2=VALUE_2
        ("use./not.with_... use-matches",  True, ["use.with_foo=Frank", "use.with_foo=OTHER", "not.with_bar=OTHER"]),
        ("use./not.with_... not-matches", False, ["use.with_foo=OTHER", "use.with_foo=OTHER2", "not.with_bar=Bob"]),
        ("use./not.with_... 2x matches",  False, ["use.with_foo=Frank", "use.with_foo=OTHER", "not.with_bar=Bob"]),
        ("use./not.with_... 0x matches",  False, ["use.with_foo=OTHER", "use.with_foo=OTHER2", "not.with_bar=OTHER"]),
        # -- not.with_CATEGORY_1=VALUE_1, use.with_CATEGORY_2=VALUE_2
        ("use./not.with_... not-matches", False, ["not.with_foo=Frank", "not.with_foo=OTHER", "use.with_bar=OTHER"]),
        ("use./not.with_... use-matches", True, ["not.with_foo=OTHER", "not.with_foo=OTHER2", "use.with_bar=Bob"]),
        ("use./not.with_... 2x matches", False, ["not.with_foo=Frank", "not.with_foo=OTHER", "use.with_bar=Bob"]),
        ("use./not.with_... 0x matches", False, ["not.with_foo=OTHER", "not.with_foo=OTHER2", "use.with_bar=OTHER"]),
    ])
    def test_two_categories_with_three_tags(self, case, expected, tags):
        self.check_should_run_with_active_tags(case, expected, tags)

'''
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
class TestActiveTagMatcher2(object):
    TagMatcher = ActiveTagMatcher
    traits = Traits4ActiveTagMatcher

    @classmethod
    def make_tag_matcher(cls):
        value_provider = {
            "foo": "alice",
            "bar": "BOB",
        }
        tag_matcher = cls.TagMatcher(value_provider)
        return tag_matcher

    @pytest.mark.parametrize("case, expected_len, tags", [
        ("case: Two enabled tags", 2,
         [traits.category1_enabled_tag, traits.category2_enabled_tag]),
        ("case: Active enabled and normal tag", 1,
         [traits.category1_enabled_tag,  "foo"]),
        ("case: Active disabled and normal tag", 1,
         [traits.category1_disabled_tag, "foo"]),
        ("case: Normal and active negated tag", 1,
         ["foo", traits.category1_not_enabled_tag]),
        ("case: Two normal tags", 0,
         ["foo", "bar"]),
    ])
    def test_select_active_tags__with_two_tags(self, case, expected_len, tags):
        tag_matcher = self.make_tag_matcher()
        selected = tag_matcher.select_active_tags(tags)
        selected = list(selected)
        assert len(selected) == expected_len, case

    @pytest.mark.parametrize("case, expected, tags", [
        # -- GROUP: With positive logic (non-negated tags)
        ("case P00: 2 disabled tags", True,
         [ traits.category1_disabled_tag, traits.category2_disabled_tag]),
        ("case P01: disabled and enabled tag", True,
         [ traits.category1_disabled_tag, traits.category2_enabled_tag]),
        ("case P10: enabled and disabled tag", True,
         [ traits.category1_enabled_tag, traits.category2_disabled_tag]),
        ("case P11: 2 enabled tags", False,  # -- SHOULD-RUN
         [ traits.category1_enabled_tag, traits.category2_enabled_tag]),
        # -- GROUP: With negated tag
        ("case N00: not-enabled and disabled tag", True,
         [ traits.category1_not_enabled_tag, traits.category2_disabled_tag]),
        ("case N01: not-enabled and enabled tag", True,
         [ traits.category1_not_enabled_tag, traits.category2_enabled_tag]),
        ("case N10: not-disabled and disabled tag", True,
         [ traits.category1_not_disabled_tag, traits.category2_disabled_tag]),
        ("case N11: not-disabled and enabled tag", False, # -- SHOULD-RUN
         [ traits.category1_not_disabled_tag, traits.category2_enabled_tag]),
        # -- GROUP: With unknown category
        ("case U0x: disabled and unknown tag", True,
         [ traits.category1_disabled_tag, traits.unknown_category_tag]),
        ("case U1x: enabled and unknown tag", False,  # -- SHOULD-RUN
         [ traits.category1_enabled_tag, traits.unknown_category_tag]),
    ])
    def test_should_exclude_with__combinations_of_2_categories(self, case, expected, tags):
        tag_matcher = self.make_tag_matcher()
        actual_result = tag_matcher.should_exclude_with(tags)
        assert expected == actual_result, case

    @pytest.mark.parametrize("case, expected, tags", [
        # -- GROUP: With positive logic (non-negated tags)
        ("case P00: 2 disabled tags", True,
         [ traits.category1_disabled_tag, traits.category1_disabled_tag2]),
        ("case P01: disabled and enabled tag", False,
         [ traits.category1_disabled_tag, traits.category1_enabled_tag]),
        ("case P10: enabled and disabled tag", False,
         [ traits.category1_enabled_tag, traits.category1_disabled_tag]),
        ("case P11: 2 enabled tags (same)", False,  # -- SHOULD-RUN
         [ traits.category1_enabled_tag, traits.category1_enabled_tag]),
        # -- GROUP: With negated tag
        ("case N00: not-enabled and disabled tag", True,
         [ traits.category1_not_enabled_tag, traits.category1_disabled_tag]),
        ("case N01: not-enabled and enabled tag", True,
         [ traits.category1_not_enabled_tag, traits.category1_enabled_tag]),
        ("case N10: not-disabled and disabled tag", True,
         [ traits.category1_not_disabled_tag, traits.category1_disabled_tag]),
        ("case N11: not-disabled and enabled tag", False, # -- SHOULD-RUN
         [ traits.category1_not_disabled_tag, traits.category1_enabled_tag]),
    ])
    def test_should_exclude_with__combinations_with_same_category(self,
                                                        case, expected, tags):
        tag_matcher = self.make_tag_matcher()
        print("tags: {}".format(tags) )
        print("tag_matcher.value: {}".format(tag_matcher.value_provider) )
        actual_result = tag_matcher.should_exclude_with(tags)
        assert expected == actual_result, case


class TestActiveTags(TestCase):
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
            ("with_foo=Frank",          "case: Subset of an active tag"),
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
        # pylint: disable=line-too-long
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
        self.assertEqual("use.with_UNKNOWN=one", traits.unknown_category_tag)
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
'''

