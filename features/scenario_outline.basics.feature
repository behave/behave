@issue
Feature: Issue #187 ScenarioOutline uses wrong return value when if fails

  Ensure that ScenarioOutline run-logic behaves as expected.

  @setup
  Scenario: Feature Setup
    Given a new working directory
    And a file named "features/steps/steps.py" with:
      """
      from behave import step

      @step('a step passes')
      def step_passes(context):
          pass

      @step('a step fails')
      def step_fails(context):
          assert False, "XFAIL-STEP"
      """

  Scenario: All examples pass
    Given a file named "features/example.scenario_outline_pass.feature" with:
      """
      Feature:  All Examples pass
        Scenario Outline:
          Given a step <outcome>

          Examples:
            | outcome | Comment |
            | passes  | First example passes |
            | passes  | Last  example passes |
      """
    When I run "behave -f plain features/example.scenario_outline_pass.feature"
    Then it should pass with:
      """
      1 feature passed, 0 failed, 0 skipped
      2 scenarios passed, 0 failed, 0 skipped
      """

  @scenario_outline.fails
  Scenario: First example fails
    Given a file named "features/example.scenario_outline_fail_first.feature" with:
      """
      Feature:  First Example in Scenario Outline fails
        Scenario Outline:
          Given a step <outcome>

          Examples:
            | outcome | Comment |
            | fails   | First example fails  |
            | passes  | Last  example passes |
      """
    When I run "behave -f plain features/example.scenario_outline_fail_first.feature"
    Then it should fail with:
      """
      0 features passed, 1 failed, 0 skipped
      1 scenario passed, 1 failed, 0 skipped
      """

  @scenario_outline.fails
  Scenario: Last example fails
    Given a file named "features/example.scenario_outline_fail_last.feature" with:
      """
      Feature:  Last Example in Scenario Outline fails
        Scenario Outline:
          Given a step <outcome>

          Examples:
            | outcome | Comment |
            | passes  | First example passes |
            | fails   | Last  example fails  |
      """
    When I run "behave -f plain features/example.scenario_outline_fail_last.feature"
    Then it should fail with:
      """
      0 features passed, 1 failed, 0 skipped
      1 scenario passed, 1 failed, 0 skipped
      """

  @scenario_outline.fails
  Scenario: Middle example fails
    Given a file named "features/example.scenario_outline_fail_middle.feature" with:
      """
      Feature:  Middle Example in Scenario Outline fails
        Scenario Outline:
          Given a step <outcome>

          Examples:
            | outcome | Comment |
            | passes  | First  example passes |
            | fails   | Middle example fails  |
            | passes  | Last   example passes |
      """
    When I run "behave -f plain features/example.scenario_outline_fail_middle.feature"
    Then it should fail with:
      """
      0 features passed, 1 failed, 0 skipped
      2 scenarios passed, 1 failed, 0 skipped
      """
