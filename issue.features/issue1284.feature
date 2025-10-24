@issue
Feature: Issue #1284 -- Pretty Formatter

  . DESCRIPTION:
  .   When using pretty formatter and a Background is present,
  .   the feature statement is duplicated.
  .
  . SEE ALSO:
  .   * https://github.com/behave/behave/issues/1284

  Scenario: Syndrome
    Given a new working directory
    And a file named "features/steps/use_steplib_behave4cmd.py" with:
      """
      import behave4cmd0.passing_steps
      """
    And a file named "features/syndrome_1284.feature" with:
      """
      Feature: Syndrome 1284
        Background:
          Given a step passes

        @dummy_test
        Scenario: S1
          When another step passes
          Then this step passes
      """

    When I run "behave -f pretty features/syndrome_1284.feature"
    Then it should pass with:
      """
      1 scenario passed, 0 failed, 0 skipped
      3 steps passed, 0 failed, 0 skipped
      """
    And the command output should contain:
      """
      USING RUNNER: behave.runner:Runner
      Feature: Syndrome 1284 # features/syndrome_1284.feature:1

        @dummy_test
        Scenario: S1               # features/syndrome_1284.feature:6
      """
    And the command output should contain "Feature: Syndrome 1284" 1 times
