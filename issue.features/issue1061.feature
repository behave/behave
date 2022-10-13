@issue
Feature: Issue #1061 -- Syndrome: Scenario does not inherit Rule Tags

  Background: Setup
    Given a new working directory
    And a file named "features/syndrome_1061.feature" with:
      """
      Feature: F1

        @rule_tag
        Rule: R1

          Scenario: S1
            Given a step passes
            When another step passes
      """
    And a file named "features/steps/use_step_library.py" with:
      """
      # -- REUSE STEPS:
      import behave4cmd0.passing_steps
      """
    And a file named "behave.ini" with:
      """
      [behave]
      show_timings = false
      """

  Scenario: Verify syndrome is fixed
    When I run "behave -f plain --tags=rule_tag features/syndrome_1061.feature"
    Then it should pass with:
      """
      Scenario: S1
        Given a step passes ... passed
        When another step passes ... passed
      """
    And the command output should contain:
      """
      1 rule passed, 0 failed, 0 skipped
      1 scenario passed, 0 failed, 0 skipped
      2 steps passed, 0 failed, 0 skipped
      """
    And note that "the rule scenario is NOT SKIPPED"
