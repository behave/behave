Feature: Local Context Parameters defined in Scenarios (Steps)

    | Specification:
    |   * When a step adds/modifies an attribute in the Context object,
    |     then its value is only available to other steps in this scenario.
    |   * After a scenario is executed all Context object changes are undone.

    Scenario: Add Local Context parameter in Scenario/Step
      Given the behave context does not have a parameter "local_name"
      When I set the context parameter "local_name" to "Alice"
      Then the behave context should have a parameter "local_name"
      And  the behave context should contain:
        | Parameter  | Value   |
        | local_name | "Alice" |

    Scenario: Ensure that Local Context parameter is not available to next Scenario
      Then the behave context should not have a parameter "local_name"
