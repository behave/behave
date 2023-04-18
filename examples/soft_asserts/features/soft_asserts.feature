Feature: Use Soft Assertions in behave

  RELATED TO: https://github.com/behave/behave/discussions/1094

  Scenario: Failing with Soft Assertions -- CASE 1

    HINT:
    Multiple assert statements in a step are executed even if a assert fails.
    After a failed step in the Scenario,
    the remaining steps are skipped and the next Scenario is executed.

    Given a minimum number value of "5"
    Then  the numbers "2" and "12" are in the valid range
    But note that "the step-2 (then step) is expected to fail"

  @behave.continue_after_failed_step
  Scenario: Failing with Soft Assertions -- CASE 2

    HINT: If a step in the Scenario fails, execution is continued.

    Given a minimum number value of "5"
    Then  the number "4" is in the valid range
    And   the number "8" is in the valid range
    But note that "the step-2 is expected to fail"
    But note that "the step-3 should be executed and should pass"

  @behave.continue_after_failed_step
  Scenario: Failing with Soft Assertions -- CASE 1 and CASE 2

    Given a minimum number value of "5"
    Then  the number "2" is in the valid range
    And   the numbers "3" and "4" are in the valid range
    And   the number "8" is in the valid range
    But note that "the step-2 and step-3 are expected to fail"
    But note that "the step-4 should be executed and should pass"

  Scenario: Passing
    Given a step passes
    And note that "this scenario should be executed and should pass"
