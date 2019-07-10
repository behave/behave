# -*- coding: UTF-8 -*-
"""
Tests for Gherkin parser with `Gherkin v6 grammar`_.

Gherkin v6 grammar extensions:

* Rule keyword added
* Aliases for Scenario, ScenarioOutline to better correspond to `Example Mapping`_

A Rule (or: business rule) allows to group multiple Scenarios::

    # -- RULE GRAMMAR PSEUDO-CODE:
    @tag1 @tag2
    Rule: Optional Rule Title...
        Description?        #< CARDINALITY: 0..1 (optional)
        Background?         #< CARDINALITY: 0..1 (optional)
        Scenario*           #< CARDINALITY: 0..N (many)
        ScenarioOutline*    #< CARDINALITY: 0..N (many)

Keyword aliases:

    | Concept          | Gherkin v6         | Alias (Gherkin v5) |
    | Scenario         | Example            | Scenario           |
    | Scenario Outline | Scenario Template  | Scenario Outline   |

.. seealso::

    * :class:~behave.parser:Parser`
    * `Gherkin v6 grammar`_

    EXAMPLE MAPPING:

    * Cucumber: `Example Mapping`_
    * Cucumber: `Example Mapping Webinar`_
    * https://docs.cucumber.io/bdd/example-mapping/
    * https://www.agilealliance.org/resources/sessions/example-mapping/

.. _`Gherkin v6 grammar`: https://github.com/cucumber/cucumber/blob/master/gherkin/gherkin.berp
.. _`Example Mapping`: https://cucumber.io/blog/example-mapping-introduction/
.. _`Example Mapping Webinar`: https://cucumber.io/blog/example-mapping-webinar/
"""

from __future__ import absolute_import, print_function
from behave.parser import (
    parse_feature, parse_rule, Parser, ParserError
)
from behave.model import Feature, Rule, Scenario, ScenarioOutline, Background
import pytest


# ---------------------------------------------------------------------------
# TEST SUPPORT
# ---------------------------------------------------------------------------
def assert_compare_steps(steps, expected):
    have = [(s.step_type, s.keyword.strip(), s.name, s.text, s.table) for s in steps]
    assert have == expected


# ---------------------------------------------------------------------------
# TEST SUITE
# ---------------------------------------------------------------------------

class TestGherkin6Parser(object):
    pass


class TestParser4Rule(object):

    @pytest.mark.smoke
    def test_parses_rule(self):
        text = u'''
Feature: With Rule

  A feature description line 1.
  A feature description line 2.

  Rule: R1
    Background: R1.Background_1
      Given background step 1
      When background step 2

    Scenario: R1.Scenario_1
      Given scenario step 1
      When scenario step 2
      Then scenario step 3
'''.lstrip()
        feature = parse_feature(text)
        rule1 = feature.rules[0]
        rule1_scenario1 = rule1.scenarios[0]

        assert feature.name == "With Rule"
        assert feature.description == [
            "A feature description line 1.",
            "A feature description line 2.",
        ]
        assert feature.background is None

        assert len(feature.rules) == 1
        assert len(feature.scenarios) == 0
        assert rule1.name == "R1"
        assert rule1.tags == []
        assert rule1.parent is feature
        assert rule1.feature is feature
        assert rule1.background is not None
        assert_compare_steps(rule1.background.steps, [
            ("given", "Given", "background step 1", None, None),
            ("when", "When", "background step 2", None, None),
        ])

        assert len(rule1.scenarios) == 1
        assert rule1_scenario1.background is rule1.background
        assert_compare_steps(rule1_scenario1.steps, [
            ("given", "Given", "scenario step 1", None, None),
            ("when", "When", "scenario step 2", None, None),
            ("then", "Then", "scenario step 3", None, None),
        ])
        assert_compare_steps(rule1_scenario1.all_steps, [
            ("given", "Given", "background step 1", None, None),
            ("when", "When", "background step 2", None, None),
            ("given", "Given", "scenario step 1", None, None),
            ("when", "When", "scenario step 2", None, None),
            ("then", "Then", "scenario step 3", None, None),
        ])

    def test_parses_rule_with_tags(self):
        text = u'''
Feature: With Rule

  @rule_tag1
  @rule_tag2 @rule_tag3
  Rule: R2
'''.lstrip()
        feature = parse_feature(text)
        rule1 = feature.rules[0]

        assert feature.name == "With Rule"
        assert feature.background is None
        assert len(feature.rules) == 1
        assert len(feature.scenarios) == 0

        assert rule1.name == "R2"
        assert rule1.tags == ["rule_tag1", "rule_tag2", "rule_tag3"]
        assert rule1.description == []
        assert rule1.background is None
        assert len(rule1.scenarios) == 0

    def test_parses_rule_with_description(self):
        text = u'''
Feature: With Rule

  Rule: R3
    Rule description line 1.
    Rule description line 2.
    
    Rule description line 3.
'''.lstrip()
        feature = parse_feature(text)
        rule1 = feature.rules[0]

        assert feature.name == "With Rule"
        assert feature.background is None
        assert len(feature.rules) == 1
        assert len(feature.scenarios) == 0

        assert rule1.name == "R3"
        assert rule1.description == [
            "Rule description line 1.",
            "Rule description line 2.",
            "Rule description line 3.",
            # -- HINT: EMPTY-LINES are ignored.
        ]
        assert rule1.tags == []
        assert rule1.background is None
        assert len(rule1.scenarios) == 0

    def test_parses_rule_with_background(self):
        text = u'''
Feature: With Rule

  Rule: R3
    Background: R3.Background
      Given background step 1
      When background step 2
'''.lstrip()
        feature = parse_feature(text)
        rule1 = feature.rules[0]

        assert feature.name == "With Rule"
        assert feature.background is None
        assert len(feature.rules) == 1
        assert len(feature.scenarios) == 0

        assert rule1.name == "R3"
        assert rule1.description == []
        assert rule1.tags == []
        assert len(rule1.scenarios) == 0
        assert rule1.background is not None
        assert_compare_steps(rule1.background.steps, [
            ("given", "Given", "background step 1", None, None),
            ("when", "When", "background step 2", None, None),
        ])

    def test_parses_rule_without_background_should_inherit_feature_background(self):
        """If a Rule has no Background,
        it inherits the Feature's Background (if one exists).
        """
        text = u'''
Feature: With Rule
  Background: Feature.Background
    Given feature background step 1
    When  feature background step 2

  Rule: R3A
    Scenario: R3A.Scenario_1
      Given scenario step 1
      When scenario step 2
'''.lstrip()
        feature = parse_feature(text)
        rule1 = feature.rules[0]

        assert feature.name == "With Rule"
        assert feature.background is not None
        assert len(feature.rules) == 1
        assert len(feature.scenarios) == 0

        assert rule1.name == "R3A"
        assert rule1.description == []
        assert rule1.tags == []
        assert len(rule1.scenarios) == 1
        assert rule1.background is not feature.background
        assert rule1.background.inherited_steps == feature.background.steps
        assert list(rule1.background.all_steps) == feature.background.steps
        assert_compare_steps(rule1.scenarios[0].all_steps, [
            ("given", "Given", "feature background step 1", None, None),
            ("when", "When", "feature background step 2", None, None),
            ("given", "Given", "scenario step 1", None, None),
            ("when", "When", "scenario step 2", None, None),
        ])

    def test_parses_rule_with_background_inherits_feature_background(self):
        """If a Rule has no Background,
        it inherits the Feature's Background (if one exists).
        """
        text = u'''
Feature: With Rule
  Background: Feature.Background
    Given feature background step 1
    When  feature background step 2

  Rule: R3B
    Background: Rule_R3B.Background
      Given rule background step 1
      When  rule background step 2

    Scenario: R3B.Scenario_1
      Given scenario step 1
      When scenario step 2
'''.lstrip()
        feature = parse_feature(text)
        rule1 = feature.rules[0]

        assert feature.name == "With Rule"
        assert feature.background is not None
        assert len(feature.rules) == 1
        assert len(feature.scenarios) == 0

        assert rule1.name == "R3B"
        assert rule1.description == []
        assert rule1.tags == []
        assert len(rule1.scenarios) == 1
        assert rule1.background is not None
        assert rule1.background is not feature.background
        assert_compare_steps(rule1.scenarios[0].all_steps, [
            ("given", "Given", "feature background step 1", None, None),
            ("when",  "When",  "feature background step 2", None, None),
            ("given", "Given", "rule background step 1", None, None),
            ("when",  "When",  "rule background step 2", None, None),
            ("given", "Given", "scenario step 1", None, None),
            ("when",  "When",  "scenario step 2", None, None),
        ])

    def test_parses_rule_with_empty_background_inherits_feature_background(self):
        """A Rule has empty Background (without any steps) prevents that
        Feature Background is inherited (if one exists).
        """
        text = u'''
Feature: With Rule
  Background: Feature.Background
    Given feature background step 1
    When  feature background step 2

  Rule: R3C
    Background: Rule_R3C.Empty_Background

    Scenario: R3B.Scenario_1
      Given scenario step 1
      When scenario step 2
'''.lstrip()
        feature = parse_feature(text)
        rule1 = feature.rules[0]

        assert feature.name == "With Rule"
        assert feature.background is not None
        assert len(feature.rules) == 1
        assert len(feature.scenarios) == 0

        assert rule1.name == "R3C"
        assert rule1.description == []
        assert rule1.tags == []
        assert len(rule1.scenarios) == 1
        assert rule1.background is not None
        assert rule1.background is not feature.background
        assert rule1.background.name == "Rule_R3C.Empty_Background"
        assert_compare_steps(rule1.scenarios[0].all_steps, [
            ("given", "Given", "feature background step 1", None, None),
            ("when",  "When",  "feature background step 2", None, None),
            ("given", "Given", "scenario step 1", None, None),
            ("when",  "When", "scenario step 2", None, None),
        ])

    def test_parses_rule_with_scenario(self):
        text = u'''
Feature: With Rule

  Rule: R4
    Scenario: R4.Scenario_1
      Given scenario step 1
      When scenario step 2
'''.lstrip()
        feature = parse_feature(text)
        rule1 = feature.rules[0]
        rule1_scenario1 = rule1.scenarios[0]

        assert feature.name == "With Rule"
        assert feature.background is None
        assert len(feature.rules) == 1
        assert len(feature.scenarios) == 0

        assert rule1.name == "R4"
        assert rule1.description == []
        assert rule1.tags == []
        assert rule1.background is None
        assert len(rule1.scenarios) == 1
        assert rule1_scenario1.name == "R4.Scenario_1"
        assert_compare_steps(rule1_scenario1.steps, [
            ("given", "Given", "scenario step 1", None, None),
            ("when", "When", "scenario step 2", None, None),
        ])

    def test_parses_rule_with_two_scenarios(self):
        text = u'''
Feature: With Rule

  Rule: R4
    Scenario: R4.Scenario_1
      Given scenario 1 step 1
      When scenario 1 step 2

    Scenario: R4.Scenario_2
      Given scenario 2 step 1
      When scenario 2 step 2
'''.lstrip()
        feature = parse_feature(text)
        rule1 = feature.rules[0]
        rule1_scenario1 = rule1.scenarios[0]
        rule1_scenario2 = rule1.scenarios[1]

        assert feature.name == "With Rule"
        assert feature.background is None
        assert len(feature.rules) == 1
        assert len(feature.scenarios) == 0

        assert rule1.name == "R4"
        assert rule1.description == []
        assert rule1.tags == []
        assert rule1.background is None
        assert len(rule1.scenarios) == 2
        assert rule1_scenario1.name == "R4.Scenario_1"
        assert rule1_scenario1.parent is rule1
        assert rule1_scenario1.feature is feature
        assert_compare_steps(rule1_scenario1.steps, [
            ("given", "Given", "scenario 1 step 1", None, None),
            ("when", "When", "scenario 1 step 2", None, None),
        ])

        assert rule1_scenario2.name == "R4.Scenario_2"
        assert rule1_scenario2.parent is rule1
        assert rule1_scenario2.feature is feature
        assert_compare_steps(rule1_scenario2.steps, [
            ("given", "Given", "scenario 2 step 1", None, None),
            ("when", "When", "scenario 2 step 2", None, None),
        ])

    def test_parses_rule_with_scenario_outline(self):
        text = u'''
Feature: With Rule

  Rule: R5
    Scenario Outline: R5.ScenarioOutline
      Given step with name "<name>"
      When step uses "<param2>"
      
      Examples:
        | name  | param2 |
        | Alice | 1      |
        | Bob   | 2      |
'''.lstrip()
        feature = parse_feature(text)
        rule1 = feature.rules[0]
        rule1_scenario1 = rule1.scenarios[0]

        assert feature.name == "With Rule"
        assert feature.background is None
        assert len(feature.rules) == 1
        assert len(feature.scenarios) == 0

        assert rule1.name == "R5"
        assert rule1.description == []
        assert rule1.tags == []
        assert rule1.background is None
        assert len(rule1.scenarios) == 1
        assert len(rule1.scenarios[0].scenarios) == 2
        assert_compare_steps(rule1_scenario1.scenarios[0].steps, [
            ("given", "Given", 'step with name "Alice"', None, None),
            ("when", "When", 'step uses "1"', None, None),
        ])
        assert_compare_steps(rule1_scenario1.scenarios[1].steps, [
            ("given", "Given", 'step with name "Bob"', None, None),
            ("when", "When", 'step uses "2"', None, None),
        ])

    def test_parses_rule_with_two_scenario_outlines(self):
        text = u'''
Feature: With Rule

  Rule: R5
    Scenario Outline: R5.ScenarioOutline_1
      Given step with name "<name>"
      When step uses "<param2>"

      Examples:
        | name  | param2 |
        | Alice | 1      |
        | Bob   | 2      |

    Scenario Outline: R5.ScenarioOutline_2
      Given step with name "<name>"

      Examples:
        | name    |
        | Charly  |
        | Dorothy |
'''.lstrip()
        feature = parse_feature(text)
        rule1 = feature.rules[0]
        rule1_scenario1 = rule1.scenarios[0]
        rule1_scenario2 = rule1.scenarios[1]

        assert feature.name == "With Rule"
        assert feature.background is None
        assert len(feature.rules) == 1
        assert len(feature.scenarios) == 0

        assert rule1.name == "R5"
        assert rule1.description == []
        assert rule1.tags == []
        assert rule1.background is None
        assert len(rule1.scenarios) == 2
        assert len(rule1_scenario1.scenarios) == 2
        assert rule1_scenario1.scenarios[0].name == "R5.ScenarioOutline_1 -- @1.1 "
        assert rule1_scenario1.scenarios[0].parent is rule1_scenario1
        assert rule1_scenario1.scenarios[0].feature is feature
        assert_compare_steps(rule1_scenario1.scenarios[0].steps, [
            ("given", "Given", 'step with name "Alice"', None, None),
            ("when", "When", 'step uses "1"', None, None),
        ])
        assert rule1_scenario1.scenarios[1].name == "R5.ScenarioOutline_1 -- @1.2 "
        assert rule1_scenario1.scenarios[0].parent is rule1_scenario1
        assert rule1_scenario1.scenarios[0].feature is feature
        assert_compare_steps(rule1_scenario1.scenarios[1].steps, [
            ("given", "Given", 'step with name "Bob"', None, None),
            ("when", "When", 'step uses "2"', None, None),
        ])

        assert len(rule1_scenario2.scenarios) == 2
        assert rule1_scenario2.scenarios[0].name == "R5.ScenarioOutline_2 -- @1.1 "
        assert rule1_scenario2.scenarios[0].parent is rule1_scenario2
        assert rule1_scenario2.scenarios[0].feature is feature
        assert_compare_steps(rule1_scenario2.scenarios[0].steps, [
            ("given", "Given", 'step with name "Charly"', None, None),
        ])
        assert rule1_scenario2.scenarios[1].name == "R5.ScenarioOutline_2 -- @1.2 "
        assert rule1_scenario2.scenarios[1].parent is rule1_scenario2
        assert rule1_scenario2.scenarios[1].feature is feature
        assert_compare_steps(rule1_scenario2.scenarios[1].steps, [
            ("given", "Given", 'step with name "Dorothy"', None, None),
        ])

    def test_parses_two_rules(self):
        text = u'''
Feature: With Rule

  Rule: R1
    Scenario: R1.Scenario_1
      Given scenario 1 step 1
      When scenario 1 step 2
  
  Rule: R2
    Scenario Outline: R2.ScenarioOutline_1
      Given step with name "<name>"
      When step uses "<param2>"
      
      Examples:
        | name  | param2 |
        | Alice | 1      |
        | Bob   | 2      |
'''.lstrip()
        feature = parse_feature(text)
        rule1 = feature.rules[0]
        rule2 = feature.rules[1]
        rule1_scenario1 = rule1.scenarios[0]
        rule2_scenario1 = rule2.scenarios[0]

        assert feature.name == "With Rule"
        assert feature.background is None
        assert len(feature.rules) == 2
        assert len(feature.scenarios) == 0

        assert rule1.name == "R1"
        assert rule1.parent is feature
        assert rule1.feature is feature
        assert rule1.description == []
        assert rule1.tags == []
        assert rule1.background is None
        assert len(rule1.scenarios) == 1
        assert rule1_scenario1.name == "R1.Scenario_1"
        assert rule1_scenario1.parent is rule1
        assert rule1_scenario1.feature is feature
        assert_compare_steps(rule1_scenario1.steps, [
            ("given", "Given", 'scenario 1 step 1', None, None),
            ("when", "When", 'scenario 1 step 2', None, None),
        ])

        assert rule2.name == "R2"
        assert rule2.parent is feature
        assert rule2.feature is feature
        assert rule2.description == []
        assert rule2.tags == []
        assert rule2.background is None
        assert len(rule2.scenarios) == 1
        assert len(rule2.scenarios[0].scenarios) == 2
        assert rule2_scenario1.scenarios[0].name == "R2.ScenarioOutline_1 -- @1.1 "
        assert rule2_scenario1.scenarios[0].parent is rule2_scenario1
        assert rule2_scenario1.scenarios[0].feature is feature
        assert_compare_steps(rule2_scenario1.scenarios[0].steps, [
        ("given", "Given", 'step with name "Alice"', None, None),
            ("when", "When", 'step uses "1"', None, None),
        ])
        assert rule2_scenario1.scenarios[1].name == "R2.ScenarioOutline_1 -- @1.2 "
        assert rule2_scenario1.scenarios[1].parent is rule2_scenario1
        assert rule2_scenario1.scenarios[1].feature is feature
        assert_compare_steps(rule2_scenario1.scenarios[1].steps, [
            ("given", "Given", 'step with name "Bob"', None, None),
            ("when", "When", 'step uses "2"', None, None),
        ])

    # @check.duplicated
    def test_parse_background_scenario_and_rules(self):
        """HINT: Some Scenarios may exist before the first Rule."""
        text = u'''
Feature: With Scenarios and Rules

  Background: Feature.Background
    Given feature background step_1
    When  feature background step_2

  Scenario: Scenario_1
    Given scenario_1 step_1
    When  scenario_1 step_2
    
  Rule: R1
    Background: R1.Background
      Given rule R1 background step_1
      
    Scenario: R1.Scenario_1
      Given rule R1 scenario_1 step_1
      When  rule R1 scenario_1 step_2

  Rule: R2
    Scenario: R2.Scenario_1
      Given rule R2 scenario_1 step_1
      When  rule R2 scenario_1 step_2
'''.lstrip()
        feature = parse_feature(text)
        assert feature.name == "With Scenarios and Rules"
        assert feature.background is not None
        assert len(feature.scenarios) == 1
        assert len(feature.rules) == 2
        assert len(feature.run_items) == 3

        scenario1 = feature.scenarios[0]
        rule1 = feature.rules[0]
        rule2 = feature.rules[1]
        rule1_scenario1 = rule1.scenarios[0]
        rule2_scenario1 = rule2.scenarios[0]

        assert feature.run_items == [scenario1, rule1, rule2]

        assert scenario1.name == "Scenario_1"
        assert scenario1.background is feature.background
        assert scenario1.parent is feature
        assert scenario1.feature is feature
        assert scenario1.tags == []
        assert scenario1.description == []
        assert_compare_steps(scenario1.all_steps, [
            (u"given", u"Given", u'feature background step_1', None, None),
            (u"when", u"When",   u'feature background step_2', None, None),
            (u"given", u"Given", u'scenario_1 step_1', None, None),
            (u"when", u"When",   u'scenario_1 step_2', None, None),
        ])

        assert rule1.name == "R1"
        assert rule1.parent is feature
        assert rule1.feature is feature
        assert rule1.description == []
        assert rule1.tags == []
        assert rule1.background is not None
        assert len(rule1.scenarios) == 1
        assert rule1_scenario1.name == "R1.Scenario_1"
        assert rule1_scenario1.parent is rule1
        assert rule1_scenario1.feature is feature
        assert_compare_steps(rule1_scenario1.all_steps, [
            ("given", "Given", 'feature background step_1', None, None),
            ("when",  "When",  'feature background step_2', None, None),
            ("given", "Given", 'rule R1 background step_1', None, None),
            ("given", "Given", 'rule R1 scenario_1 step_1', None, None),
            ("when",  "When",  'rule R1 scenario_1 step_2', None, None),
        ])

        assert rule2.name == "R2"
        assert rule2.parent is feature
        assert rule2.feature is feature
        assert rule2.description == []
        assert rule2.tags == []
        assert rule2.background is not feature.background
        assert list(rule2.background.inherited_steps) == list(feature.background.steps)
        assert list(rule2.background.all_steps) == list(feature.background.steps)
        assert len(rule2.scenarios) == 1
        assert rule2_scenario1.name == "R2.Scenario_1"
        assert rule2_scenario1.parent is rule2
        assert rule2_scenario1.feature is feature
        assert_compare_steps(rule2_scenario1.all_steps, [
            ("given", "Given", 'feature background step_1', None, None),
            ("when",  "When",  'feature background step_2', None, None),
            ("given", "Given", 'rule R2 scenario_1 step_1', None, None),
            ("when",  "When",  'rule R2 scenario_1 step_2', None, None),
        ])


# ---------------------------------------------------------------------------
# TEST SUITE: Verify Feature Background to Rule Background Inheritance
# ---------------------------------------------------------------------------
class TestParser4Background(object):
    """Verify feature.background to rule.background inheritance, etc."""

    def test_parse__norule_scenarios_use_feature_background(self):
        """AFFECTED: Scenarios outside of rules (before first rule)."""
        text = u'''
            Feature: With Scenarios and Rules
            
              Background: Feature.Background
                Given feature background step_1
            
              Scenario: Scenario_1
                Given scenario_1 step_1
            
              Rule: R1
                Scenario: R1.Scenario_1
                  Given rule R1 scenario_1 step_1
            '''.lstrip()
        feature = parse_feature(text)
        assert feature.name == "With Scenarios and Rules"
        assert feature.background is not None
        assert len(feature.scenarios) == 1
        assert len(feature.rules) == 1
        assert len(feature.run_items) == 2

        scenario1 = feature.scenarios[0]
        rule1 = feature.rules[0]
        assert feature.run_items == [scenario1, rule1]

        assert scenario1.name == "Scenario_1"
        assert scenario1.background is feature.background
        assert scenario1.background_steps == feature.background.steps
        assert_compare_steps(scenario1.all_steps, [
            (u"given", u"Given", u'feature background step_1', None, None),
            (u"given", u"Given", u'scenario_1 step_1', None, None),
        ])

    def test_parse__norule_scenarios_with_disabled_background(self):
        """AFFECTED: Scenarios outside of rules (before first rule)."""
        text = u'''
            Feature: Scenario with disabled background
            
              Background: Feature.Background
                Given feature background step_1
            
              @fixture.behave.disable_background
              Scenario: Scenario_1
                Given scenario_1 step_1
            
              Scenario: Scenario_2
                Given scenario_2 step_1
            '''.lstrip()
        feature = parse_feature(text)
        assert feature.name == "Scenario with disabled background"
        assert feature.background is not None
        assert len(feature.scenarios) == 2
        assert len(feature.run_items) == 2

        scenario1 = feature.scenarios[0]
        scenario2 = feature.scenarios[1]
        assert feature.run_items == [scenario1, scenario2]

        scenario1.use_background = False    # -- FIXTURE-EFFECT (simulated)
        assert scenario1.name == "Scenario_1"
        assert scenario1.background is feature.background
        assert scenario1.background_steps != feature.background.steps
        assert scenario1.background_steps == []
        assert_compare_steps(scenario1.all_steps, [
            (u"given", u"Given", u'scenario_1 step_1', None, None),
        ])

        # -- ENSURE: Disabling of background has no effect on other scenarios.
        assert scenario2.name == "Scenario_2"
        assert scenario2.background is feature.background
        assert scenario2.background_steps == feature.background.steps
        assert_compare_steps(scenario2.all_steps, [
            (u"given", u"Given", u'feature background step_1', None, None),
            (u"given", u"Given", u'scenario_2 step_1', None, None),
        ])

    def test_parse__rule_scenarios_inherit_feature_background_without_rule_background(self):
        text = u'''
            Feature: With Background and Rule
    
              Background: Feature.Background
                Given feature background step_1
    
              Rule: R1
                Scenario: R1.Scenario_1
                  Given rule R1 scenario_1 step_1
            '''.lstrip()
        feature = parse_feature(text)
        assert feature.name == "With Background and Rule"
        assert feature.background is not None
        assert len(feature.scenarios) == 0
        assert len(feature.rules) == 1
        assert len(feature.run_items) == 1

        rule1 = feature.rules[0]
        rule1_scenario1 = rule1.scenarios[0]
        assert feature.run_items == [rule1]

        assert rule1_scenario1.name == "R1.Scenario_1"
        assert rule1_scenario1.background is not None
        # assert rule1_scenario1.background is not feature.background
        assert rule1_scenario1.background_steps == feature.background.steps
        assert_compare_steps(rule1_scenario1.all_steps, [
            (u"given", u"Given", u'feature background step_1', None, None),
            (u"given", u"Given", u'rule R1 scenario_1 step_1', None, None),
        ])

    def test_parse__rule_scenarios_inherit_feature_background_with_rule_background(self):
        text = u'''
            Feature: With Feature.Background and Rule.Background

              Background: Feature.Background
                Given feature background step_1

              Rule: R1
                Background: R1.Background
                  Given rule R1 background step_1
                
                Scenario: R1.Scenario_1
                  Given rule R1 scenario_1 step_1
            '''.lstrip()
        feature = parse_feature(text)
        assert feature.name == "With Feature.Background and Rule.Background"
        assert feature.background is not None
        assert len(feature.scenarios) == 0
        assert len(feature.rules) == 1
        assert len(feature.run_items) == 1

        rule1 = feature.rules[0]
        rule1_scenario1 = rule1.scenarios[0]
        assert feature.run_items == [rule1]

        assert rule1.background is not None
        assert rule1.background is not feature.background
        assert rule1.background.inherited_steps == feature.background.steps
        assert list(rule1.background.all_steps) != feature.background.steps

        assert rule1_scenario1.name == "R1.Scenario_1"
        assert rule1_scenario1.background is rule1.background
        assert rule1_scenario1.background_steps == list(rule1.background.all_steps)
        assert_compare_steps(rule1_scenario1.all_steps, [
            (u"given", u"Given", u'feature background step_1', None, None),
            (u"given", u"Given", u'rule R1 background step_1', None, None),
            (u"given", u"Given", u'rule R1 scenario_1 step_1', None, None),
        ])

    def test_parse__rule_scenarios_with_rule_background_when_background_inheritance_is_disabled(self):
        # -- HINT: Background inheritance is enabled (by default).
        text = u'''
            Feature: With Feature Background Inheritance disabled

              Background: Feature.Background
                Given feature background step_1

              @fixture.behave.override_background
              Rule: R1
                Background: R1.Background
                  Given rule R1 background step_1

                Scenario: R1.Scenario_1
                  Given rule R1 scenario_1 step_1
            '''.lstrip()
        feature = parse_feature(text)
        assert feature.name == "With Feature Background Inheritance disabled"
        assert feature.background is not None
        assert len(feature.scenarios) == 0
        assert len(feature.rules) == 1
        assert len(feature.run_items) == 1

        rule1 = feature.rules[0]
        rule1_scenario1 = rule1.scenarios[0]
        assert feature.run_items == [rule1]

        rule1.use_background_inheritance = False  # FIXTURE-EFFECT (simulated)
        assert rule1.background is not None
        assert rule1.background.use_inheritance is False
        assert rule1.background is not feature.background
        assert rule1.background.inherited_steps == []
        assert rule1.background.inherited_steps != feature.background.steps
        assert list(rule1.background.all_steps) != feature.background.steps

        assert rule1_scenario1.name == "R1.Scenario_1"
        assert rule1_scenario1.background is rule1.background
        assert rule1_scenario1.background_steps == rule1.background.steps
        assert rule1_scenario1.background_steps == list(rule1.background.all_steps)
        assert_compare_steps(rule1_scenario1.all_steps, [
            (u"given", u"Given", u'rule R1 background step_1', None, None),
            (u"given", u"Given", u'rule R1 scenario_1 step_1', None, None),
        ])

    def test_parse__rule_scenarios_without_rule_background_when_background_inheritance_is_disabled_without(self):
        # -- HINT: Background inheritance is enabled (by default).
        text = u'''
            Feature: With Feature Background Inheritance disabled

              Background: Feature.Background
                Given feature background step_1

              @fixture.behave.override_background
              Rule: R1
                Scenario: R1.Scenario_1
                  Given rule R1 scenario_1 step_1
            '''.lstrip()
        feature = parse_feature(text)
        assert feature.name == "With Feature Background Inheritance disabled"
        assert feature.background is not None
        assert len(feature.scenarios) == 0
        assert len(feature.rules) == 1
        assert len(feature.run_items) == 1

        rule1 = feature.rules[0]
        rule1_scenario1 = rule1.scenarios[0]
        assert feature.run_items == [rule1]

        rule1.use_background_inheritance = False  # FIXTURE-EFFECT (simulated)
        assert rule1.background is not None
        assert rule1.background.use_inheritance is False
        assert rule1.background is not feature.background
        assert rule1.background.inherited_steps == []

        assert rule1_scenario1.name == "R1.Scenario_1"
        assert rule1_scenario1.background is rule1.background
        assert rule1_scenario1.background_steps == rule1.background.steps
        assert rule1_scenario1.background_steps == list(rule1.background.all_steps)
        assert_compare_steps(rule1_scenario1.all_steps, [
            (u"given", u"Given", u'rule R1 scenario_1 step_1', None, None),
        ])

    def test_parse__rule_scenarios_without_feature_background_and_with_rule_background(self):
        text = u'''
            Feature: Without Feature.Background and with Rule.Background

              Rule: R1
                Background: R1.Background
                  Given rule R1 background step_1

                Scenario: R1.Scenario_1
                  Given rule R1 scenario_1 step_1
            '''.lstrip()
        feature = parse_feature(text)
        assert feature.name == "Without Feature.Background and with Rule.Background"
        assert feature.background is None
        assert len(feature.scenarios) == 0
        assert len(feature.rules) == 1
        assert len(feature.run_items) == 1

        rule1 = feature.rules[0]
        rule1_scenario1 = rule1.scenarios[0]
        assert feature.run_items == [rule1]

        assert rule1.background is not None
        assert rule1.background is not feature.background
        assert rule1.background.inherited_steps == []

        assert rule1_scenario1.name == "R1.Scenario_1"
        assert rule1_scenario1.background is rule1.background
        assert rule1_scenario1.background_steps == rule1.background.steps
        assert rule1_scenario1.background_steps == list(rule1.background.all_steps)
        assert_compare_steps(rule1_scenario1.all_steps, [
            (u"given", u"Given", u'rule R1 background step_1', None, None),
            (u"given", u"Given", u'rule R1 scenario_1 step_1', None, None),
        ])

    def test_parse__rule_scenarios_without_feature_and_rule_background(self):
        text = u'''
            Feature: Without Feature.Background and Rule.Background

              Rule: R1
                Scenario: R1.Scenario_1
                  Given rule R1 scenario_1 step_1
            '''.lstrip()
        feature = parse_feature(text)
        assert feature.name == "Without Feature.Background and Rule.Background"
        assert feature.background is None
        assert len(feature.scenarios) == 0
        assert len(feature.rules) == 1
        assert len(feature.run_items) == 1

        rule1 = feature.rules[0]
        rule1_scenario1 = rule1.scenarios[0]
        assert feature.run_items == [rule1]

        assert rule1.background is None

        assert rule1_scenario1.name == "R1.Scenario_1"
        assert rule1_scenario1.background is None
        assert rule1_scenario1.background is rule1.background
        assert rule1_scenario1.background_steps == []
        assert_compare_steps(rule1_scenario1.all_steps, [
            (u"given", u"Given", u'rule R1 scenario_1 step_1', None, None),
        ])


# ---------------------------------------------------------------------------
# TEST SUITE: Verify Alias keywords
# ---------------------------------------------------------------------------
class TestParser4Scenario(object):
    def test_use_example_alias(self):
        """HINT: Some Scenarios may exist before the first Rule."""
        text = u'''
Feature: With Example as Alias for Scenario

  Example: Scenario_1
    Given scenario_1 step_1
    When  scenario_1 step_2
'''.lstrip()
        feature = parse_feature(text)
        assert feature.name == "With Example as Alias for Scenario"
        assert len(feature.scenarios) == 1
        assert len(feature.run_items) == 1

        scenario1 = feature.scenarios[0]
        assert feature.run_items == [scenario1]

        assert scenario1.name == "Scenario_1"
        assert scenario1.keyword == "Example"
        assert scenario1.background is None
        assert scenario1.parent is feature
        assert scenario1.feature is feature
        assert scenario1.tags == []
        assert scenario1.description == []
        assert_compare_steps(scenario1.all_steps, [
            ("given", "Given", 'scenario_1 step_1', None, None),
            ("when", "When", 'scenario_1 step_2', None, None),
        ])


class TestParser4ScenarioOutline(object):
    def test_use_scenario_template_alias(self):
        """HINT: Some Scenarios may exist before the first Rule."""
        text = u'''
    Feature: Use ScenarioTemplate as Alias for ScenarioOutline

      Scenario Template: ScenarioOutline_1
        Given a step with name "<name>"
        
        Examples:
          | name  |
          | Alice |
          | Bob   |
    '''.lstrip()
        feature = parse_feature(text)
        assert feature.name == "Use ScenarioTemplate as Alias for ScenarioOutline"
        assert len(feature.scenarios) == 1
        assert len(feature.run_items) == 1

        scenario1 = feature.scenarios[0]
        assert feature.run_items == [scenario1]

        assert scenario1.name == "ScenarioOutline_1"
        assert scenario1.keyword == "Scenario Template"
        assert scenario1.background is None
        assert scenario1.parent is feature
        assert scenario1.feature is feature
        assert scenario1.tags == []
        assert scenario1.description == []
        assert len(scenario1.scenarios) == 2
        assert scenario1.scenarios[0].name == "ScenarioOutline_1 -- @1.1 "
        assert_compare_steps(scenario1.scenarios[0].steps, [
            ("given", "Given", 'a step with name "Alice"', None, None),
        ])
        assert scenario1.scenarios[1].name == "ScenarioOutline_1 -- @1.2 "
        assert_compare_steps(scenario1.scenarios[1].steps, [
            ("given", "Given", 'a step with name "Bob"', None, None),
        ])
