@wip
Feature: Scenario Outlines can read tags with commas

  @tag,with,commas
  Scenario: Scenario can see tags with commas
    Given I print the tags
    Then I see the tag tag,with,commas

  @tag,with,commas
  Scenario Outline: Scenario Outline can see tags with commas
    Given I print the tags
    And I see the tag tag,with,commas

    Examples:
    | data  |
    | value |

  Scenario Outline: Scenario Outline can see tags with commas in examples
    Given I print the tags
    And I see the tag tag,with,commas

    @tag,with,commas
    Examples:
    | data  |
    | value |
