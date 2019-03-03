# -*- coding: utf-8 -*-
"""
Provides step definitions that test tag expressions (and tag logic).

.. code-block:: gherkin

    Given the default tags "-@foo"
    And   the tag expression "@foo"
    Then the tag expression selects elements with tags:
        | tags         | selected? |
        | @foo         |   yes     |
        | @other       |   no      |

.. code-block:: gherkin

    Given the named model elements with tags:
        | name | tags   |
        | S1   | @foo   |
    Then the tag expression select model elements with:
        | tag expression | selected?    |
        |  @foo          | S1, S3       |
        | -@foo          | S0, S2, S3   |
"""

from __future__ import absolute_import
from behave import given, then, register_type
from behave.tag_expression import make_tag_expression
from behave_model_util import convert_comma_list, convert_model_element_tags
from hamcrest import assert_that, equal_to


# -----------------------------------------------------------------------------
# TEST DOMAIN, FIXTURES, STEP UTILS:
# -----------------------------------------------------------------------------
class ModelElement(object):
    def __init__(self, name, tags=None):
        self.name = name
        self.tags = tags or []

# -----------------------------------------------------------------------------
# TYPE CONVERTERS:
# -----------------------------------------------------------------------------
def convert_tag_expression(text):
    return make_tag_expression(text.strip())
register_type(TagExpression=convert_tag_expression)


def convert_yesno(text):
    text = text.strip().lower()
    assert text in convert_yesno.choices
    return text in convert_yesno.true_choices
convert_yesno.choices = ("yes", "no", "true", "false")
convert_yesno.true_choices = ("yes", "true")


# -----------------------------------------------------------------------------
# STEP DEFINITIONS:
# -----------------------------------------------------------------------------
@given('the tag expression "{tag_expression:TagExpression}"')
def step_given_the_tag_expression(context, tag_expression):
    """
    Define a tag expression that is used later-on.

    .. code-block:: gherkin

        Given the tag expression "@foo"
    """
    context.tag_expression = tag_expression

@given('the default tags "{default_tags:TagExpression}"')
def step_given_the_tag_expression(context, default_tags):
    """
    Define a tag expression that is used later-on.

    .. code-block:: gherkin

        Given the tag expression "@foo"
    """
    context.default_tags = default_tags
    tag_expression = getattr(context, "tag_expression", None)
    if tag_expression is None:
        context.tag_expression = default_tags

@then('the tag expression selects elements with tags')
def step_then_tag_expression_selects_elements_with_tags(context):
    """
    Checks if a tag expression selects an element with the given tags.

    .. code-block:: gherkin
        Then the tag expression selects elements with tags:
            | tags         | selected? |
            | @foo         |   yes     |
            | @other       |   no      |
    """
    assert context.tag_expression, "REQUIRE: context.tag_expression"
    context.table.require_columns(["tags", "selected?"])
    tag_expression = context.tag_expression
    expected = []
    actual   = []
    for row in context.table.rows:
        element_tags = convert_model_element_tags(row["tags"])
        expected_element_selected = convert_yesno(row["selected?"])
        actual_element_selected = tag_expression.check(element_tags)
        expected.append((element_tags, expected_element_selected))
        actual.append((element_tags, actual_element_selected))

    # -- PERFORM CHECK:
    assert_that(actual, equal_to(expected))


@given('the model elements with name and tags')
def step_given_named_model_elements_with_tags(context):
    """
    .. code-block:: gherkin

        Given the model elements with name and tags:
            | name | tags   |
            | S1   | @foo   |
        Then the tag expression select model elements with:
            | tag expression | selected?    |
            |  @foo          | S1, S3       |
            | -@foo          | S0, S2, S3   |
    """
    assert context.table, "REQUIRE: context.table"
    context.table.require_columns(["name", "tags"])

    # -- PREPARE:
    model_element_names = set()
    model_elements = []
    for row in context.table.rows:
        name = row["name"].strip()
        tags = convert_model_element_tags(row["tags"])
        assert name not in model_element_names, "DUPLICATED: name=%s" % name
        model_elements.append(ModelElement(name, tags=tags))
        model_element_names.add(name)

    # -- SETUP:
    context.model_elements = model_elements


@then('the tag expression selects model elements with')
def step_given_named_model_elements_with_tags(context):
    """
    .. code-block:: gherkin

        Then the tag expression select model elements with:
            | tag expression | selected?    |
            |  @foo          | S1, S3       |
            | -@foo          | S0, S2, S3   |
    """
    assert context.model_elements, "REQUIRE: context attribute"
    assert context.table, "REQUIRE: context.table"
    context.table.require_columns(["tag expression", "selected?"])

    for row_index, row in enumerate(context.table.rows):
        tag_expression_text = row["tag expression"]
        tag_expression = convert_tag_expression(tag_expression_text)
        expected_selected_names = convert_comma_list(row["selected?"])

        actual_selected = []
        for model_element in context.model_elements:
            if tag_expression.check(model_element.tags):
                actual_selected.append(model_element.name)

        assert_that(actual_selected, equal_to(expected_selected_names),
            "tag_expression=%s (row=%s)" % (tag_expression_text, row_index))
