@sequential
Feature: Default paths for features in behave configfile

    As a tester
    I want to specify the default paths for features in the configuration file
    That should be used if none are provided as command-line args
    To support pre-pared/canned test environments
    (and to support my laziness while using behave in a shell).


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
        And a file named "features/alice.feature" with:
            """
            Feature: Alice
                Scenario: A1
                    Given a step passes
                    When a step passes
                    Then a step passes
            """
        And a file named "features/bob.feature" with:
            """
            Feature: Bob
                Scenario: B1
                    When a step passes
            """
        And a file named "more.features/charly.feature" with:
            """
            Feature: Charly
                Scenario: C1
                    Then a step passes
            """
        And a file named "behave.ini" with:
            """
            [behave]
            show_timings = false
            paths = features/bob.feature
                    more.features/charly.feature
            """

    Scenario: Used default paths from behave configfile
        When I run "behave -f plain"
        Then it should pass with:
            """
            2 features passed, 0 failed, 0 skipped
            2 scenarios passed, 0 failed, 0 skipped
            """
        And the command output should contain:
            """
            Feature: Bob
                Scenario: B1
                    When a step passes ... passed

            Feature: Charly
                Scenario: C1
                    Then a step passes ... passed
            """
        But the command output should not contain:
            """
            Feature: Alice
            """

    Scenario: Command-line args can override default paths in configfile
        When I run "behave -f plain features/alice.feature"
        Then it should pass with:
            """
            1 feature passed, 0 failed, 0 skipped
            1 scenario passed, 0 failed, 0 skipped
            3 steps passed, 0 failed, 0 skipped, 0 undefined
             """
        And the command output should contain:
            """
            Feature: Alice
                Scenario: A1
            """
        But the command output should not contain:
            """
            Feature: Bob
            """
        And the command output should not contain:
            """
            Feature: Charly
            """

    Scenario: Command-line args are provided (CASE 2)
        When I run "behave -f plain features"
        Then it should pass with:
            """
            2 features passed, 0 failed, 0 skipped
            2 scenarios passed, 0 failed, 0 skipped
             """
        And the command output should contain:
            """
            Feature: Alice
                Scenario: A1
                    Given a step passes ... passed
                    When a step passes ... passed
                    Then a step passes ... passed

            Feature: Bob
                Scenario: B1
                    When a step passes ... passed
            """
        But the command output should not contain:
            """
            Feature: Charly
            """
