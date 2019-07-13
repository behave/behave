@use.with_python.version=3.4
@use.with_python.version=3.5
@use.with_python.version=3.6
@use.with_python.version=3.7
@use.with_python.version=3.8
Feature:
  Scenario:
    Given I dispatch an async-call with param "Alice"
    And   I dispatch an async-call with param "Bob"
    Then the collected result of the async-calls is "ALICE, BOB"
