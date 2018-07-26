@wip
Feature: Scenario Outlines can read tags with commas

  @tag,with,commas @tags;with;semi;colons
  Scenario: Scenario can see tags with commas
    Given I print the tags
    Then I see the tag tag,with,commas
    And I see the tag tags;with;semi;colons

  @tag,with,commas @tags;with;semi;colons
  Scenario Outline: Scenario Outline can see tags with commas
    Given I print the tags
    And I see the tag tag,with,commas
    And I see the tag tags;with;semi;colons

    Examples:
    | data  |
    | value |

  Scenario Outline: Scenario Outline can see tags with commas in examples
    Given I print the tags
    And I see the tag tag,with,commas
    And I see the tag tags;with;semi;colons

    @tag,with,commas @tags;with;semi;colons
    Examples:
    | data  |
    | value |
