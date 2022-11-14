Feature: When an unknown formatter is used


  Scenario: Unknown formatter alias is used
    When I run "behave -f unknown1"
    Then it should fail with:
      """
      behave: error: BAD_FORMAT=unknown1 (problem: LookupError)
      """

  Scenario: Unknown formatter class is used (case: unknown module)
    When I run "behave -f behave.formatter.unknown:UnknownFormatter"
    Then it should fail with:
      """
      behave: error: BAD_FORMAT=behave.formatter.unknown:UnknownFormatter (problem: ModuleNotFoundError)
      """

  Scenario: Unknown formatter class is used (case: unknown class)
    When I run "behave -f behave.formatter.plain:UnknownFormatter"
    Then it should fail with:
      """
      behave: error: BAD_FORMAT=behave.formatter.plain:UnknownFormatter (problem: ClassNotFoundError)
      """

  Scenario: Invalid formatter class is used
    When I run "behave -f behave.formatter.base:StreamOpener"
    Then it should fail with:
      """
      behave: error: BAD_FORMAT=behave.formatter.base:StreamOpener (problem: InvalidClassError)
      """

  Scenario: Unknown formatter is used together with another formatter
    When I run "behave -f plain -f unknown1"
    Then it should fail with:
      """
      behave: error: BAD_FORMAT=unknown1 (problem: LookupError)
      """

  Scenario: Two unknown formatters are used
    When I run "behave -f plain -f unknown1 -f tags -f behave.formatter.plain:UnknownFormatter"
    Then it should fail with:
      """
      behave: error: BAD_FORMAT=unknown1 (problem: LookupError), behave.formatter.plain:UnknownFormatter (problem: ClassNotFoundError)
      """
