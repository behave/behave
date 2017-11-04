@issue
Feature: Issue #606 -- Name option with special unicode chars


  Background:
    Given a new working directory
    And a file named "features/alice.feature" with:
      """
      Feature: Alice

        Scenario: Ärgernis ist überall
          Given a step passes

        Scenario: My second Ärgernis
          When another step passes

        Scenario: Unused
          Then some step passes
      """
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

  Scenario: Use special unicode chars in --name options
    When  I run "behave -f plain --name Ärgernis features/"
    Then it should pass with:
      """
      1 feature passed, 0 failed, 0 skipped
      2 scenarios passed, 0 failed, 1 skipped
      2 steps passed, 0 failed, 1 skipped, 0 undefined
      """
    And the command output should contain:
      """
      Scenario: Ärgernis ist überall
        Given a step passes ... passed

      Scenario: My second Ärgernis
        When another step passes ... passed
      """
    But the command output should not contain:
      """
      UnicodeDecodeError: 'ascii' codec can't decode byte
      """
