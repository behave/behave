@sequential
Feature: Rerun Formatter

    To simplify to run the scenarios that have failed during the last test run
    As a tester
    I want that behave generates the necessary information for me.

    . SOLUTION:
    .
    .   Put RerunFormatter into "behave.ini" configuration file:
    .
    .       # -- file:behave.ini
    .       [behave]
    .       format   = rerun
    .       outfiles = rerun.txt
    .
    .   Then a "rerun.txt" file is generated during each test run
    .   that contains the file locations of the failing scenarios, like:
    .
    .       # -- file:rerun.txt
    .       # RERUN: Failing scenarios during last test run.
    .       features/alice.feature:10
    .       features/alice.feature:42
    .
    .   To rerun the failing scenarios of the last test run, use:
    .
    .       behave @rerun.txt


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
                assert False, "XFAIL-STEP"
            """
        And a file named "features/alice.feature" with:
            """
            Feature: Alice

              Scenario: Passing
                Given a step passes
                When a step passes
                Then a step passes

              @xfail
              Scenario: When-step fails
                Given a step passes
                When a step fails
                Then a step passes

              @xfail
              Scenario: Then-step fails
                Given a step passes
                When a step passes
                Then a step fails
            """
        And a file named "features/bob.feature" with:
            """
            Feature: Bob

              @xfail
              Scenario: Failing early
                Given a step fails
                When a step passes
                Then a step fails

              Scenario: Passing
                Given a step passes

              @xfail
              Scenario: Failing
                When a step passes
                Then a step fails
            """

    @usecase.step1
    Scenario: Rerun file is generated when failures occur
        When I run "behave -f rerun -o rerun.txt -f plain -T features/"
        Then it should fail with:
            """
            0 features passed, 2 failed, 0 skipped
            2 scenarios passed, 4 failed, 0 skipped
            """
        And the command output should contain:
            """
            Failing scenarios:
              features/alice.feature:9  When-step fails
              features/alice.feature:15  Then-step fails
              features/bob.feature:4  Failing early
              features/bob.feature:13  Failing
            """
        And the file "rerun.txt" should contain:
            """
            # -- RERUN: 4 failing scenarios during last test run.
            features/alice.feature:9
            features/alice.feature:15
            features/bob.feature:4
            features/bob.feature:13
            """

    @usecase.step2
    Scenario: Use rerun file during next test run to test only failing scenarios
        Given a file named "rerun.txt" with:
            """
            # -- RERUN: 4 failing scenarios during last test run.
            features/alice.feature:9
            features/alice.feature:15
            features/bob.feature:4
            features/bob.feature:13
            """
        When I run "behave -f plain -T --no-skipped @rerun.txt"
        Then it should fail with:
            """
            0 features passed, 2 failed, 0 skipped
            0 scenarios passed, 4 failed, 2 skipped
            """
        And the command output should contain:
            """
            Feature: Alice

              Scenario: When-step fails
                Given a step passes ... passed
                When a step fails ... failed
            Assertion Failed: XFAIL-STEP

              Scenario: Then-step fails
                Given a step passes ... passed
                When a step passes ... passed
                Then a step fails ... failed
            Assertion Failed: XFAIL-STEP

            Feature: Bob

              Scenario: Failing early
                Given a step fails ... failed
            Assertion Failed: XFAIL-STEP

              Scenario: Failing
                When a step passes ... passed
                Then a step fails ... failed
            Assertion Failed: XFAIL-STEP
            """
        And the command output should contain:
            """
            Failing scenarios:
              features/alice.feature:9  When-step fails
              features/alice.feature:15  Then-step fails
              features/bob.feature:4  Failing early
              features/bob.feature:13  Failing
            """


    Scenario: Rerun file is deleted when no failures occur

      The rerun output file should be deleted
      if the test run was successful and no failures occurred.

        Given an empty file named "rerun.txt"
        When I run "behave -f rerun -o rerun.txt -f plain -T --no-skipped --tags=~@xfail features/"
        Then it should pass with:
            """
            2 features passed, 0 failed, 0 skipped
            2 scenarios passed, 0 failed, 4 skipped
            """
        And a file named "rerun.txt" should not exist


    Scenario: Use RerunFormatter with output=stdout
        When I run "behave -f rerun -f plain -T --no-skipped features/"
        Then it should fail with:
            """
            0 features passed, 2 failed, 0 skipped
            2 scenarios passed, 4 failed, 0 skipped
                 """
        And the command output should contain:
            """
            # -- RERUN: 4 failing scenarios during last test run.
            features/alice.feature:9
            features/alice.feature:15
            features/bob.feature:4
            features/bob.feature:13
            """


    @with.behave_configfile
    Scenario: Use rerun file with RerunFormatter in behave configuration file
        Given a file named "behave.ini" with:
            """
            [behave]
            format   = rerun
            outfiles = rerun.txt
            show_timings = false
            show_skipped = false
            """
        When I run "behave -f plain features/"
        Then it should fail with:
            """
            0 features passed, 2 failed, 0 skipped
            2 scenarios passed, 4 failed, 0 skipped
            """
        And the file "rerun.txt" should contain:
            """
            # -- RERUN: 4 failing scenarios during last test run.
            features/alice.feature:9
            features/alice.feature:15
            features/bob.feature:4
            features/bob.feature:13
            """
        When I run "behave -f plain @rerun.txt"
        Then it should fail with:
            """
            0 features passed, 2 failed, 0 skipped
            0 scenarios passed, 4 failed, 2 skipped
            """
        And the command output should contain:
            """
            Feature: Alice

              Scenario: When-step fails
                Given a step passes ... passed
                When a step fails ... failed
            Assertion Failed: XFAIL-STEP

              Scenario: Then-step fails
                Given a step passes ... passed
                When a step passes ... passed
                Then a step fails ... failed
            Assertion Failed: XFAIL-STEP

            Feature: Bob

              Scenario: Failing early
                Given a step fails ... failed
            Assertion Failed: XFAIL-STEP

              Scenario: Failing
                When a step passes ... passed
                Then a step fails ... failed
            Assertion Failed: XFAIL-STEP
            """
        And the file "rerun.txt" should contain:
            """
            # -- RERUN: 4 failing scenarios during last test run.
            features/alice.feature:9
            features/alice.feature:15
            features/bob.feature:4
            features/bob.feature:13
            """

    @sad.case
    @with.behave_configfile
    Scenario: Two RerunFormatter use same output file
        Given a file named "behave.ini" with:
            """
            [behave]
            format   = rerun
            outfiles = rerun.txt
            """
        When I run "behave -f rerun -o rerun.txt -f plain features/"
        Then it should fail with:
            """
            0 features passed, 2 failed, 0 skipped
            2 scenarios passed, 4 failed, 0 skipped
            """
        And the file "rerun.txt" should contain:
            """
            # -- RERUN: 4 failing scenarios during last test run.
            features/alice.feature:9
            features/alice.feature:15
            features/bob.feature:4
            features/bob.feature:13
            """
        But the file "rerun.txt" should not contain:
            """
            # -- RERUN: 4 failing scenarios during last test run.
            features/alice.feature:9
            features/alice.feature:15
            features/bob.feature:4
            features/bob.feature:13

            # -- RERUN: 4 failing scenarios during last test run.
            features/alice.feature:9
            features/alice.feature:15
            features/bob.feature:4
            features/bob.feature:13
            """
        And note that "the second RerunFormatter overwrites the output of the first one"

    @with.behave_configfile
    Scenario: RerunFormatter with steps-catalog
        Given a file named "behave.ini" with:
            """
            [behave]
            format   = rerun
            outfiles = rerun.txt
            """
        When I run "behave --steps-catalog features/"

        Then it should pass with:
            """
            Given a step passes
            """
        And a file named "rerun.txt" does not exist

