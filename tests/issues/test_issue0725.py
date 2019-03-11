# -*- coding: UTF-8 -*-
"""
https://github.com/behave/behave/issues/725

ANALYSIS:
----------

ScenarioOutlineBuilder did not copy ScenarioOutline.description
to the Scenarios that were created from the ScenarioOutline.
"""

from __future__ import absolute_import, print_function
from behave.parser import parse_feature


def test_issue():
    """Verifies that issue #725 is fixed."""
    text = u'''
Feature: ScenarioOutline with description

  Scenario Outline: SO_1
    Description line 1 for ScenarioOutline.
    Description line 2 for ScenarioOutline.

    Given a step with "<name>"
    
    Examples:
      | name  |
      | Alice |
      | Bob   |
'''.lstrip()
    feature = parse_feature(text)
    assert len(feature.scenarios) == 1
    scenario_outline_1 = feature.scenarios[0]
    assert len(scenario_outline_1.scenarios) == 2
    # -- HINT: Last line triggers building of the Scenarios from ScenarioOutline.

    expected_description = [
        "Description line 1 for ScenarioOutline.",
        "Description line 2 for ScenarioOutline.",
    ]
    assert scenario_outline_1.description == expected_description
    assert scenario_outline_1.scenarios[0].description == expected_description
    assert scenario_outline_1.scenarios[1].description == expected_description
