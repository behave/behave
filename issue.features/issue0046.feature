@issue
Feature: Issue #46 Behave returns 0 (SUCCESS) even in case of test failures

  As I behave user
  I want to detect test success or test failures
  By using the process return value, 0 (SUCCESS) and non-zero for failure.

  Background: Test Setup
    Given a new working directory
    Given a file named "features/steps/steps.py" with:
      """
      from behave import given

      @given(u'passing')
      def step(context):
          pass

      @given(u'failing')
      def step(context):
          assert False, "failing"
      """

  Scenario: Successful Execution
    Given a file named "features/passing.feature" with:
      """
      Feature: Passing
        Scenario: Passing Scenario Example
          Given passing
      """
    When I run "behave -c -q features/passing.feature"
    Then it should pass with:
      """
      1 feature passed, 0 failed, 0 skipped
      1 scenario passed, 0 failed, 0 skipped
      1 step passed, 0 failed, 0 skipped, 0 undefined
      """

  Scenario: Failing Execution
    Given a file named "features/failing.feature" with:
      """
      Feature: Failing
        Scenario: Failing Scenario Example
          Given failing
      """
    When I run "behave -c -q features/failing.feature"
    Then it should fail with:
      """
      0 features passed, 1 failed, 0 skipped
      0 scenarios passed, 1 failed, 0 skipped
      0 steps passed, 1 failed, 0 skipped, 0 undefined
      """

  Scenario: Passing and Failing Execution
    Given a file named "features/passing_and_failing.feature" with:
      """
      Feature: Passing and Failing
        Scenario: Passing Scenario Example
          Given passing
        Scenario: Failing Scenario Example
          Given failing
      """
    When I run "behave -c -q features/passing_and_failing.feature"
    Then it should fail with:
      """
      0 features passed, 1 failed, 0 skipped
      1 scenario passed, 1 failed, 0 skipped
      1 step passed, 1 failed, 0 skipped, 0 undefined
      """
    And the command output should contain:
      """
      Feature: Passing and Failing
        Scenario: Passing Scenario Example
          Given passing
        Scenario: Failing Scenario Example
          Given failing
            Assertion Failed: failing
      """
