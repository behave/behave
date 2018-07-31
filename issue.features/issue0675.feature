@issue
Feature: Issue #675 -- .feature files cannot be found within symlink directories


  Background: setting up directory structure without symlink
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

  Scenario: failing case: feature symlink doesn't exist yet
    When I run "behave -f plain second"
    Then it should fail
    And the command output should contain "ConfigError: No feature files in"

  Scenario: add symlink to feature directory and expect pass
    When I run "ln -s ../features second/features"
    And I run "behave -f plain second"
    Then it should pass with:
      """
      1 feature passed, 0 failed, 0 skipped
      1 scenario passed, 0 failed, 0 skipped
      3 steps passed, 0 failed, 0 skipped, 0 undefined
      """
