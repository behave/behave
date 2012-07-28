@issue
Feature: Issue #52 Behave counts are wrong with option --tags

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

  Scenario: Successful Execution of Tagged Scenario
    Given a file named "features/tagged_scenario1.feature" with:
      """
      Feature: Passing tagged Scenario
        @done
        Scenario: 1
          Given passing

        @unimplemented
        Scenario: N1
          Given passing
        @unimplemented
        Scenario: N2
          Given passing
      """
    When I run "behave --junit -c --tags @done features/tagged_scenario1.feature"
    Then it should pass with:
      """
      1 feature passed, 0 failed, 0 skipped
      1 scenario passed, 0 failed, 2 skipped
      """

  Scenario: Failing Execution of Tagged Scenario
    Given a file named "features/tagged_scenario2.feature" with:
      """
      Feature: Failing tagged Scenario
        @done
        Scenario: 1
          Given failing

        @unimplemented
        Scenario: N1
          Given passing
        @unimplemented
        Scenario: N2
          Given passing
      """
    When I run "behave --junit -c --tags @done features/tagged_scenario2.feature"
    Then the command output should contain:
      """
      0 features passed, 1 failed, 0 skipped
      0 scenarios passed, 1 failed, 2 skipped
      """
    And it should fail
