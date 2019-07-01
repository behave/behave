@fail
Feature: With Rule(s) and Failing Scenario(s)

  HINT: Contains failing scenarios (by intention).

  @xfail
  Scenario: F0 -- Fails
    When some step fails

  Rule: Fails in Scenario F2

    Scenario: F1
      Given a step passes

    @xfail
    Scenario: F2 -- Fails
      Given another step passes
      When a step fails
      Then another step passes
