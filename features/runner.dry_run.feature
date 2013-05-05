@sequential
Feature: Runner should support a --dry-run option

    As a tester
    I want to check if behave tests are syntactically correct
    And all step definitions exist
    Before I actually run the tests (by executing steps).

    | Specification: Dry-run mode
    |   * Undefined steps are detected
    |   * Marks steps as "untested" or "undefined"
    |   * Marks scenarios as "untested"
    |   * Marks features as "untested"
    |   * Causes no failed scenarios, features
    |   * Causes failed test-run when undefined steps are found.

    @setup
    Scenario: Feature Setup
        Given a new working directory
        And a file named "features/steps/steps.py" with:
            """
            from behave import step

            @step('a step passes')
            def step_passes(context):
                pass

            @step('a step fails')
            def step_fails(context):
                assert False, "XFAIL"
            """
        And a file named "features/alice.feature" with:
            """
            Feature: Alice

                @selected
                Scenario: A1
                    Given a step passes
                    When a step passes
                    Then a step passes

                @other_selected
                Scenario: A2
                    Given a step passes
                    When a step fails
                    Then a step passes

                @selected
                Scenario: A3
                    Given a step passes

                @selected
                Scenario: A4
                    Given a step fails
            """
        And a file named "features/bob.feature" with:
            """
            Feature: Bob
                Scenario: B1
                    Given a step passes
                    When a step passes
                    Then a step passes

                Scenario: B2
                    Given a step passes
                    When a step fails
                    Then a step passes
            """
        And a file named "features/undefined_steps.feature" with:
            """
            Feature: Undefined Steps

                @selected
                Scenario: U1
                    Given a step passes
                    When a step is undefined
                    Then a step fails

                @other_selected
                Scenario: U2 fails
                    Given a step is undefined
                    When a step passes
                    And  a step fails
                    Then a step is undefined
            """


    Scenario: Dry-run one feature should mark feature/scenarios/steps as untested
        When I run "behave -f plain --dry-run features/alice.feature"
        Then it should pass with:
            """
            0 features passed, 0 failed, 0 skipped, 1 untested
            0 scenarios passed, 0 failed, 0 skipped, 4 untested
            0 steps passed, 0 failed, 0 skipped, 0 undefined, 8 untested
            """
        And the command output should contain:
            """
            Feature: Alice
                Scenario: A1
                Scenario: A2
                Scenario: A3
                Scenario: A4
            """

    Scenario: Dry-run one feature with tags should mark skipped scenario/steps as skipped
        When I run "behave -f plain --dry-run --tags=@selected --no-skipped features/alice.feature"
        Then it should pass with:
            """
            0 features passed, 0 failed, 0 skipped, 1 untested
            0 scenarios passed, 0 failed, 1 skipped, 3 untested
            0 steps passed, 0 failed, 3 skipped, 0 undefined, 5 untested
            """
        And the command output should contain:
            """
            Feature: Alice
                Scenario: A1
                Scenario: A3
                Scenario: A4
            """


    Scenario: Dry-run two features
        When I run "behave --dry-run features/alice.feature features/bob.feature"
        Then it should pass with:
            """
            0 features passed, 0 failed, 0 skipped, 2 untested
            0 scenarios passed, 0 failed, 0 skipped, 6 untested
            0 steps passed, 0 failed, 0 skipped, 0 undefined, 14 untested
            """

    Scenario: Dry-run one feature with undefined steps
        When I run "behave --dry-run features/undefined_steps.feature"
        Then it should fail with:
            """
            0 features passed, 0 failed, 0 skipped, 1 untested
            0 scenarios passed, 0 failed, 0 skipped, 2 untested
            0 steps passed, 0 failed, 0 skipped, 3 undefined, 4 untested
            """

    Scenario: Dry-run two features, one with undefined steps
        When I run "behave --dry-run features/alice.feature features/undefined_steps.feature"
        Then it should fail with:
            """
            0 features passed, 0 failed, 0 skipped, 2 untested
            0 scenarios passed, 0 failed, 0 skipped, 6 untested
            0 steps passed, 0 failed, 0 skipped, 3 undefined, 12 untested
            """

    Scenario: Dry-run two features, one with undefined steps and use tags
        When I run "behave --dry-run --tags=@selected features/alice.feature features/undefined_steps.feature"
        Then it should fail with:
            """
            0 features passed, 0 failed, 0 skipped, 2 untested
            0 scenarios passed, 0 failed, 2 skipped, 4 untested
            0 steps passed, 0 failed, 7 skipped, 1 undefined, 7 untested
            """

    Scenario: Dry-run two features, one with undefined steps and use other tags
        When I run "behave --dry-run --tags=@other_selected features/alice.feature features/undefined_steps.feature"
        Then it should fail with:
            """
            0 features passed, 0 failed, 0 skipped, 2 untested
            0 scenarios passed, 0 failed, 4 skipped, 2 untested
            0 steps passed, 0 failed, 8 skipped, 2 undefined, 5 untested
            """
