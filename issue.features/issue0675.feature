@issue
@sequential
@not.with_platform=windows
Feature: Issue #675 -- Feature files cannot be found within symlink directories

  NOTES:
    Test may only work on UNIX-like system (Linux, macOS, FreeBSD, ...).
    Test requires that all scenarios are run (not: ordering-idenpendent).


  Background: Setup Directory Structure
    Given a new working directory
    And a file named "features/pass.feature" with:
      """
      Feature: Issue 675

      Scenario: this too shall pass
        Given this
        When this
        Then this
      """
    And a file named "second/steps/steps.py" with:
      """
      from behave import step

      @step(u'this')
      def step_impl(context):
        pass
      """

  Scenario: Without Symlink to Feature Directory (expected to fail)
    When I run "behave -f plain second"
    Then it should fail
    And the command output should contain "ConfigError: No feature files in"

  Scenario: With Symlink to Feature Directory (expected to pass)
    When I create a symlink from "../features" to "second/features"
    And I run "behave -f plain second"
    Then it should pass with:
      """
      1 feature passed, 0 failed, 0 skipped
      1 scenario passed, 0 failed, 0 skipped
      3 steps passed, 0 failed, 0 skipped, 0 undefined
      """
