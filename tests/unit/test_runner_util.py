# -*- coding: UTF-8 -*-

from __future__ import absolute_import, print_function
from collections import OrderedDict
from behave.runner_util import FeatureLineDatabase
from behave.parser import parse_feature
from behave.model import Feature, Rule, ScenarioOutline, Scenario, Background
import pytest


# ---------------------------------------------------------------------------------------
# TEST DATA: FeatureLineDatabase
# ---------------------------------------------------------------------------------------
feature_text1 = u"""
    Feature: Alice
        Background: Alice.Background
          Given a background step passes
          
        Scenario: A1
          Given a scenario step passes

        Scenario: A2
          Given a scenario step passes
          When a scenario step passes
    """

feature_text_with_scenario_outline = u"""
    Feature: Bob
    
        Scenario Outline: Bob.SO_2_<row.id>
          Given a person with name "<Name>"
          Then the person is born in <Birthyear>
        
          Examples:
            | Name  | Birthyear |
            | Alice |  1990     |
            | Bob   |  1991     |
            
        Scenario: Bob.S3
          Given a scenario step passes
          When a scenario step passes
    """

feature_text_with_rule = u"""
    Feature: Charly
        Background: Charly.Background
          Given a background step passes

        Scenario: C1
          Given a scenario step passes

        Rule: Charly.Rule_1

          Scenario: Rule_1.C2
            Given a scenario step passes
            When a scenario step passes
    """

feature_file_map = {
    "basic.feature": feature_text1,
    "scenario_outline.feature": feature_text_with_scenario_outline,
    "rule.feature": feature_text_with_rule,
}

# ---------------------------------------------------------------------------------------
# TEST SUITE FOR: FeatureLineDatabase
# ---------------------------------------------------------------------------------------
class TestFeatureLineDatabase(object):
    def test_make(self):
        feature = parse_feature(feature_text1.strip(),
                                filename="features/Alice.feature")
        scenario_0 = feature.scenarios[0]
        scenario_1 = feature.scenarios[1]

        line_database = FeatureLineDatabase.make(feature)
        expected = OrderedDict([
            (0, feature),
            (feature.location.line, feature),
            (scenario_0.line, scenario_0),
            (scenario_1.line, scenario_1),
        ])
        assert line_database.data == expected
        assert feature.location.line == 1

    def test_make__with_scenario_outline(self):
        feature = parse_feature(feature_text_with_scenario_outline.strip(),
                                filename="features/Bob.feature")
        scenarios = feature.walk_scenarios(with_outlines=True)
        scenario_outline = scenarios[0]
        assert scenario_outline is feature.run_items[0]
        scenario_1 = scenarios[1]
        scenario_2 = scenarios[2]
        scenario_3 = scenarios[3]

        line_database = FeatureLineDatabase.make(feature)
        expected = OrderedDict([
            (0, feature),
            (feature.location.line, feature),
            (scenario_outline.line, scenario_outline),
            (scenario_1.line, scenario_1),
            (scenario_2.line, scenario_2),
            (scenario_3.line, scenario_3),
        ])
        assert line_database.data == expected
        assert feature.location.line < scenario_outline.location.line
        assert scenario_outline.location.line < scenario_1.location.line
        assert scenario_1.location.line < scenario_2.location.line
        assert scenario_2.location.line < scenario_3.location.line


    def test_select_run_items_by_line__feature_line_selects_feature(self):
        feature = parse_feature(feature_text1, filename="features/Alice.feature")
        line_database = FeatureLineDatabase.make(feature)
        selected = line_database.select_run_item_by_line(feature.location.line)
        assert selected is feature
        assert isinstance(selected, Feature)

    @pytest.mark.parametrize("filename", [
        "basic.feature", "scenario_outline.feature", "rule.feature"
    ])
    def test_select_run_items_by_line__entity_line_selects_entity(self, filename):
        feature_text = feature_file_map[filename]
        feature = parse_feature(feature_text, filename=filename)
        line_database = FeatureLineDatabase.make(feature)
        last_line = 0
        all_run_items = feature.walk_scenarios(with_outlines=True, with_rules=True)
        for run_item in all_run_items:
            selected = line_database.select_run_item_by_line(run_item.location.line)
            assert selected is run_item
            assert last_line < selected.location.line
            last_line = run_item.location.line

    @pytest.mark.parametrize("filename", [
        "basic.feature", "scenario_outline.feature", "rule.feature"
    ])
    def test_select_run_items_by_line__line_before_entity_selects_last_entity(self, filename):
        feature_text = feature_file_map[filename]
        feature = parse_feature(feature_text, filename=filename)
        line_database = FeatureLineDatabase.make(feature)
        all_run_items = feature.walk_scenarios(with_outlines=True, with_rules=True)
        last_run_item = feature
        for run_item in all_run_items:
            predecessor_line = run_item.location.line - 1
            selected = line_database.select_run_item_by_line(predecessor_line)
            assert selected is last_run_item
            assert selected is not run_item
            last_run_item = run_item

    @pytest.mark.parametrize("filename", [
        "basic.feature", "scenario_outline.feature", "rule.feature"
    ])
    def test_select_run_items_by_line__line_after_entity_selects_entity(self, filename):
        # -- HINT: In most cases
        # EXCEPT:
        #   * Scenarios of ScenarioOutline: scenario.line == SO.examples.row.line
        #   * Empty entity without steps is directly followed by other entity
        feature_text = feature_file_map[filename]
        feature = parse_feature(feature_text, filename=filename)
        line_database = FeatureLineDatabase.make(feature)
        all_run_items = feature.walk_scenarios(with_outlines=True, with_rules=True)
        file_end_line = all_run_items[-1].location.line + 1000
        for index, run_item in enumerate(all_run_items):
            next_line = run_item.location.line + 1
            next_entity_line = file_end_line
            if index+1 < len(all_run_items):
                next_entity = all_run_items[index+1]
                next_entity_line = next_entity.line
            if next_line >= next_entity_line:
                # -- EXCLUDE: Scenarios in a ScenarioOutline
                print("EXCLUDED: %s: %s (line=%s)" %
                      (run_item.keyword, run_item.name, run_item.line))
                continue

            selected = line_database.select_run_item_by_line(next_line)
            assert selected is run_item
