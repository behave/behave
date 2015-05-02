@issue
Feature: Issue #162 Unnecessary ContextMaskWarnings when assert fails or exception is raised

  . Behave shows unnecessary ContextMaskWarnings related to:
  .
  .   * tags
  .   * capture_stdout
  .   * capture_stderr
  .   * log_capture
  .
  . if:
  .
  .   * an assertion fails in a step-definition/step-function
  .   * an exception is raised by a step-definition/step-function
  .
  . and an additional scenario follows.
  . REASON: Context "behave" mode is not restored when an exception is raised.


  @setup
  Scenario: Feature Setup
    Given a new working directory
    And a file named "features/steps/steps.py" with:
      """
      from behave import step

      @step('a step passes')
      def step_passes(context):
          pass

      @step('a step assert fails')
      def step_assert_fails(context):
          assert False, "XFAIL-STEP"

      @step('an exception is raised')
      def step_raises_exception(context):
          raise RuntimeError("XFAIL-STEP")
      """


  Scenario: Assertion fails in a step
    Given a file named "features/example0162_assert_fails.feature" with:
      """
      Feature:
        Scenario:
          Given a step passes
          When a step assert fails
          Then a step passes

        Scenario:
          Given a step passes
      """
    When I run "behave -f plain features/example0162_assert_fails.feature"
    Then it should fail with:
      """
      1 scenario passed, 1 failed, 0 skipped
      2 steps passed, 1 failed, 1 skipped, 0 undefined
      """
    But the command output should not contain:
      """
      ContextMaskWarning: user code is masking context attribute
      """


  Scenario: Exception is raised in a step
    Given a file named "features/example0162_exception_raised.feature" with:
      """
      Feature:
        Scenario:
          Given a step passes
          When an exception is raised
          Then a step passes

        Scenario:
          Given a step passes
      """
    When I run "behave -f plain features/example0162_exception_raised.feature"
    Then it should fail with:
      """
      1 scenario passed, 1 failed, 0 skipped
      2 steps passed, 1 failed, 1 skipped, 0 undefined
      """
    But the command output should not contain:
      """
      ContextMaskWarning: user code is masking context attribute
      """
