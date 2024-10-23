Feature: General Feature Test

  Scenario: Test if general steps are loaded from the 'nested_steps' subdirectory
    Given a general step is executed
    Then the general step should be recognized
