# -*- coding: UTF-8 -*-
"""

.. code-block:: gherkin

    Given I setup the current values for active tags with:
        | category | value |
        | foo      | xxx   |
    Then the following active tag combinations are enabled:
        | tags                        | enabled? |
        | @active.with_foo=xxx        | yes      |
        | @active.with_foo=other      | no       |

"""

from behave import given, when, then, step
from behave.tag_matcher import ActiveTagMatcher
from behave.tag_expression import TagExpression
from behave.userdata import parse_bool
from hamcrest import assert_that, equal_to


# -----------------------------------------------------------------------------
# UTILITY FUNCTIONS:
# -----------------------------------------------------------------------------
def normalize_tags(tags):
    # -- STRIP: Leading '@' from tags.
    return [TagExpression.normalize_tag(tag)  for tag in tags]


# -----------------------------------------------------------------------------
# STEP DEFINITIONS:
# -----------------------------------------------------------------------------
@given(u'I setup the current values for active tags with')
def step_given_setup_the_current_values_for_active_tags_with(context):
    assert context.table, "REQUIRE: table"
    context.table.require_columns(["category", "value"])

    active_values = getattr(context, "active_value_provider", None)
    if active_values is None:
        # -- SETUP DATA:
        context.active_value_provider = active_values = {}

    for row in context.table.rows:
        category = row["category"]
        value = row["value"]
        active_values[category] = value


@then(u'the following active tag combinations are enabled')
def step_then_following_active_tags_combinations_are_enabled(context):
    assert context.table, "REQUIRE: table"
    assert context.active_value_provider, "REQUIRE: active_value_provider"
    context.table.require_columns(["tags", "enabled?"])
    ignore_unknown_categories = getattr(context,
        "active_tags_ignore_unknown_categories",
        ActiveTagMatcher.ignore_unknown_categories)

    table = context.table
    annotate_column_id = 0
    active_tag_matcher = ActiveTagMatcher(context.active_value_provider)
    active_tag_matcher.ignore_unknown_categories = ignore_unknown_categories
    mismatched_rows = []
    for row_index, row in enumerate(table.rows):
        tags = normalize_tags(row["tags"].split())
        expected_enabled = parse_bool(row["enabled?"])
        actual_enabled = active_tag_matcher.should_run_with(tags)

        if actual_enabled != expected_enabled:
            # -- ANNOTATE MISMATCH IN EXTRA COLUMN:
            if annotate_column_id == 0:
                annotate_column_id = table.ensure_column_exists("MISMATCH!")
            row.cells[annotate_column_id] = "= %s" % actual_enabled
            mismatched_rows.append(row_index)

    # -- FINALLY: Ensure that there are no mismatched rows.
    assert_that(mismatched_rows, equal_to([]), "No mismatched rows:")


@step(u'unknown categories are ignored in active tags')
def step_unknown_categories_are_ignored_in_active_tags(context):
    context.active_tags_ignore_unknown_categories = True

@step(u'unknown categories are not ignored in active tags')
def step_unknown_categories_are_not_ignored_in_active_tags(context):
    context.active_tags_ignore_unknown_categories = False
