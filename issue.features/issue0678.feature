@issue
@enhancement
Feature: Scenario Outlines shall support tags with commas

  @tag,with,commas @tag;with;semicolons
  Scenario: Scenario supports these tags
    Given I inspect the tags of the current scenario
    Then the tag "tag,with,commas" is contained
    And the tag "tag;with;semicolons" is contained

  @tag,with,commas @tag;with;semicolons
  Scenario Outline: Scenario Outline supports these tags
    Given I inspect the tags of the current scenario
    Then the tag "tag,with,commas" is contained
    And the tag "tag;with;semicolons" is contained

    Examples:
    | data  |
    | value |

  Scenario Outline: Scenario Outline supports tagged example
    Given I inspect the tags of the current scenario
    Then the tag "tag,with,commas" is contained
    And the tag "tag;with;semicolons" is contained

    @tag,with,commas @tag;with;semicolons
    Examples:
    | data  |
    | value |
