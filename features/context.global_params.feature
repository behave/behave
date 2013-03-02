Feature: Global Context Parameters defined in "environment.py"

    | Specification:
    |   * When a Context parameter is defined in "environment.py",
    |     its value is provided to all scenarios (steps).
    |   * Each scenario has the same global parameters (and values).
    |   * A scenario (step) may modify global parameters (values).
    |   * After a scenario is executed all changes to Context parameters are reverted.

    Scenario: Test Setup Description (Example)
      Given a file named "features/environment.py" with:
        """
        def before_all(context):
            context.global_name = "env:Alice"
            context.global_age  = 12
        """

    Scenario: Modify global Context parameter in Scenario Step
      Given the behave context contains:
        | Parameter   | Value        |
        | global_name | "env:Alice"  |
        | global_age  | 12           |
      When I set the context parameter "global_name" to "step:Bob"
      Then the behave context should contain:
        | Parameter   | Value        |
        | global_name | "step:Bob"   |
        | global_age  | 12           |

    Scenario: Ensure that Global Context parameter is reset for next Scenario
      Then the behave context should have a parameter "global_name"
      And  the behave context should contain:
        | Parameter   | Value        |
        | global_name | "env:Alice"  |
        | global_age  | 12           |

