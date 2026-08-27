@issue
Feature: Issue #1329 -- @functools.wraps on log_capture.capture

  . DESCRIPTION:
  .   The @capture decorator in log_capture.py was missing @functools.wraps(func)
  .   on its inner wrapper function, causing the original function name
  .   (e.g., before_scenario) to be lost.
  .
  . SEE ALSO:
  .   * https://github.com/behave/behave/issues/1329

  Scenario: @capture preserves the decorated function name
    Given a new working directory
    And a file named "features/steps/use_steplib_behave4cmd.py" with:
      """
      import behave4cmd0.passing_steps
      """
    And a file named "features/environment.py" with:
      """
      from behave.log_capture import capture

      def assert_name_preserved(func):
          assert func.__name__ == "before_scenario", \
              "Expected __name__ == 'before_scenario', got: %r" % func.__name__
          return func

      @assert_name_preserved
      @capture
      def before_scenario(context, scenario):
          pass
      """
    And a file named "features/issue1329.feature" with:
      """
      Feature: Issue 1329
        Scenario: Check function name is preserved
          Given a step passes
      """
    When I run "behave features/issue1329.feature"
    Then it should pass with:
      """
      1 scenario passed, 0 failed, 0 skipped
      1 step passed, 0 failed, 0 skipped
      """
