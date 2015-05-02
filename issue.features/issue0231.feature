@issue
@not_reproducible
Feature: Issue #231: Display the output of the last print command

  . The output of the last print command in a step is not displayed
  . in the behave output (at least with standard pretty formatter),
  . unless the string to print ends with newline ('\n').
  .
  . ANALYSIS: NOT-REPRODUCIBLE
  .   Checked print function and stdout without newline.
  .   Both show the expected capture stdout output when the step fails.

  @setup
  Scenario: Feature Setup
    Given a new working directory
    And a file named "features/syndrome1.feature" with:
      """
      Feature:
        Scenario: Alice
           Given a step passes
           When  a step passes
           Then  I write "ALICE was HERE" without newline to stdout and fail
      """
    And a file named "features/syndrome2.feature" with:
      """
      Feature:
        Scenario: Bob
           Given a step passes
           Then  I print "BOB was HERE" without newline and fail
      """
    And a file named "features/steps/steps.py" with:
      """
      from __future__ import print_function
      from behave import step
      import sys

      @step('{word:w} step passes')
      def step_passes(context, word):
          pass

      @step('I write "{message}" without newline to stdout and fail')
      def step_write_without_newline_and_fail(context, message):
          sys.stdout.write(message)
          assert False, "FAIL: "+ message

      @step('I print "{message}" without newline and fail')
      def step_print_without_newline_and_fail(context, message):
          print(message, end="")
          assert False, "FAIL: "+ message
      """


  Scenario: Write to stdout without newline
    When I run "behave -f pretty -c -T features/syndrome1.feature"
    Then it should fail with:
      """
      0 scenarios passed, 1 failed, 0 skipped
      2 steps passed, 1 failed, 0 skipped, 0 undefined
      """
    And the command output should contain:
      """
      Captured stdout:
      ALICE was HERE
      """

  Scenario: Use print function without newline
    When I run "behave -f pretty -c -T features/syndrome2.feature"
    Then it should fail with:
      """
      0 scenarios passed, 1 failed, 0 skipped
      1 step passed, 1 failed, 0 skipped, 0 undefined
      """
    And the command output should contain:
      """
      Captured stdout:
      BOB was HERE
      """
