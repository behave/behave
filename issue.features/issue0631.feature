@issue
@wip @not_working
Feature: Issue #631 -- Scenario Outline variables not possible in table headings

  Background:
    Given a new working directory
    And a file named "features/alice.feature" with:
      """
      Feature:

        Scenario Outline: A1
          When the following request is sent
             | <method>     |
             | /example-url/<method> |
          Then a step passes

          Examples: Supported methods
            | method |
            | GET    |
            | POST   |
      """
    And a file named "features/steps/passing_steps.py" with:
      """
      from behave import step

      @step(u'{word:w} step passes')
      def step_passes(context, word):
          pass
      """
    And a file named "features/steps/problematic_steps.py" with:
      """
      from behave import when

      @when(u'the following request is sent')
      def step_passes(context):
          assert context.table, "REQUIRE: step.table exists"
          pass
      """
    And a file named "behave.ini" with:
      """
      [behave]
      show_timings = false
      """

  @xfail
  Scenario: Check Syndrome
    When  I run "behave -f plain features/"
    Then it should pass with:
      """
      1 feature passed, 0 failed, 0 skipped
      2 scenarios passed, 0 failed, 0 skipped
      4 steps passed, 0 failed, 0 skipped, 0 undefined
      """
    And the command output should not contain "<method>"
