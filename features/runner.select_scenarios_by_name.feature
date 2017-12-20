@sequential
Feature: Select named scenarios to run

    As a tester
    I want to select a subset of all scenarios
    By using their name or parts of the scenario name.

    . SPECIFICATION: When --name option is provided
    .   * Name selection is applied only to scenarios (currently)
    .   * A scenario is selected when scenario name part matches one of the provided names
    .   * Regular expressions can be used to match parts
    .   * If a scenario is not selected, it should be marked as skipped


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
                Scenario: Alice in Wonderland
                    Given a step passes

                Scenario: Alice in Florida
                    When a step passes

                Scenario: Alice in Antarctica
                    Then a step passes
            """
        And a file named "features/bob.feature" with:
            """
            Feature: Bob
                Scenario: Bob in Berlin
                    Given a step passes

                Scenario: Bob in Florida
                    When a step passes

                Scenario: Alice and Bob
                    Then a step passes
            """
        And a file named "behave.ini" with:
            """
            [behave]
            show_skipped = false
            show_timings = false
            """

    Scenario: Select scenarios with name="Alice" and inspect list
        When I run "behave -f plain --name="Alice" --dry-run features/"
        Then it should pass with:
            """
            0 features passed, 0 failed, 0 skipped, 2 untested
            0 scenarios passed, 0 failed, 2 skipped, 4 untested
            0 steps passed, 0 failed, 2 skipped, 0 undefined, 4 untested
            """
        And the command output should contain:
            """
            Feature: Alice
              Scenario: Alice in Wonderland
                  Given a step passes ... untested
              Scenario: Alice in Florida
                  When a step passes ... untested
              Scenario: Alice in Antarctica
                  Then a step passes ... untested

            Feature: Bob
              Scenario: Alice and Bob
                Then a step passes ... untested
            """

    Scenario: Select scenarios with name="Alice" and run them
        When I run "behave -f plain -T --name="Alice" features/"
        Then it should pass with:
            """
            2 features passed, 0 failed, 0 skipped
            4 scenarios passed, 0 failed, 2 skipped
            4 steps passed, 0 failed, 2 skipped, 0 undefined
            """
        And the command output should contain:
            """
            Feature: Alice
              Scenario: Alice in Wonderland
                Given a step passes ... passed
              Scenario: Alice in Florida
                When a step passes ... passed
              Scenario: Alice in Antarctica
                Then a step passes ... passed

            Feature: Bob
              Scenario: Alice and Bob
                Then a step passes ... passed
            """

    Scenario: Select scenarios with name="Bob"
        When I run "behave -f plain --name="Bob" --dry-run features/"
        Then it should pass with:
            """
            0 features passed, 0 failed, 1 skipped, 1 untested
            0 scenarios passed, 0 failed, 3 skipped, 3 untested
            0 steps passed, 0 failed, 3 skipped, 0 undefined, 3 untested
            """
        And the command output should contain:
            """
            Feature: Bob
              Scenario: Bob in Berlin
                Given a step passes ... untested
              Scenario: Bob in Florida
                When a step passes ... untested
              Scenario: Alice and Bob
                Then a step passes ... untested
            """

    Scenario: Select scenarios with name="Florida"
        When I run "behave -f plain --name="Florida" --dry-run features/"
        Then it should pass with:
            """
            0 features passed, 0 failed, 0 skipped, 2 untested
            0 scenarios passed, 0 failed, 4 skipped, 2 untested
            0 steps passed, 0 failed, 4 skipped, 0 undefined, 2 untested
            """
        And the command output should contain:
            """
            Feature: Alice
              Scenario: Alice in Florida
                When a step passes ... untested

            Feature: Bob
              Scenario: Bob in Florida
                When a step passes ... untested
            """

    Scenario: Select scenarios with name that consists of multiple words
        When I run "behave -f plain --name="Alice and Bob" --dry-run features/"
        Then it should pass with:
            """
            0 features passed, 0 failed, 1 skipped, 1 untested
            0 scenarios passed, 0 failed, 5 skipped, 1 untested
            """
        And the command output should contain:
            """
            Feature: Bob
                Scenario: Alice and Bob
            """

    Scenario: Select scenarios by using two names
        When I run "behave -f plain --name="Alice" --name="Florida" --dry-run features/"
        Then it should pass with:
            """
            0 features passed, 0 failed, 0 skipped, 2 untested
            0 scenarios passed, 0 failed, 1 skipped, 5 untested
            0 steps passed, 0 failed, 1 skipped, 0 undefined, 5 untested
            """
        And the command output should contain:
            """
            Feature: Alice
              Scenario: Alice in Wonderland
                Given a step passes ... untested
              Scenario: Alice in Florida
                When a step passes ... untested
              Scenario: Alice in Antarctica
                Then a step passes ... untested

            Feature: Bob
              Scenario: Bob in Florida
                When a step passes ... untested
              Scenario: Alice and Bob
                Then a step passes ... untested
            """

    Scenario: Select scenarios by using a regular expression
        When I run "behave -f plain --name="Alice in .*" --dry-run features/"
        Then it should pass with:
            """
            0 features passed, 0 failed, 1 skipped, 1 untested
            0 scenarios passed, 0 failed, 3 skipped, 3 untested
            """
        And the command output should contain:
            """
            Feature: Alice
              Scenario: Alice in Wonderland
                Given a step passes ... untested
              Scenario: Alice in Florida
                When a step passes ... untested
              Scenario: Alice in Antarctica
                Then a step passes ... untested
            """
        But the command output should not contain:
            """
            Scenario: Bob in
            """

    @not.with_os=win32
    Scenario: Exclude scenarios by using a regular expression (not-pattern)

        Select all scenarios that do not start with "Alice" in its name.
        Exclude all scenarios that start with "Alice" in its name.
        NOTE: Seems to work only for not-start-with idiom.

        When I run "behave -f plain --name='^(?!Alice)' --dry-run features/"
        Then it should pass with:
            """
            0 features passed, 0 failed, 1 skipped, 1 untested
            0 scenarios passed, 0 failed, 4 skipped, 2 untested
            """
        And the command output should contain:
            """
            Feature: Bob
                Scenario: Bob in Berlin
                  Given a step passes ... untested
                Scenario: Bob in Florida
                  When a step passes ... untested
            """
        But the command output should not contain:
            """
            Scenario: Alice
            """

    Scenario: Select scenarios by using another regular expression
        When I run "behave -f plain --name=".* in .*" --dry-run features/"
        Then it should pass with:
            """
            0 features passed, 0 failed, 0 skipped, 2 untested
            0 scenarios passed, 0 failed, 1 skipped, 5 untested
            """
        And the command output should contain:
            """
            Feature: Alice
              Scenario: Alice in Wonderland
                Given a step passes ... untested
              Scenario: Alice in Florida
                When a step passes ... untested
              Scenario: Alice in Antarctica
                Then a step passes ... untested

            Feature: Bob
              Scenario: Bob in Berlin
                Given a step passes ... untested
              Scenario: Bob in Florida
                When a step passes ... untested
            """
        But the command output should not contain:
            """
            Scenario: Alice and Bob
            """

    Scenario: Select scenarios by using two regular expressions
        When I run "behave -f plain --name="Alice in .*" --name="Bob in .*" --dry-run features/"
        Then it should pass with:
            """
            0 features passed, 0 failed, 0 skipped, 2 untested
            0 scenarios passed, 0 failed, 1 skipped, 5 untested
            """
        And the command output should contain:
            """
            Feature: Alice
              Scenario: Alice in Wonderland
                Given a step passes ... untested
              Scenario: Alice in Florida
                When a step passes ... untested
              Scenario: Alice in Antarctica
                Then a step passes ... untested

            Feature: Bob
              Scenario: Bob in Berlin
                Given a step passes ... untested
              Scenario: Bob in Florida
                When a step passes ... untested
            """
        But the command output should not contain:
            """
            Scenario: Alice and Bob
            """

    Scenario: Select scenarios by using an unknown/unused name
        When I run "behave -f plain --name="UNKNOWN" --dry-run features/"
        Then it should pass with:
            """
            0 features passed, 0 failed, 2 skipped
            0 scenarios passed, 0 failed, 6 skipped
            """

    Scenario: Select scenarios with special unicode names
        Given a file named "features/xantippe.feature" with:
          """
          Feature: Use special unicode names

            Scenario: Ärgernis is everywhere
              Given a step passes

            Scenario: Second Ärgernis
              Then a step passes

            Scenario: Something else
              When a step passes
          """
        When I run "behave -f plain --name="Ärgernis" --dry-run features/xantippe.feature"
        Then it should pass with:
          """
          0 features passed, 0 failed, 0 skipped, 1 untested
          0 scenarios passed, 0 failed, 1 skipped, 2 untested
          """
        But the command output should not contain:
          """
          UnicodeDecodeError: 'ascii' codec can't decode byte
          """
