"""
Contains classes and functionality to provide the active-tag mechanism.
Active-tags provide a skip-if logic based on tags in feature files.
"""

import logging
import operator
import re
import warnings
import six
from ._types import Unknown, require_callable
from .compat.collections import UserDict
from .model_core import TagAndStatusStatement


# -----------------------------------------------------------------------------
# VALUE OBJECT CLASSES FOR: Active-Tag Value Providers
# -----------------------------------------------------------------------------
class ValueObject(object):
    """Value object for active-tags that holds the current value for
    one activate-tag category and its comparison function.

    The :param:`compare_func(current_value, tag_value)` is a predicate function
    with two arguments that performs the comparison between the
    "current_value" and the "tag_value".

    EXAMPLE::

        # -- SIMPLIFIED EXAMPLE:
        from behave.tag_matcher import ValueObject
        import operator     # Module contains comparison functions.
        class NumberObject(ValueObject): ...  # Details left out here.

        xxx_current_value = 42
        active_tag_value_provider = {
            "xxx.value": ValueObject(xxx_current_value)  # USES: operator.eq (equals)
            "xxx.min_value": NumberValueObject(xxx_current_value, operator.ge),
            "xxx.max_value": NumberValueObject(xxx_current_value, operator.le),
        }

        # -- LATER WITHIN: ActivTag Logic
        # EXAMPLE TAG: @use.with_xxx.min_value=10  (schema: "@use.with_{category}={value}")
        tag_category = "xxx.min_value"
        current_value = active_tag_value_provider.get(tag_category)
        if not isinstance(current_value, ValueObject):
            current_value = ValueObject(current_value)
        ...
        tag_matches = current_value.matches(tag_value)
    """
    def __init__(self, value, compare=operator.eq):
        require_callable(compare)
        self._value = value
        self.compare = compare

    @property
    def value(self):
        if callable(self._value):
            # -- SUPPORT: Lazy computation of current-value.
            return self._value()
        # -- OTHERWISE:
        return self._value

    @value.setter
    def value(self, new_value):
        if callable(self._value):
            raise ValueError("CALLABLE: Cannot assign value to active tag")
        self._value = new_value

    def matches(self, tag_value):
        """Comparison between current value and :param:`tag_value`.

        :param tag_value: Tag value from active tag (as string).
        :return: True, if comparison matches. False, otherwise.
        """
        return bool(self.compare(self.value, tag_value))

    @staticmethod
    def on_type_conversion_error(tag_value, e):
        logger = logging.getLogger("behave.active_tags")
        logger.error("TYPE CONVERSION ERROR: active_tag.value='%s' (error: %s)" % \
                     (tag_value, str(e)))
        # MAYBE: logger.exception(e)
        return False    # HINT: mis-matched

    def __str__(self):
        """Conversion to string."""
        return str(self.value)

    def __repr__(self):
        return "<%s: value=%s, compare=%s>" % \
               (self.__class__.__name__, self.value, self.compare)


class NumberValueObject(ValueObject):
    def matches(self, tag_value):
        try:
            tag_number = int(tag_value)
            return super(NumberValueObject, self).matches(tag_number)
        except ValueError as e:
            # -- INTEGER TYPE-CONVERSION ERROR:
            return self.on_type_conversion_error(tag_value, e)

    def __int__(self):
        """Convert into integer-number value."""
        return int(self.value)


class BoolValueObject(ValueObject):
    TRUE_STRINGS = set(["true", "yes", "on"])
    FALSE_STRINGS = set(["false", "no", "off"])

    def matches(self, tag_value):
        try:
            boolean_tag_value = self.to_bool(tag_value)
            return super(BoolValueObject, self).matches(boolean_tag_value)
        except ValueError as e:
            return self.on_type_conversion_error(tag_value, e)

    def __bool__(self):
        """Conversion to boolean value."""
        return bool(self.value)

    @classmethod
    def to_bool(cls, value):
        if isinstance(value, str):
            text = value.lower()
            if text in cls.TRUE_STRINGS:
                return True
            elif text in cls.FALSE_STRINGS:
                return False
            else:
                raise ValueError("NON-BOOL: %s" % value)
        # -- OTHERWISE:
        return bool(value)


# -----------------------------------------------------------------------------
# CLASSES FOR: Active-Tags and ActiveTagMatchers
# -----------------------------------------------------------------------------
class TagMatcher(object):
    """Abstract base class that defines the TagMatcher protocol."""

    def should_skip(self, model_element, use_inherited=False):
        """
        Checks if a model element should be skipped by using its active tags.

        This provides the algorithm how active-tags and inherited active-tags
        should be evaluated:

        * First use only the tags of the model element.
        * Then use also the inherited tags from the parent(s).

        EXAMPLE:

        * An active-tag is assigned to a feature.
        * Then, this active-tag is overridden in a scenario.
        * Scenario active-tags are only evaluated if the feature is not skipped.

        :param model_element:  Feature, Rule or Scenario element.
        :param use_inherited: If true, inherited tags should be evaluated.
        :return: True, if this model element should be skipped.

        .. versionadded:: 1.2.7
        """
        if not isinstance(model_element, TagAndStatusStatement):
            msg = "{!r} (expected: Feature/Rule/Scenario)".format(model_element)
            raise TypeError(msg)

        return (self.should_skip_with_tags(model_element.tags) or
                (use_inherited and
                 self.should_skip_with_tags(model_element.inherited_tags)))

    def should_skip_with_tags(self, tags):
        """
        Determines if a feature/scenario with these tags should be skipped.
        Needs to be implemented by a subclass.

        :param tags:    List of scenario/feature tags to check.
        :return: True, if scenario/feature should be excluded from the run-set.
        :return: False, if scenario/feature should run.

        .. versionadded:: 1.2.7
        """
        raise NotImplementedError()

    def should_run_with_tags(self, tags):
        """
        Determines if a Feature/Rule/Scenario with these tags should run or not.

        :param tags:    List of tags to check.
        :return: True,  if model element should run.
        :return: False, if model element should be skipped.

        .. versionadded:: 1.2.7
        """
        return not self.should_skip_with_tags(tags)

    def should_run_with(self, tags):
        """
        Determines if a Feature/Rule/Scenario with these tags should run or not.

        :param tags:    List of tags to check.
        :return: True,  if model element should run.
        :return: False, if model element should be skipped.

        .. deprecated:: 1.2.7
        """
        # -- BACKWARD-COMPATIBLE: behave < 1.2.7
        warnings.warn("Use 'should_run_with_tags()' instead.", DeprecationWarning)
        return self.should_run_with_tags(tags)

    def should_exclude_with(self, tags):
        """
        Determines if a feature/scenario with these tags should be excluded
        from the run-set.

        :param tags:    List of scenario/feature tags to check.
        :return: True, if scenario/feature should be excluded from the run-set.
        :return: False, if scenario/feature should run.

        .. deprecated:: 1.2.7
        """
        # -- BACKWARD-COMPATIBLE: behave < 1.2.7
        warnings.warn("Use 'should_skip_with_tags()' instead.", DeprecationWarning)
        return self.should_skip_with_tags(tags)


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
            if active_tag_matcher.should_skip_with_tags(feature.tags):
                feature.skip()   #< LATE-EXCLUDE from run-set.

        def before_scenario(context, scenario):
            if active_tag_matcher.should_skip_with_tags(scenario.tags):
                skip_reason = active_tag_matcher.skip_reason
                scenario.skip(skip_reason)   #< LATE-EXCLUDE from run-set.
    """
    value_separator = "="
    tag_prefixes = ["use", "not", "active", "not_active", "only"]
    tag_schema = r"^(?P<prefix>%s)\.with_(?P<category>\w+(\.\w+)*)%s(?P<value>.*)$"
    ignore_unknown_categories = True
    use_skip_reason = False

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
        self.skip_reason = None

    # -- IMPLEMENT INTERFACE FOR: TagMatcher
    def should_skip_with_tags(self, tags):
        """
        Checks if a model element should be skipped by using its active tags.

        :param tags: List of tags to use.
        :return: True, if model element with these tags should be skipped.

        .. versionadded:: 1.2.7
        """
        # print(f"ACTIVE_TAG.should_skip_with_tags: tags={tags};")
        group_categories = list(self.group_active_tags_by_category(tags))
        for group_category, category_tag_pairs in group_categories:
            if not self.is_tag_group_enabled(group_category, category_tag_pairs):
                # -- LOGICAL-AND SHORTCUT: Any false => Makes everything false
                if self.use_skip_reason:
                    current_value = self.value_provider.get(group_category, None)
                    reason = "%s (but: %s)" % (group_category, current_value)
                    self.skip_reason = reason
                # print(f"ACTIVE_TAG.should_skip_with_tags: verdict=true, "
                #       f"reason={self.skip_reason} (categories: {group_categories})")
                return True     # SHOULD-EXCLUDE: not enabled = not False
        # -- LOGICAL-AND: All parts are True
        # print(f"ACTIVE_TAG.should_skip_with_tags: verdict=false (categories: {group_categories})")
        return False    # SHOULD-EXCLUDE: not enabled = not True

    # -- SPECIFIC:
    @property
    def exclude_reason(self):
        # -- BACKWARD-COMPATIBLE: behave < 1.2.7
        warnings.warn("Use 'skip_reason' instead'", DeprecationWarning)
        return self.skip_reason

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
                   | ((xxx == "alice") or (xxx == "bob")) and
                   |  not((xxx == "charly") or (xxx == "doro"))
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

        current_value = self.value_provider.get(group_category, Unknown)
        # print(f"ACTIVE_TAG.is_tag_group_enabled:{group_category}: current_value={current_value}")
        if current_value is Unknown and self.ignore_unknown_categories:
            # -- CASE: Unknown category, ignore it.
            return True
        elif not isinstance(current_value, ValueObject):
            current_value = ValueObject(current_value)

        positive_tags_matched = []
        negative_tags_matched = []
        for category_tag, tag_match in group_tag_pairs:
            tag_prefix = tag_match.group("prefix")
            category = tag_match.group("category")
            tag_value = tag_match.group("value")
            assert category == group_category

            if self.is_tag_negated(tag_prefix):
                # -- CASE: @not.with_CATEGORY=VALUE
                # NORMALLY: tag_matched = (current_value == tag_value)
                tag_matched = current_value.matches(tag_value)
                negative_tags_matched.append(tag_matched)
            else:
                # -- CASE: @use.with_CATEGORY=VALUE
                # NORMALLY: tag_matched = (current_value == tag_value)
                tag_matched = current_value.matches(tag_value)
                positive_tags_matched.append(tag_matched)
        tag_expression1 = any(positive_tags_matched)    #< LOGICAL-OR expression
        tag_expression2 = any(negative_tags_matched)    #< LOGICAL-OR expression
        if not positive_tags_matched:
            tag_expression1 = True
        tag_group_enabled = bool(tag_expression1 and not tag_expression2)
        # print(f"ACTIVE_TAG.is_tag_group_enabled: {group_category}.enabled={tag_group_enabled}")
        return tag_group_enabled

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
        require_callable(exclude_function)
        super(PredicateTagMatcher, self).__init__()
        self.predicate = exclude_function

    def should_skip_with_tags(self, tags):
        return self.predicate(tags)


class CompositeTagMatcher(TagMatcher):
    """Provides a composite tag matcher."""

    def __init__(self, tag_matchers=None):
        super(CompositeTagMatcher, self).__init__()
        self.tag_matchers = tag_matchers or []

    def should_skip_with_tags(self, tags):
        for tag_matcher in self.tag_matchers:
            if tag_matcher.should_skip_with_tags(tags):
                return True
        # -- OTHERWISE:
        return False


# -----------------------------------------------------------------------------
# ACTIVE TAG VALUE PROVIDER CLASSES:
# -----------------------------------------------------------------------------
class IActiveTagValueProvider(object):
    """Protocol/Interface for active-tag value providers."""

    def get(self, category, default=None):
        return NotImplemented


class ActiveTagValueProvider(UserDict):
    def __init__(self, data=None):
        if data is None:
            data = {}
        UserDict.__init__(self, data)

    @staticmethod
    def use_value(value):
        if callable(value):
            # -- RE-EVALUATE VALUE: Each time
            value_func = value
            value = value_func()
        return value

    def __getitem__(self, name):
        value = self.data[name]
        return self.use_value(value)

    def get(self, category, default=None):
        value = self.data.get(category, default)
        return self.use_value(value)

    def values(self):
        for value in self.data.values(self):
            yield self.use_value(value)

    def items(self):
        for category, value in self.data.items():
            yield (category, self.use_value(value))

    def categories(self):
        return self.keys()


class CompositeActiveTagValueProvider(ActiveTagValueProvider):
    """Provides a composite helper class to resolve active-tag values
    from a list of value-providers.
    """

    def __init__(self, value_providers=None):
        if value_providers is None:
            value_providers = []
        super(CompositeActiveTagValueProvider, self).__init__()
        self.value_providers = list(value_providers)

    def get(self, category, default=None):
        # -- FIRST: Check category cached-map (=self.data)
        value = self.data.get(category, Unknown)
        if value is Unknown:
            # -- NOT DISCOVERED: Search over value_providers.
            for value_provider in self.value_providers:
                value = value_provider.get(category, Unknown)
                if value is Unknown:
                    continue

                # -- FOUND CATEGORY:
                self.data[category] = value
                break
            # -- FOUND-CATEGORY or NOT-FOUND:
            if value is Unknown:
                value = default

        return self.use_value(value)

    # -- MORE: Provide a dict-like interface.
    def keys(self):
        for value_provider in self.value_providers:
            try:
                for category in value_provider.keys():
                    yield category
            except AttributeError:
                # -- keys() method not supported.
                pass

    def values(self):
        for category in self.keys():
            value = self.get(category)
            yield value

    def items(self):
        for category in self.keys():
            value = self.get(category)
            yield category, value


# -----------------------------------------------------------------------------
# UTILITY FUNCTIONS:
# -----------------------------------------------------------------------------
def bool_to_string(value):
    """Converts a boolean active-tag value into its normalized
    string representation.

    :param value:  Boolean value to use (or value converted into bool).
    :returns: Boolean value converted into a normalized string.
    """
    return str(bool(value)).lower()


def setup_active_tag_values(active_tag_values, data):
    """Setup/update active_tag values with dict-like data.
    Only values for keys that are already present are updated.

    :param active_tag_values:   Data storage for active_tag value (dict-like).
    :param data:   Data that should be used for active_tag values (dict-like).
    """
    for category in list(active_tag_values.keys()):
        if category in data:
            active_tag_values[category] = data[category]


def print_active_tags(active_tag_value_provider, categories=None):
    """Print a summary of the current active-tag values."""
    if categories is None:
        try:
            categories = list(active_tag_value_provider.keys())
        except TypeError:   # TypeError: object is not iterable
            categories = []

    active_tag_data = active_tag_value_provider
    print("ACTIVE-TAGS:")
    for category in categories:
        active_tag_value = active_tag_data.get(category)
        print("use.with_{category}={value}".format(
            category=category, value=active_tag_value))

    # -- FINALLY: TRAILING NEW-LINE
    print()
