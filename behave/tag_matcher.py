# -*- coding: UTF-8 -*-
"""
Contains classes and functionality to provide the active-tag mechanism.
Active-tags provide a skip-if logic based on tags in feature files.
"""

from __future__ import absolute_import
import re
import operator
import six


def bool_to_string(value):
    """Converts a Boolean value into its normalized string representation."""
    return str(bool(value)).lower()


class TagMatcher(object):
    """Abstract base class that defines the TagMatcher protocol."""

    def should_run_with(self, tags):
        """Determines if a feature/scenario with these tags should run or not.

        :param tags:    List of scenario/feature tags to check.
        :return: True,  if scenario/feature should run.
        :return: False, if scenario/feature should be excluded from the run-set.
        """
        return not self.should_exclude_with(tags)

    def should_exclude_with(self, tags):
        """Determines if a feature/scenario with these tags should be excluded
        from the run-set.

        :param tags:    List of scenario/feature tags to check.
        :return: True, if scenario/feature should be excluded from the run-set.
        :return: False, if scenario/feature should run.
        """
        raise NotImplementedError


class ActiveTagMatcher(TagMatcher):
    """Provides an active tag matcher for many categories.

    TAG SCHEMA 1 (preferred):
      * use.with_{category}={value}
      * not.with_{category}={value}

    TAG SCHEMA 2:
      * active.with_{category}={value}
      * not_active.with_{category}={value}

    TAG LOGIC
    ----------

    Determine active-tag groups by grouping active-tags
    with same category together::

        active_group.enabled := enabled(group.tag1) or enabled(group.tag2) or ...
        active_tags.enabled  := enabled(group1) and enabled(group2) and ...

    All active-tag groups must be turned "on" (enabled).
    Otherwise, the model element should be excluded.

    CONCEPT: ValueProvider
    ------------------------------

    A ValueProvider provides the value of a category, used in active tags.
    A ValueProvider must provide a mapping-like protocol:

    .. code-block:: python

        class MyValueProvider(object):
            def get(self, category_name, default=None):
                ...
                return category_value   # OR: default, if category is unknown.

    EXAMPLE:
    --------

    Run some scenarios only when runtime conditions are met:

      * Run scenario Alice only on Windows OS
      * Run scenario Bob with all browsers except Chrome

    .. code-block:: gherkin

        # -- FILE: features/alice.feature
        Feature:

          @use.with_os=win32
          Scenario: Alice (Run only on Windows)
            Given I do something
            ...

          @not.with_browser=chrome
          Scenario: Bob (Excluded with Web-Browser Chrome)
            Given I do something else
            ...


    .. code-block:: python

        # -- FILE: features/environment.py
        from behave.tag_matcher import ActiveTagMatcher
        import sys

        # -- MATCHES ANY ACTIVE TAGS: @{prefix}.with_{category}={value}
        # NOTE: active_tag_value_provider provides current category values.
        active_tag_value_provider = {
            "browser": os.environ.get("BEHAVE_BROWSER", "chrome"),
            "os":      sys.platform,
        }
        active_tag_matcher = ActiveTagMatcher(active_tag_value_provider)

        def before_feature(context, feature):
            if active_tag_matcher.should_exclude_with(feature.tags):
                feature.skip()   #< LATE-EXCLUDE from run-set.

        def before_scenario(context, scenario):
            if active_tag_matcher.should_exclude_with(scenario.effective_tags):
                exclude_reason = active_tag_matcher.exclude_reason
                scenario.skip(exclude_reason)   #< LATE-EXCLUDE from run-set.
    """
    value_separator = "="
    tag_prefixes = ["use", "not", "active", "not_active", "only"]
    tag_schema = r"^(?P<prefix>%s)\.with_(?P<category>\w+(\.\w+)*)%s(?P<value>.*)$"
    ignore_unknown_categories = True
    use_exclude_reason = False

    def __init__(self, value_provider, tag_prefixes=None,
                 value_separator=None, ignore_unknown_categories=None):
        if value_provider is None:
            value_provider = {}
        if tag_prefixes is None:
            tag_prefixes = self.tag_prefixes
        if ignore_unknown_categories is None:
            ignore_unknown_categories = self.ignore_unknown_categories

        super(ActiveTagMatcher, self).__init__()
        self.value_provider = value_provider
        self.tag_pattern = self.make_tag_pattern(tag_prefixes, value_separator)
        self.tag_prefixes = tag_prefixes
        self.ignore_unknown_categories = ignore_unknown_categories
        self.exclude_reason = None

    @classmethod
    def make_tag_pattern(cls, tag_prefixes, value_separator=None):
        if value_separator is None:
            value_separator = cls.value_separator
        any_tag_prefix = r"|".join(tag_prefixes)
        expression = cls.tag_schema % (any_tag_prefix, value_separator)
        return re.compile(expression)

    @classmethod
    def make_category_tag(cls, category, value=None,
                          tag_prefix=None, value_sep=None):
        """Build category tag (mostly for testing purposes).
        :return: Category tag as string (without leading AT char).
        """
        if tag_prefix is None:
            tag_prefix = cls.tag_prefixes[0]    # -- USE: First as default.
        if value_sep is None:
            value_sep = cls.value_separator
        value = value or ""
        return "%s.with_%s%s%s" % (tag_prefix, category, value_sep, value)

    def is_tag_negated(self, tag):      # pylint: disable=no-self-use
        return tag.startswith("not")

    def is_tag_group_enabled(self, group_category, group_tag_pairs):
        """Provides boolean logic to determine if all active-tags
        which use the same category result in an enabled value.

        .. code-block:: gherkin

            @use.with_xxx=alice
            @use.with_xxx=bob
            @not.with_xxx=charly
            @not.with_xxx=doro
            Scenario:
                Given a step passes
                ...

        Use LOGICAL expression for active-tags with same category::

            category_tag_group.enabled := positive-tag-expression and not negative-tag-expression
              positive-tag-expression  := enabled(tag1) or enabled(tag2) or ...
              negative-tag-expression  := enabled(tag3) or enabled(tag4) or ...
               tag1, tag2 are positive-tags, like @use.with_category=value
               tag3, tag4 are negative-tags, like @not.with_category=value

             xxx   | Only use parts: (xxx == "alice") or (xxx == "bob")
            -------+-------------------
            alice  | true
            bob    | true
            other  | false

             xxx   | Only not parts:
                   | (not xxx == "charly") and (not xxx == "doro")
                   | = not((xxx == "charly") or (xxx == "doro"))
            -------+-------------------
            charly | false
            doro   | false
            other  | true

             xxx   | Use and not parts:
                   | ((xxx == "alice") or (xxx == "bob")) and not((xxx == "charly") or (xxx == "doro"))
            -------+-------------------
            alice  | true
            bob    | true
            charly | false
            doro   | false
            other  | false

        :param group_category:      Category for this tag-group (as string).
        :param category_tag_group:  List of active-tag match-pairs.
        :return: True, if tag-group is enabled.
        """
        if not group_tag_pairs:
            # -- CASE: Empty group is always enabled (CORNER-CASE).
            return True

        current_value = self.value_provider.get(group_category, None)
        if current_value is None and self.ignore_unknown_categories:
            # -- CASE: Unknown category, ignore it.
            return True

        positive_tags_matched = []
        negative_tags_matched = []
        for category_tag, tag_match in group_tag_pairs:
            tag_prefix = tag_match.group("prefix")
            category = tag_match.group("category")
            tag_value = tag_match.group("value")
            assert category == group_category

            if self.is_tag_negated(tag_prefix):
                # -- CASE: @not.with_CATEGORY=VALUE
                tag_matched = (tag_value == current_value)
                negative_tags_matched.append(tag_matched)
            else:
                # -- CASE: @use.with_CATEGORY=VALUE
                tag_matched = (tag_value == current_value)
                positive_tags_matched.append(tag_matched)
        tag_expression1 = any(positive_tags_matched)    #< LOGICAL-OR expression
        tag_expression2 = any(negative_tags_matched)    #< LOGICAL-OR expression
        if not positive_tags_matched:
            tag_expression1 = True
        tag_group_enabled = bool(tag_expression1 and not tag_expression2)
        return tag_group_enabled

    def should_exclude_with(self, tags):
        group_categories = self.group_active_tags_by_category(tags)
        for group_category, category_tag_pairs in group_categories:
            if not self.is_tag_group_enabled(group_category, category_tag_pairs):
                # -- LOGICAL-AND SHORTCUT: Any false => Makes everything false
                if self.use_exclude_reason:
                    current_value = self.value_provider.get(group_category, None)
                    reason = "%s (but: %s)" % (group_category, current_value)
                    self.exclude_reason = reason
                return True     # SHOULD-EXCLUDE: not enabled = not False
        # -- LOGICAL-AND: All parts are True
        return False    # SHOULD-EXCLUDE: not enabled = not True

    def select_active_tags(self, tags):
        """Select all active tags that match the tag schema pattern.

        :param tags: List of tags (as string).
        :return: List of (tag, match_object) pairs (as generator).
        """
        for tag in tags:
            match_object = self.tag_pattern.match(tag)
            if match_object:
                yield (tag, match_object)

    def group_active_tags_by_category(self, tags):
        """Select all active tags that match the tag schema pattern
        and returns groups of active-tags, each group with tags
        of the same category.

        :param tags: List of tags (as string).
        :return: List of tag-groups (as generator), each tag-group is a
                list of (tag1, match1) pairs for the same category.
        """
        category_tag_groups = {}
        for tag in tags:
            match_object = self.tag_pattern.match(tag)
            if match_object:
                category = match_object.group("category")
                category_tag_pairs = category_tag_groups.get(category, None)
                if category_tag_pairs is None:
                    category_tag_pairs = category_tag_groups[category] = []
                category_tag_pairs.append((tag, match_object))

        for category, category_tag_pairs in six.iteritems(category_tag_groups):
            yield (category, category_tag_pairs)


class PredicateTagMatcher(TagMatcher):
    def __init__(self, exclude_function):
        assert callable(exclude_function)
        super(PredicateTagMatcher, self).__init__()
        self.predicate = exclude_function

    def should_exclude_with(self, tags):
        return self.predicate(tags)


class CompositeTagMatcher(TagMatcher):
    """Provides a composite tag matcher."""

    def __init__(self, tag_matchers=None):
        super(CompositeTagMatcher, self).__init__()
        self.tag_matchers = tag_matchers or []

    def should_exclude_with(self, tags):
        for tag_matcher in self.tag_matchers:
            if tag_matcher.should_exclude_with(tags):
                return True
        # -- OTHERWISE:
        return False


def setup_active_tag_values(active_tag_values, data):
    """Setup/update active_tag values with dict-like data.
    Only values for keys that are already present are updated.

    :param active_tag_values:   Data storage for active_tag value (dict-like).
    :param data:   Data that should be used for active_tag values (dict-like).
    """
    for category in list(active_tag_values.keys()):
        if category in data:
            active_tag_values[category] = data[category]
