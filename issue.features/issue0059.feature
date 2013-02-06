@issue
Feature: Issue #59 Fatal error when using --format=json

  Using the JSON formatter caused a fatal error.

  Background: Test Setup
    Given a new working directory
    And   a file named "features/steps/steps.py" with:
      """
      from behave import given

      @given(u'passing')
      def step(context):
          pass
      """
    And   a file named "features/issue59_test.feature" with:
      """
      Feature: Passing tagged Scenario
        Scenario: P1
          Given passing
      """

  Scenario: Use the JSONFormatter
    When I run "behave --format=json features/issue59_test.feature"
    Then it should pass with:
      """
      1 feature passed, 0 failed, 0 skipped
      1 scenario passed, 0 failed, 0 skipped
      """
