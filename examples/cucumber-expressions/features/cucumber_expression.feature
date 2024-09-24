Feature: Use CucumberExpressions in Step Definitions
    Scenario: User selects a color twice
      Given I am on the profile settings page
      When I select the "red" theme colour
      But  I select the "blue" theme color
      Then the profile color should be "blue"
