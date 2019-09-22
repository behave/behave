@issue
Feature: Issue #772 -- Syndrome: ScenarioOutline with Examples keyword w/o Table



  Background: Setup
    Given a new working directory
    And a file named "features/syndrome_772.feature" with:
      """
      Feature: Examples without table

        Scenario Outline:
          Given a step passes
          When another step passes

          Examples: Without table
      """
    And a file named "features/steps/use_step_library.py" with:
      """
      # -- REUSE STEPS:
      import behave4cmd0.passing_steps
      """

  Scenario: Use ScenarioOutline with Examples keyword without table
    When I run "behave -f plain features/syndrome_772.feature"
    Then it should pass with:
      """
      Feature: Examples without table
      ERROR: ScenarioOutline.Examples: Has NO-TABLE syndrome (features/syndrome_772.feature:7)
      """
    And the command output should not contain "Parser failure in state"
