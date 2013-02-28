@issue
Feature: Issue #125: Duplicate "Captured stdout" if substep has failed


Background: Test Setup
  Given a new working directory
  And   a file named "features/steps/steps.py" with:
      """
      from behave import step

      @step(u'a step fails with stdout "{message}"')
      def step_fails_with_stdout(context, message):
          print(message)
          assert False, 'EXPECT: Step fails with stdout.'

      @step(u'substep fails with stdout')
      def master_stdout_step(context):
          context.execute_steps(u'When a step fails with stdout "hello"')
      """

Scenario: Subprocess call shows generated output
  Given a file named "features/issue125.feature" with:
      """
      Feature:
          Scenario:
              When substep fails with stdout
      """
  When I run "behave -f plain features/issue125.feature"
  Then it should fail with:
      """
      0 scenarios passed, 1 failed, 0 skipped
      0 steps passed, 1 failed, 0 skipped, 0 undefined
      """
  And the command output should not contain:
      """
      Captured stdout:
      hello

      Captured stdout:
      hello
      """
