@issue
@mistaken
Feature: Issue 573 Select scenarios fails with empty Scenarios

    @setup
    Scenario: Test Setup
        Given a new working directory
        And a file named "features/steps/steps.py" with:
            """
            from behave import step

            @step('a step passes')
            def step_passes(context):
                pass
            """
        And a file named "features/syndrome.feature" with:
            """
            Feature: Alice
                Scenario: Empty (no steps)

                Scenario: Not Empty (with steps)
                    When a step passes
            """
        And a file named "behave.ini" with:
            """
            [behave]
            show_skipped = false
            show_timings = false
            """

    Scenario: Select scenarios by name in dry-run mode
        When I run "behave -f plain --name="Not Empty \(with steps\)" --dry-run features/"
        Then the command output should contain:
            """
            Feature: Alice
              Scenario: Not Empty (with steps)
                  When a step passes ... untested
            """
        And it should pass with:
            """
            0 features passed, 0 failed, 0 skipped, 1 untested
            0 scenarios passed, 0 failed, 1 skipped, 1 untested
            0 steps passed, 0 failed, 0 skipped, 0 undefined
            """

    Scenario: Select scenarios by name and run them
        When I run "behave -f plain --name="Not Empty \(with steps\)" features/"
        Then the command output should contain:
            """
            Feature: Alice
              Scenario: Not Empty (with steps)
                  When a step passes ... passed
            """
        And it should pass with:
            """
            1 feature passed, 0 failed, 0 skipped
            1 scenario passed, 0 failed, 1 skipped
            1 step passed, 0 failed, 0 skipped, 0 undefined
            """

    Scenario: Select scenarios by name with partial name and run them
        When I run "behave -f plain --name="Not Empty" features/"
        Then the command output should contain:
            """
            Feature: Alice
              Scenario: Not Empty (with steps)
                  When a step passes ... passed
            """
        And it should pass with:
            """
            1 feature passed, 0 failed, 0 skipped
            1 scenario passed, 0 failed, 1 skipped
            1 step passed, 0 failed, 0 skipped, 0 undefined
            """
