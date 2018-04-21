@wip
Feature: Issue #643 -- Unable to add comments on table data lines

  Background:
    Given a new working directory
    And a file named "features/steps/passing_steps.py" with:
      """
      from behave import step

      @step(u'{word:w} step passes')
      def step_passes(context, word):
          pass
      """
    And a file named "behave.ini" with:
      """
      [behave]
      show_timings = false
      """

  Scenario: Check Syndrome
    Given a file named "features/syndrome_643.feature" with:
      """
      Feature:

        Scenario Outline:
          Given a step passes

          Examples:
            |  name  |   size  |
            |   me   | 1048576 | # 1MB
            | myself | 2097152 | # 2MB
            |   I    | 4194304 | # 4MB
      """
    When  I run "behave -f plain features/syndrome_643.feature"
    Then it should fail with:
      """
      ParserError: Failed to parse "{__WORKDIR__}/features/syndrome_643.feature": Malformed table at line 8
      """

  Scenario: Check Syndrome -- Variant B
    Given a file named "features/syndrome_643B.feature" with:
      """
      Feature:

        Scenario Outline:
          Given a step passes

          Examples:
            |  name  |   size  | # Headings
            |   me   | 1048576 | # 1MB
            | myself | 2097152 | # 2MB
            |   I    | 4194304 | # 4MB
      """
    When  I run "behave -f plain features/syndrome_643B.feature"
    Then it should pass with:
      """
      1 feature passed, 0 failed, 0 skipped
      3 scenarios passed, 0 failed, 0 skipped
      3 steps passed, 0 failed, 0 skipped, 0 undefined
      """
    But note that "providing a comment after each table row 'fixes' the parse-problem, too"
