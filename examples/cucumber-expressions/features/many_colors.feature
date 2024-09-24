Feature: Use TypeBuilder.with_many
  Scenario: User selects many colors with cardinality=1
    When I select the "blue" colour
    Then I have selected 1 colour

  Scenario: User selects many colors with cardinality=3
    When I select the "red, blue, green" colors
    Then I have selected 3 colors
