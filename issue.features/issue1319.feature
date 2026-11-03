@issue
Feature: Issue #1319 -- USING RUNNER message should not go to stdout

  . DESCRIPTION:
  .   The "USING RUNNER: ..." message was printed unconditionally to stdout,
  .   interfering with custom formatters that write to stdout and whose output
  .   is parsed by external tools. This message is diagnostic and should go
  .   to stderr instead.
  .
  . SEE ALSO:
  .   * https://github.com/behave/behave/issues/1319

  Scenario: USING RUNNER is not on stdout
    Given a new working directory
    And a file named "features/steps/use_steplib_behave4cmd.py" with:
      """
      import behave4cmd0.passing_steps
      """
    And a file named "features/run_with_runner.feature" with:
      """
      Feature: Runner output
        Scenario: S1
          Given a step passes
      """
    When I run "behave features/run_with_runner.feature"
    Then it should pass with:
      """
      1 scenario passed, 0 failed, 0 skipped
      1 step passed, 0 failed, 0 skipped
      """
    But the command stdout should not contain "USING RUNNER"
