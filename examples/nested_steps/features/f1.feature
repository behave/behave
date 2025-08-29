Feature: f1
  Scenario: S1
    Given I meet "Alice"
    When I invite "Alice" for dinner
    Then a dinner reservation for "Alice" and me was made
