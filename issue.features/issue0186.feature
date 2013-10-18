@issue
Feature: Issue #186: ScenarioOutline uses wrong return value when if fails

  ScenarioOutline returns encountered a failure only if the last scenario failed.
  Failures in earlier examples return the wrong result.
  Ensure that ScenarioOutline run-logic behaves as expected.

  @reuse.colocated_test
  Scenario: Reuse existing test
    Given I use the current directory as working directory
    When I run "behave -f plain features/scenario_outline.basics.feature"
    Then it should pass
