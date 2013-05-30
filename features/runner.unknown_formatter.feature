Feature: When an unknown formatter is used


  Scenario: Unknown formatter is used
    When I run "behave -f unknown1"
    Then it should fail with:
      """
      behave: error: format=unknown1 is unknown
      """

  Scenario: Unknown formatter is used together with another formatter
    When I run "behave -f plain -f unknown1"
    Then it should fail with:
      """
      behave: error: format=unknown1 is unknown
      """

  Scenario: Two unknown formatters are used
    When I run "behave -f plain -f unknown1 -f tags -f unknown2"
    Then it should fail with:
      """
      behave: error: format=unknown1, unknown2 is unknown
      """
