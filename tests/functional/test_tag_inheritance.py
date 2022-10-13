"""
Test the tag inheritance mechanism between model entities:

* Feature(s)
* Rule(s)
* ScenarioOutline(s)
* Scenario(s)

Tag inheritance mechanism:

* Inner model element inherits tags from its outer/parent elements
* Parametrized tags from a ScenarioOutline/ScenarioTemplate are filtered out

EXAMPLES:

* Scenario inherits the tags of its Feature
* Scenario inherits the tags of its Rule
* Scenario derives its tags of its ScenarioOutline (and Examples table)

* Rule inherits tags of its Feature
* ScenarioOutline/ScenarioTemplate inherits tags from its Feature
* ScenarioOutline/ScenarioTemplate inherits tags from its Rule
"""

from __future__ import absolute_import, print_function
from behave.parser import parse_feature
import pytest


# -----------------------------------------------------------------------------
# TEST SUPPORT
# -----------------------------------------------------------------------------
def get_inherited_tags(model_element):
    inherited_tags = set(model_element.effective_tags).difference(model_element.tags)
    return sorted(inherited_tags)   # -- ENSURE: Deterministic ordering


def assert_tags_same_as_effective_tags(model_element):
    assert set(model_element.tags) == set(model_element.effective_tags)


def assert_inherited_tags_equal_to(model_element, expected_tags):
    inherited_tags = get_inherited_tags(model_element)
    assert inherited_tags == expected_tags


def assert_no_tags_are_inherited(model_element):
    assert_inherited_tags_equal_to(model_element, [])


# -----------------------------------------------------------------------------
# TEST SUITE
# -----------------------------------------------------------------------------
class TestTagInheritance4Feature(object):
    """A Feature is the outermost model element.
    Therefore, it cannot inherit any features.
    """

    @pytest.mark.parametrize("tags, case", [
        ([], "without tags"),
        (["feature_tag1", "feature_tag2"], "with tags"),
    ])
    def test_no_inherited_tags(self, tags, case):
        tag_line = " ".join("@%s" % tag for tag in tags)
        text = u"""
            {tag_line}
            Feature: F1
            """.format(tag_line=tag_line)
        this_feature = parse_feature(text)
        assert this_feature.tags == tags
        assert this_feature.effective_tags == set(tags)
        assert_no_tags_are_inherited(this_feature)


class TestTagInheritance4Rule(object):
    def test_no_inherited_tags__without_feature_tags(self):
        text = u"""
        Feature: F1
          @rule_tag1
          Rule: R1
        """
        this_feature = parse_feature(text)
        this_rule = this_feature.rules[0]
        assert this_feature.tags == []
        assert this_rule.tags == ["rule_tag1"]
        assert_tags_same_as_effective_tags(this_rule)
        assert_no_tags_are_inherited(this_rule)

    def test_inherited_tags__with_feature_tags(self):
        text = u"""
        @feature_tag1 @feature_tag2
        Feature: F2
          @rule_tag1
          Rule: R2
        """
        this_feature = parse_feature(text)
        this_rule = this_feature.rules[0]
        expected_feature_tags = ["feature_tag1", "feature_tag2"]
        assert this_feature.tags == expected_feature_tags
        assert this_rule.tags == ["rule_tag1"]
        assert_inherited_tags_equal_to(this_rule, expected_feature_tags)

    def test_duplicated_tags_are_removed_from_inherited_tags(self):
        text = u"""
        @feature_tag1 @duplicated_tag
        Feature: F2
          @rule_tag1 @duplicated_tag
          Rule: R2
        """
        this_feature = parse_feature(text)
        this_rule = this_feature.rules[0]
        assert this_feature.tags == ["feature_tag1", "duplicated_tag"]
        assert this_rule.tags == ["rule_tag1", "duplicated_tag"]
        assert_inherited_tags_equal_to(this_rule, ["feature_tag1"])


class TestTagInheritance4ScenarioOutline(object):
    def test_no_inherited_tags__without_feature_tags(self):
        text = u"""
        Feature: F3
            @outline_tag1
            Scenario Outline: T1
        """
        this_feature = parse_feature(text)
        this_scenario_outline = this_feature.run_items[0]
        assert this_feature.tags == []
        assert this_scenario_outline.tags == ["outline_tag1"]
        assert_no_tags_are_inherited(this_scenario_outline)

    def test_no_inherited_tags__without_feature_and_rule_tags(self):
        text = u"""
        Feature: F3
          Rule: R3
            @outline_tag1
            Scenario Outline: T1
        """
        this_feature = parse_feature(text)
        this_rule = this_feature.rules[0]
        this_scenario_outline = this_rule.run_items[0]
        assert this_feature.tags == []
        assert this_rule.tags == []
        assert this_scenario_outline.tags == ["outline_tag1"]
        assert_no_tags_are_inherited(this_scenario_outline)

    def test_inherited_tags__with_feature_tags(self):
        text = u"""
        @feature_tag1 @feature_tag2
        Feature: F3
            @outline_tag1
            Scenario Outline: T3
        """
        this_feature = parse_feature(text)
        this_scenario_outline = this_feature.run_items[0]
        expected_feature_tags = ["feature_tag1", "feature_tag2"]
        assert this_feature.tags == expected_feature_tags
        assert this_scenario_outline.tags == ["outline_tag1"]
        assert_inherited_tags_equal_to(this_scenario_outline, expected_feature_tags)

    def test_inherited_tags__with_rule_tags(self):
        text = u"""
        Feature: F3
          @rule_tag1 @rule_tag2
          Rule: R3
            @outline_tag1
            Scenario Outline: T3
        """
        this_feature = parse_feature(text)
        this_rule = this_feature.rules[0]
        this_scenario_outline = this_rule.run_items[0]
        expected_rule_tags = ["rule_tag1", "rule_tag2"]
        assert this_feature.tags == []
        assert this_rule.tags == expected_rule_tags
        assert this_scenario_outline.tags == ["outline_tag1"]
        assert_inherited_tags_equal_to(this_scenario_outline, expected_rule_tags)

    def test_inherited_tags__with_feature_and_rule_tags(self):
        text = u"""
        @feature_tag1
        Feature: F3
          @rule_tag1 @rule_tag2
          Rule: R3
            @outline_tag1
            Scenario Outline: T3
        """
        this_feature = parse_feature(text)
        this_rule = this_feature.rules[0]
        this_scenario_outline = this_rule.run_items[0]
        expected_feature_tags = ["feature_tag1"]
        expected_rule_tags = ["rule_tag1", "rule_tag2"]
        expected_inherited_tags = ["feature_tag1", "rule_tag1", "rule_tag2"]
        assert this_feature.tags == expected_feature_tags
        assert this_rule.tags == expected_rule_tags
        assert this_scenario_outline.tags == ["outline_tag1"]
        assert_inherited_tags_equal_to(this_scenario_outline, expected_inherited_tags)

    def test_duplicated_tags_are_removed_from_inherited_tags(self):
        text = u"""
        @feature_tag1 @duplicated_tag
        Feature: F3
          @rule_tag1 @duplicated_tag
          Rule: R3
            @outline_tag1 @duplicated_tag
            Scenario Outline: T3
        """
        this_feature = parse_feature(text)
        this_rule = this_feature.rules[0]
        this_scenario_outline = this_rule.run_items[0]
        assert this_feature.tags == ["feature_tag1", "duplicated_tag"]
        assert this_rule.tags == ["rule_tag1", "duplicated_tag"]
        assert this_scenario_outline.tags == ["outline_tag1", "duplicated_tag"]
        assert_inherited_tags_equal_to(this_scenario_outline, ["feature_tag1", "rule_tag1"])


class TestTagInheritance4Scenario(object):
    def test_no_inherited_tags__without_feature_tags(self):
        text = u"""
        Feature: F4
            @scenario_tag1
            Scenario: S4
        """
        this_feature = parse_feature(text)
        this_scenario = this_feature.scenarios[0]
        assert this_feature.tags == []
        assert this_scenario.tags == ["scenario_tag1"]
        assert_no_tags_are_inherited(this_scenario)

    def test_no_inherited_tags__without_feature_and_rule_tags(self):
        text = u"""
        Feature: F4
          Rule: R4
            @scenario_tag1
            Scenario: S4
        """
        this_feature = parse_feature(text)
        this_rule = this_feature.rules[0]
        this_scenario = this_rule.scenarios[0]
        assert this_feature.tags == []
        assert this_rule.tags == []
        assert this_scenario.tags == ["scenario_tag1"]
        assert_no_tags_are_inherited(this_scenario)

    def test_inherited_tags__with_feature_tags(self):
        text = u"""
        @feature_tag1 @feature_tag2
        Feature: F4
            @scenario_tag1
            Scenario: S4
        """
        this_feature = parse_feature(text)
        this_scenario = this_feature.scenarios[0]
        expected_feature_tags = ["feature_tag1", "feature_tag2"]
        assert this_feature.tags == expected_feature_tags
        assert this_scenario.tags == ["scenario_tag1"]
        assert_inherited_tags_equal_to(this_scenario, expected_feature_tags)

    def test_inherited_tags__with_rule_tags(self):
        text = u"""
        Feature: F3
          @rule_tag1 @rule_tag2
          Rule: R3
            @scenario_tag1
            Scenario: S4
        """
        this_feature = parse_feature(text)
        this_rule = this_feature.rules[0]
        this_scenario = this_rule.scenarios[0]
        expected_rule_tags = ["rule_tag1", "rule_tag2"]
        assert this_feature.tags == []
        assert this_rule.tags == expected_rule_tags
        assert this_scenario.tags == ["scenario_tag1"]
        assert_inherited_tags_equal_to(this_scenario, expected_rule_tags)

    def test_inherited_tags__with_feature_and_rule_tags(self):
        text = u"""
        @feature_tag1
        Feature: F4
          @rule_tag1 @rule_tag2
          Rule: R4
            @scenario_tag1
            Scenario: S4
        """
        this_feature = parse_feature(text)
        this_rule = this_feature.rules[0]
        this_scenario = this_rule.scenarios[0]
        expected_feature_tags = ["feature_tag1"]
        expected_rule_tags = ["rule_tag1", "rule_tag2"]
        expected_inherited_tags = ["feature_tag1", "rule_tag1", "rule_tag2"]
        assert this_feature.tags == expected_feature_tags
        assert this_rule.tags == expected_rule_tags
        assert this_scenario.tags == ["scenario_tag1"]
        assert_inherited_tags_equal_to(this_scenario, expected_inherited_tags)

    def test_duplicated_tags_are_removed_from_inherited_tags(self):
        text = u"""
        @feature_tag1 @duplicated_tag
        Feature: F4
          @rule_tag1 @duplicated_tag
          Rule: R4
            @scenario_tag1 @duplicated_tag
            Scenario: S4
        """
        this_feature = parse_feature(text)
        this_rule = this_feature.rules[0]
        this_scenario = this_rule.scenarios[0]
        assert this_feature.tags == ["feature_tag1", "duplicated_tag"]
        assert this_rule.tags == ["rule_tag1", "duplicated_tag"]
        assert this_scenario.tags == ["scenario_tag1", "duplicated_tag"]
        assert_inherited_tags_equal_to(this_scenario, ["feature_tag1", "rule_tag1"])


class TestTagInheritance4ScenarioFromTemplate(object):
    """Test tag inheritance for scenarios from a ScenarioOutline or
    ScenarioTemplate (as alias for ScenarioOutline).

    SCENARIO TEMPLATE MECHANISM::

        scenario_template := scenario_outline
        scenario.tags := scenario_template.tags + scenario_template.examples[i].tags
    """

    def test_no_inherited_tags__without_feature_tags(self):
        text = u"""
        Feature: F5
            @template_tag1
            Scenario Outline: T5
              Given I meet "<name>"

              @examples_tag1
              Examples:
                | name |
                | Alice |
        """
        this_feature = parse_feature(text)
        this_scenario_outline = this_feature.run_items[0]
        this_scenario = this_scenario_outline.scenarios[0]
        assert this_feature.tags == []
        assert this_scenario_outline.tags == ["template_tag1"]
        assert this_scenario.tags == ["template_tag1", "examples_tag1"]
        assert_no_tags_are_inherited(this_scenario)

    def test_no_inherited_tags__without_feature_and_rule_tags(self):
        text = u"""
        Feature: F5
          Rule: R5
            @template_tag1
            Scenario Outline: T5
              Given I meet "<name>"

              @examples_tag1
              Examples:
                | name |
                | Alice |
        """
        this_feature = parse_feature(text)
        this_rule = this_feature.rules[0]
        this_scenario_outline = this_rule.run_items[0]
        this_scenario = this_scenario_outline.scenarios[0]
        assert this_feature.tags == []
        assert this_rule.tags == []
        assert this_scenario_outline.tags == ["template_tag1"]
        assert this_scenario.tags == ["template_tag1", "examples_tag1"]
        assert_no_tags_are_inherited(this_scenario)

    def test_inherited_tags__with_feature_tags(self):
        text = u"""
        @feature_tag1 @feature_tag2
        Feature: F5
            @template_tag1
            Scenario Outline: T5
              Given I meet "<name>"

              Examples:
                | name |
                | Alice |
        """
        this_feature = parse_feature(text)
        this_scenario_outline = this_feature.run_items[0]
        this_scenario = this_scenario_outline.scenarios[0]
        expected_feature_tags = ["feature_tag1", "feature_tag2"]
        assert this_feature.tags == expected_feature_tags
        assert this_scenario.tags == ["template_tag1"]
        assert_inherited_tags_equal_to(this_scenario, expected_feature_tags)

    def test_inherited_tags__with_rule_tags(self):
        text = u"""
        Feature: F5
          @rule_tag1 @rule_tag2
          Rule: R5

            @template_tag1
            Scenario Outline: T5
              Given I meet "<name>"

              Examples:
                | name |
                | Alice |
        """
        this_feature = parse_feature(text)
        this_rule = this_feature.rules[0]
        this_scenario_outline = this_feature.run_items[0]
        this_scenario = this_scenario_outline.scenarios[0]
        expected_rule_tags = ["rule_tag1", "rule_tag2"]
        assert this_feature.tags == []
        assert this_rule.tags == expected_rule_tags
        assert this_scenario.tags == ["template_tag1"]
        assert_inherited_tags_equal_to(this_scenario, expected_rule_tags)

    def test_inherited_tags__with_feature_and_rule_tags(self):
        text = u"""
        @feature_tag1
        Feature: F4
          @rule_tag1 @rule_tag2
          Rule: R4

            @template_tag1
            Scenario Outline: T5
              Given I meet "<name>"

              Examples:
                | name |
                | Alice |
        """
        this_feature = parse_feature(text)
        this_rule = this_feature.rules[0]
        this_scenario_outline = this_rule.run_items[0]
        this_scenario = this_scenario_outline.scenarios[0]

        expected_feature_tags = ["feature_tag1"]
        expected_rule_tags = ["rule_tag1", "rule_tag2"]
        expected_inherited_tags = expected_feature_tags + expected_rule_tags
        assert this_feature.tags == expected_feature_tags
        assert this_rule.tags == expected_rule_tags
        assert this_scenario.tags == ["template_tag1"]
        assert_inherited_tags_equal_to(this_scenario, expected_inherited_tags)

    def test_tags_are_derived_from_template(self):
        text = u"""
        Feature: F5

            @template_tag1 @param_name_<name>
            Scenario Outline: T5
              Given I meet "<name>"

              Examples:
                | name |
                | Alice |
        """
        this_feature = parse_feature(text)
        this_scenario_template = this_feature.run_items[0]
        this_scenario = this_scenario_template.scenarios[0]

        assert this_feature.tags == []
        assert this_scenario_template.tags == ["template_tag1", "param_name_<name>"]
        assert this_scenario.tags == ["template_tag1", "param_name_Alice"]
        assert_no_tags_are_inherited(this_scenario)

    def test_tags_are_derived_from_template_examples_for_table_row(self):
        text = u"""
        Feature: F5
          Rule: R5
            Scenario Outline: T5
              Given I meet "<name>"

              @examples_tag1
              Examples:
                | name |
                | Alice |
        """
        this_feature = parse_feature(text)
        this_rule = this_feature.rules[0]
        this_scenario_outline = this_rule.run_items[0]
        this_scenario = this_scenario_outline.scenarios[0]

        assert this_feature.tags == []
        assert this_scenario.tags == ["examples_tag1"]
        assert_no_tags_are_inherited(this_scenario)

    def test_duplicated_tags_are_removed_from_inherited_tags(self):
        text = u"""
        @feature_tag1 @duplicated_tag
        Feature: F4
          @rule_tag1 @duplicated_tag
          Rule: R4

            @template_tag1 @duplicated_tag
            Scenario Outline: T5
              Given I meet "<name>"

              @examples_tag1
              Examples:
                | name |
                | Alice |
        """
        this_feature = parse_feature(text)
        this_rule = this_feature.rules[0]
        this_scenario_template = this_rule.scenarios[0]
        this_scenario = this_scenario_template.scenarios[0]
        assert this_feature.tags == ["feature_tag1", "duplicated_tag"]
        assert this_rule.tags == ["rule_tag1", "duplicated_tag"]
        assert this_scenario.tags == ["template_tag1", "duplicated_tag", "examples_tag1"]
        assert_inherited_tags_equal_to(this_scenario, ["feature_tag1", "rule_tag1"])
