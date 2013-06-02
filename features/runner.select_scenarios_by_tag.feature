@sequential
Feature: Select scenarios by using tags

    As a tester
    I want to select a subset of all scenarios by using tags
    (for selecting/including them or excluding them)
    So that I run only a subset of scenarios.

    | RELATED:
    |   * runner.tag_logic.feature


    @setup
    Scenario: Feature Setup
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
              @foo
              Scenario: Alice in Wonderland
                Given a step passes

              @foo
              Scenario: Alice in Florida
                When a step passes

              @bar
              Scenario: Alice in Antarctica
                Then a step passes
            """
        And a file named "features/bob.feature" with:
            """
            Feature: Bob
              @bar
              Scenario: Bob in Berlin
                Given a step passes

              @foo
              Scenario: Bob in Florida
                When a step passes

              Scenario: Alice and Bob
                Then a step passes
            """


    Scenario: Select scenarios with tag=@foo (inclusive)
        When I run "behave -f plain --tags=foo --no-skipped --no-timings features/"
        Then it should pass with:
            """
            2 features passed, 0 failed, 0 skipped
            3 scenarios passed, 0 failed, 3 skipped
            3 steps passed, 0 failed, 3 skipped, 0 undefined
            """
        And the command output should contain:
            """
            Feature: Alice
              Scenario: Alice in Wonderland
                Given a step passes ... passed

              Scenario: Alice in Florida
                When a step passes ... passed

            Feature: Bob
              Scenario: Bob in Florida
                When a step passes ... passed
            """

    Scenario: Select scenarios without tag=@foo (exclusive)

      Use  '-' (minus-sign) or '~' (tilde) in front of the tag-name
      to negate the tag-selection (excluding tags mode).

        When I run "behave -f plain --tags=~@foo --no-skipped --no-timings features/"
        Then it should pass with:
            """
            2 features passed, 0 failed, 0 skipped
            3 scenarios passed, 0 failed, 3 skipped
            3 steps passed, 0 failed, 3 skipped, 0 undefined
            """
        And the command output should contain:
            """
            Feature: Alice

              Scenario: Alice in Antarctica
                Then a step passes ... passed

            Feature: Bob

              Scenario: Bob in Berlin
                Given a step passes ... passed

              Scenario: Alice and Bob
                Then a step passes ... passed
            """


    Scenario: Select scenarios with tag=@foo in dry-run mode (inclusive)

      Ensure that tag-selection works also in dry-run mode.

        When I run "behave -f plain --tags=@foo --dry-run --no-skipped features/"
        Then it should pass with:
            """
            0 features passed, 0 failed, 0 skipped, 2 untested
            0 scenarios passed, 0 failed, 3 skipped, 3 untested
            0 steps passed, 0 failed, 3 skipped, 0 undefined, 3 untested
            """
        And the command output should contain:
            """
            Feature: Alice
              Scenario: Alice in Wonderland
              Scenario: Alice in Florida

            Feature: Bob
              Scenario: Bob in Florida
            """
