@sequential
Feature: Runner should stop after first failure if --stop option is used

    As a tester
    To abort testing early (sometimes)
    When the first failure occurs.


    @setup
    Scenario: Test Setup
        Given a new working directory
        And a file named "features/steps/steps.py" with:
            """
            from behave import step
            import sys

            @step('a step passes')
            def step_passes(context):
                pass

            @step('a step fails')
            def step_fails(context):
                assert False, "XFAIL"
            """
        And a file named "features/alice_fails.feature" with:
            """
            Feature: Alice
                Scenario: A1
                    Given a step passes
                    When a step passes
                    Then a step passes

                Scenario: A2 fails
                    Given a step passes
                    When a step fails
                    Then a step passes

                Scenario: A3
                    Given a step passes

                Scenario: A4 fails
                    Given a step fails
            """
        And a file named "features/bob_passes.feature" with:
            """
            Feature: Bob
                Scenario: B1
                    Given a step passes
                    When a step passes
                    Then a step passes

                Scenario: B2 fails
                    Given a step passes
                    When a step passes
                    Then a step passes
            """


    Scenario: Stop running after first failure with one feature
        When I run "behave -f plain -T --stop features/alice_fails.feature"
        Then it should fail with:
            """
            Failing scenarios:
              features/alice_fails.feature:7  A2 fails

            0 features passed, 1 failed, 0 skipped
            1 scenario passed, 1 failed, 0 skipped, 2 untested
            4 steps passed, 1 failed, 1 skipped, 0 undefined, 2 untested
            """
        And the command output should contain:
            """
            Feature: Alice
                Scenario: A1
                    Given a step passes ... passed
                    When a step passes ... passed
                    Then a step passes ... passed

                Scenario: A2 fails
                    Given a step passes ... passed
                    When a step fails ... failed
                    Assertion Failed: XFAIL
            """
        But the command output should not contain:
            """
            Scenario: A3
            """

    Scenario: Stop running after first failure with several features (CASE 1)
        When I run "behave -f plain -T --stop features/alice_fails.feature features/bob_passes.feature "
        Then it should fail with:
            """
            Failing scenarios:
              features/alice_fails.feature:7  A2 fails

            0 features passed, 1 failed, 0 skipped, 1 untested
            1 scenario passed, 1 failed, 0 skipped, 4 untested
            4 steps passed, 1 failed, 1 skipped, 0 undefined, 8 untested
            """

    Scenario: Stop running after first failure with several features (CASE 2: Different order)
        When I run "behave -f plain -T --stop features/bob_passes.feature features/alice_fails.feature"
        Then it should fail with:
            """
            Failing scenarios:
              features/alice_fails.feature:7  A2 fails

            1 feature passed, 1 failed, 0 skipped
            3 scenarios passed, 1 failed, 0 skipped, 2 untested
            10 steps passed, 1 failed, 1 skipped, 0 undefined, 2 untested
            """

    Scenario: Stop running after first failure with several features (CASE 3: Use directory)
        When I run "behave -f plain -T --stop features/"
        Then it should fail with:
            """
            Failing scenarios:
              features/alice_fails.feature:7  A2 fails

            0 features passed, 1 failed, 0 skipped, 1 untested
            1 scenario passed, 1 failed, 0 skipped, 4 untested
            4 steps passed, 1 failed, 1 skipped, 0 undefined, 8 untested
            """
