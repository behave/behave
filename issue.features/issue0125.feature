@issue
Feature: Issue #125: Duplicate "Captured stdout" if substep has failed


  Background: Test Setup
    Given a new working directory
    And   a file named "features/steps/steps.py" with:
      """
      from behave import step

      @step('a step fails with stdout "{message}"')
      def step_fails_with_stdout(context, message):
          print(message)
          assert False, 'EXPECT: Step fails with stdout.'

      @step('substep fails with stdout "{message}"')
      def substep_fails_with_stdout(context, message):
          context.execute_steps('When a step fails with stdout "%s"' % message)
      """

  Scenario: Subprocess call shows generated output
    Given a file named "features/issue125_example.feature" with:
      """
      Feature:
        Scenario:
          When substep fails with stdout "Hello"
      """
    When I run "behave -f plain --no-timings features/issue125_example.feature"
    Then it should fail with:
      """
      0 scenarios passed, 1 failed, 0 skipped
      0 steps passed, 1 failed, 0 skipped
      """
    And the command output should contain:
      """
      Feature:
        Scenario:
          When substep fails with stdout "Hello" ... failed

      ASSERT FAILED: FAILED SUB-STEP: When a step fails with stdout "Hello"
      Substep info: ASSERT FAILED: EXPECT: Step fails with stdout.
      """
    And the command output should contain 1 times:
      """
      CAPTURED STDOUT: scenario
      Hello
      """
    But note that "the captured output should not be contained multiple times"

