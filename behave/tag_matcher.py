# -*- coding: utf-8 -*-

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


class OnlyWithCategoryTagMatcher(TagMatcher):
    """
    Provides a tag matcher that allows to determine if feature/scenario
    should run or should be excluded from the run-set (at runtime).

    EXAMPLE:
    --------

    Run some scenarios only when runtime conditions are met:

      * Run scenario Alice only on Windows OS
      * Run scenario Bob only on MACOSX

    .. code-block:: gherkin

        # -- FILE: features/alice.feature
        # TAG SCHEMA: @only.with_{category}.{current_value}
        Feature:

          @only.with_os=win32
          Scenario: Alice (Run only on Windows)
            Given I do something
            ...

          @only.with_os=darwin
          Scenario: Bob (Run only on MACOSX)
            Given I do something else
            ...


    .. code-block:: python

        # -- FILE: features/environment.py
        from behave.tag_matcher import OnlyWithCategoryTagMatcher
        import sys

        # -- MATCHES TAGS: @only.with_{category}=* = @only.with_os=*
        active_tag_matcher = OnlyWithCategoryTagMatcher("os", sys.platform)

        def before_scenario(context, scenario):
            if active_tag_matcher.should_exclude_with(scenario.effective_tags):
                scenario.mark_skipped()   #< LATE-EXCLUDE from run-set.
    """
    tag_prefix = "only.with_"
    value_separator = "="

    def __init__(self, category, value, tag_prefix=None, value_sep=None):
        super(OnlyWithCategoryTagMatcher, self).__init__()
        self.active_tag = self.make_category_tag(category, value,
                                                 tag_prefix, value_sep)
        self.category_tag_prefix = self.make_category_tag(category, None,
                                                   tag_prefix, value_sep)

    def should_exclude_with(self, tags):
        category_tags = self.select_category_tags(tags)
        if category_tags and self.active_tag not in category_tags:
            return True
        # -- OTHERWISE: feature/scenario with theses tags should run.
        return False

    def select_category_tags(self, tags):
        return [tag  for tag in tags
                if tag.startswith(self.category_tag_prefix)]

    @classmethod
    def make_category_tag(cls, category, value=None, tag_prefix=None,
                          value_sep=None):
        if tag_prefix is None:
            tag_prefix = cls.tag_prefix
        if value_sep is None:
            value_sep = cls.value_separator
        value = value or ""
        return "%s%s%s%s" % (tag_prefix, category, value_sep, value)


class OnlyWithAnyCategoryTagMatcher(TagMatcher):
    """
    Provides a tag matcher that matches any category that follows the
    "@only.with_" tag schema and determines if it should run or
    should be excluded from the run-set (at runtime).

    TAG SCHEMA: @only.with_{category}.{value}

    .. seealso:: OnlyWithCategoryTagMatcher

    EXAMPLE:
    --------

    Run some scenarios only when runtime conditions are met:

      * Run scenario Alice only on Windows OS
      * Run scenario Bob only with browser Chrome

    .. code-block:: gherkin

        # -- FILE: features/alice.feature
        # TAG SCHEMA: @only.with_{category}={current_value}
        Feature:

          @only.with_os=win32
          Scenario: Alice (Run only on Windows)
            Given I do something
            ...

          @only.with_browser=chrome
          Scenario: Bob (Run only with Web-Browser Chrome)
            Given I do something else
            ...


    .. code-block:: python

        # -- FILE: features/environment.py
        from behave.tag_matcher import OnlyWithAnyCategoryTagMatcher
        import sys

        # -- MATCHES ANY TAGS: @only.with_{category}={value}
        # NOTE: category_value_provider provides active category values.
        category_value_provider = {
            "browser": os.environ.get("BEHAVE_BROWSER", "chrome"),
            "os":      sys.platform,
        }
        active_tag_matcher = OnlyWithAnyCategoryTagMatcher(category_value_provider)

        def before_scenario(context, scenario):
            if active_tag_matcher.should_exclude_with(scenario.effective_tags):
                scenario.mark_skipped()   #< LATE-EXCLUDE from run-set.
    """

    def __init__(self, category_value_provider, tag_prefix=None, value_sep=None):
        if value_sep is None:
            value_sep = OnlyWithCategoryTagMatcher.value_separator
        self.category_value_provider = category_value_provider
        self.tag_prefix = tag_prefix or OnlyWithCategoryTagMatcher.tag_prefix
        self.value_separator = value_sep

    def should_exclude_with(self, tags):
        exclude_decision_map = {}
        for category_tag in self.select_category_tags(tags):
            category, value = self.parse_category_tag(category_tag)
            active_value = self.category_value_provider.get(category, None)
            if active_value is None:
                # -- CASE: Unknown category, ignore it.
                continue
            elif active_value == value:
                # -- CASE: Active category value selected, decision should run.
                exclude_decision_map[category] = False
            else:
                # -- CASE: Inactive category value selected, may exclude it.
                if not exclude_decision_map.has_key(category):
                    exclude_decision_map[category] = True
        return any(exclude_decision_map.values())

    def select_category_tags(self, tags):
        return [tag  for tag in tags
                if tag.startswith(self.tag_prefix)]

    def parse_category_tag(self, tag):
        assert tag and tag.startswith(self.tag_prefix)
        category_value = tag[len(self.tag_prefix):]
        if self.value_separator in category_value:
            category, value = category_value.split(self.value_separator, 1)
        else:
            # -- OOPS: TAG SCHEMA FORMAT MISMATCH
            category = category_value
            value = None
        return category, value


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
