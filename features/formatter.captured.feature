@logging
@capture
Feature: Captured Formatter

  As a tester
  I want to inspect the captured output of features, rules, scenarios and steps
  So that I can diagnose where some output was captured.

  . SPECIFICATION:
  .  * Select this formatter with: "-f captured"
  .  * Shows the statement (with its location) and its captured output
  .  * A step is only shown if it has any captured output

  Background:
    Given a new working directory
    And a file named "features/steps/steps.py" with:
        """
        from behave import step

        @step('I print "{text}"')
        def step_print(context, text):
            print(text)

        @step('I print "{text}" and fail')
        def step_print_and_fail(context, text):
            print(text)
            assert False, "XFAIL-STEP"
        """

  Scenario: Failing step with captured output
    Given a file named "features/failing.feature" with:
        """
        Feature: Failing
          Scenario: F1
            Given I print "Hello Alice" and fail
        """
    When I run "behave -f captured --no-color features/failing.feature"
    Then it should fail with:
        """
        0 scenarios passed, 1 failed, 0 skipped
        0 steps passed, 1 failed, 0 skipped
        """
    And the command output should not contain "Traceback"
    And the command output should contain:
        """
            Step: Given I print "Hello Alice" and fail  -- ON_END: failed
            Location: features/failing.feature:3

        ____CAPTURED: FAILED _______________________
        CAPTURED STDOUT: step
        Hello Alice

        CAPTURED STDERR: step
        ASSERT FAILED: XFAIL-STEP
        ____CAPTURED_END________________________________
        """
    And the command output should contain:
        """
          Scenario: F1  -- ON_END: failed
          Location: features/failing.feature:2

        ____CAPTURED: FAILED _______________________
        CAPTURED STDOUT: scenario
        Hello Alice
        ____CAPTURED_END________________________________
        """

  Scenario: Passing steps with captured output
    Given a file named "features/passing.feature" with:
        """
        Feature: Passing
          Scenario: P1
            Given I print "Hello Bob"
            When I print "Hello Charly"
        """
    When I run "behave -f captured --no-color features/passing.feature"
    Then it should pass with:
        """
        1 scenario passed, 0 failed, 0 skipped
        2 steps passed, 0 failed, 0 skipped
        """
    And the command output should not contain "Traceback"
    And the command output should contain:
        """
          Scenario: P1  -- ON_END: passed
          Location: features/passing.feature:2
        """
