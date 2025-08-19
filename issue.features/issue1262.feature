@issue
@not_reproducible
Feature: Issue #1262 -- v1.3.0 upwards doesn't find some step

  . DESCRIPTION:
  . Since behave v1.3.0, the then-step is no longer found.
  .
  . SEE ALSO:
  .   * https://github.com/behave/behave/issues/1262

  Background:
    Given a new working directory
    And a file named "features/steps/use_behave4cmd_steps.py" with:
      """
      import behave4cmd0.passing_steps
      """
    And a file named "features/syndrome_1262.feature" with:
      """
      Feature: Syndrome 1262
        Scenario: S1
          Given a step passes
          When another step passes
          Then the data returned contains all IP addresses available.

        Scenario: S2
          Given I need to get the IP addresses without filtering
          When I run the IP addresses function without filtering applied
          Then the data returned contains all IP addresses available.
      """

  @step_matcher.<step_matcher>
  Scenario Outline: Check Syndrome w/ step-matcher "<step_matcher>"
    And a file named "features/steps/syndrome_steps.py" with:
      """
      from behave import given, when, then, use_step_matcher

      use_step_matcher("<step_matcher>")

      @given(u'I need to get the IP addresses without filtering')
      @when(u'I run the IP addresses function without filtering applied')
      @then(u'the data returned contains all IP addresses available.')
      def then_data_contains_all_ip_addresses_available(ctx):
          pass
      """
    When I run "behave -f plain features/syndrome_1262.feature"
    Then it should pass with:
      """
      2 scenarios passed, 0 failed, 0 skipped
      6 steps passed, 0 failed, 0 skipped
      """
    And the command output should not contain "StepNotImplementedError"

    Examples:
      | step_matcher |
      | parse |
      | re|
