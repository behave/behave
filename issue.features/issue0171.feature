@issue
Feature: Issue #171: Importing step from other step file fails with AmbiguousStep Error

  | When a step module imports another step module
  | this should not cause AmbiguousStep errors
  | due to duplicated registration of the same step functions.
  |
  | NOTES:
  |   * In general you should avoid this case (provided as example here).


  Scenario: Step module imports other step module

    Reuse existing, co-located feature test.

    Given I use the current directory as working directory
    When I run "behave -f plain features/step.import_other_step_module.feature"
    Then it should pass with:
      """
      2 scenarios passed, 0 failed, 0 skipped
      """
