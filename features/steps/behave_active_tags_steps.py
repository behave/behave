# -*- coding: UTF-8 -*-
"""

.. code-block:: gherkin

    Given I setup the current values for active tags with:
        | category | value |
        | foo      | xxx   |
    Then the following active tag combinations are enabled:
        | tags                | enabled? |
        | @use.with_foo=xxx   | yes      |
        | @use.with_foo=other | no       |
    Then the following active tag combinations are enabled with inherited tags:
        | tags                | inherited_tags      | enabled? |
        | @use.with_foo=xxx   | @use.with_foo=other | yes      |
        | @use.with_foo=xxx   | @not.with_foo=xxx   | yes      |
        | @use.with_foo=other | @use.with_foo=xxx   | yes      |
        | @use.with_foo=other | @not.with_foo=xxx   | no       |

"""

import operator
from behave import given, then, step
from behave._types import parse_bool
from behave.active_tag.python import (
    ACTIVE_TAG_VALUE_PROVIDER as ACTIVE_TAG_VALUE_PROVIDER4PYTHON
)
from behave.model_core import TagAndStatusStatement
from behave.tag_matcher import (
    ActiveTagMatcher, NumberValueObject
)
from behave.tag_expression import TagExpression
from behave4cmd0.step_util import require_table
from hamcrest import assert_that, equal_to


# -----------------------------------------------------------------------------
# CONSTANTS
# -----------------------------------------------------------------------------
ACTIVE_TAG_VALUE_PROVIDER = {
    "temperature.min_value": NumberValueObject(20, operator.ge),
    "temperature.max_value": NumberValueObject(100, operator.le),
}
ACTIVE_TAG_VALUE_PROVIDER.update(ACTIVE_TAG_VALUE_PROVIDER4PYTHON)
NUMBER_VALUES = set(["temperature.min_value", "temperature.max_value"])


# -----------------------------------------------------------------------------
# UTILITY FUNCTIONS:
# -----------------------------------------------------------------------------
def normalize_tags(tags):
    # -- STRIP: Leading '@' from tags.
    return [TagExpression.normalize_tag(tag)  for tag in tags]

def make_model_element(**kwargs):
    this_args = dict(
        filename="some.feature",
        line=42,
        keyword=u"Scenario",
        name=u"",
        tags=None,
    )
    this_args.update(kwargs)
    return TagAndStatusStatement(**this_args)


# -----------------------------------------------------------------------------
# STEP DEFINITIONS:
# -----------------------------------------------------------------------------
@given(u'I setup the current values for active tags with')
@given(u'I setup the current values for active tags with:')
def step_given_setup_the_current_values_for_active_tags_with(ctx):
    require_table(ctx, with_columns=["category", "current_value"])

    active_values = getattr(ctx, "active_value_provider", None)
    if active_values is None:
        # -- SETUP DATA:
        active_value_provider = {}
        active_value_provider.update(ACTIVE_TAG_VALUE_PROVIDER)
        ctx.active_value_provider = active_value_provider
        active_values = active_value_provider

    for row in ctx.table.rows:
        category = row["category"]
        current_value = row["current_value"]
        if category in NUMBER_VALUES:
            current_value = int(current_value)

        value_object = active_values.get(category, None)
        if value_object is not None:
            # -- USE EXISTING VALUE OBJECT:
            value_object.value = current_value
            current_value = value_object
        active_values[category] = current_value


@then(u'the following active tag combinations are enabled')
@then(u'the following active tag combinations are enabled:')
def step_then_following_active_tags_combinations_are_enabled(ctx):
    require_table(ctx, with_columns=["tags", "enabled?"])
    assert ctx.active_value_provider, "REQUIRE: active_value_provider"
    # WAS: assert ctx.table, "REQUIRE: table"
    # WAS: ctx.table.require_columns(["tags", "enabled?"])
    ignore_unknown_categories = getattr(ctx,
        "active_tags_ignore_unknown_categories",
        ActiveTagMatcher.ignore_unknown_categories)

    table = ctx.table
    annotate_column_id = 0
    active_tag_matcher = ActiveTagMatcher(ctx.active_value_provider)
    active_tag_matcher.ignore_unknown_categories = ignore_unknown_categories
    mismatched_rows = []
    for row_index, row in enumerate(table.rows):
        tags = normalize_tags(row["tags"].split())
        expected_enabled = parse_bool(row["enabled?"])
        actual_enabled = active_tag_matcher.should_run_with_tags(tags)

        if actual_enabled != expected_enabled:
            print("MISMATCH with tags: {} -- expected:{} != actual:{}".format(
                tags, expected_enabled, actual_enabled
            ))
            # -- ANNOTATE MISMATCH IN EXTRA COLUMN:
            if annotate_column_id == 0:
                annotate_column_id = table.ensure_column_exists("MISMATCH!")
            row.cells[annotate_column_id] = "= %s" % actual_enabled
            mismatched_rows.append(row_index)

    # -- FINALLY: Ensure that there are no mismatched rows.
    assert_that(mismatched_rows, equal_to([]),
                "No mismatched rows: {}".format(mismatched_rows))

@then(u'the following active tag combinations are enabled with inherited tags:')
def step_then_following_active_tags_combinations_are_enabled_with_inherited_tags(ctx):
    require_table(ctx, with_columns=["tags", "inherited_tags", "enabled?"])
    assert ctx.active_value_provider, "REQUIRE: active_value_provider"
    ignore_unknown_categories = getattr(ctx,
        "active_tags_ignore_unknown_categories",
        ActiveTagMatcher.ignore_unknown_categories)

    table = ctx.table
    annotate_column_id = 0
    active_tag_matcher = ActiveTagMatcher(ctx.active_value_provider)
    active_tag_matcher.ignore_unknown_categories = ignore_unknown_categories
    mismatched_rows = []
    for row_index, row in enumerate(table.rows):
        tags = normalize_tags(row["tags"].split())
        inherited_tags = normalize_tags(row["inherited_tags"].split())
        expected_enabled = parse_bool(row["enabled?"])

        model_parent  = make_model_element(keyword=u"Feature", tags=inherited_tags)
        model_element = make_model_element(keyword=u"Scenario", tags=tags,
                                          parent=model_parent)
        actual_enabled = not active_tag_matcher.should_skip(model_element,
                                                            use_inherited=True)

        if actual_enabled != expected_enabled:
            print("MISMATCH with tags: {}, inherited_tags: {} -- expected:{} != actual:{}".format(
                " ".join(tags), " ".join(inherited_tags),
                expected_enabled, actual_enabled
            ))
            # -- ANNOTATE MISMATCH IN EXTRA COLUMN:
            if annotate_column_id == 0:
                annotate_column_id = table.ensure_column_exists("MISMATCH!")
            row.cells[annotate_column_id] = "= %s" % actual_enabled
            mismatched_rows.append(row_index)

    # -- FINALLY: Ensure that there are no mismatched rows.
    assert_that(mismatched_rows, equal_to([]),
                "No mismatched rows: {}".format(mismatched_rows))

@step(u'unknown categories are ignored in active tags')
def step_unknown_categories_are_ignored_in_active_tags(ctx):
    ctx.active_tags_ignore_unknown_categories = True


@step(u'unknown categories are not ignored in active tags')
def step_unknown_categories_are_not_ignored_in_active_tags(ctx):
    ctx.active_tags_ignore_unknown_categories = False
