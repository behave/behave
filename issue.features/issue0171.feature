@issue
Feature: Issue #171: Importing step from other step file fails with AmbiguousStep Error

  . When a step module imports another step module
  . this should not cause AmbiguousStep errors
  . due to duplicated registration of the same step functions.
  .
  . NOTES:
  .   * In general you should avoid this case (provided as example here).


  @reuse.colocated_test
  Scenario: Step module imports other step module
    Given I use the current directory as working directory
    When I run "behave -f plain features/step.import_other_step_module.feature"
    Then it should pass
