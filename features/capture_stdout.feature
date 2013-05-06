@sequential
Feature: Capture stdout output and show it in case of failures/errors

    As a tester
    To simplify failure diagnostics
    I want that:
      - captured output is displayed only when failures/errors occur
      - all output is displayed when capture is disabled
        (but may clutter up formatter output)


    @setup
    Scenario: Test Setup
        Given a new working directory
        And a file named "features/steps/stdout_steps.py" with:
            """
            from behave import step
            import sys

            @step('a step writes "{text}" to stdout and passes')
            def step_writes_to_stdout_and_passes(context, text):
                sys.stdout.write("stdout:%s;\n" % text)

            @step('a step writes "{text}" to stdout and fails')
            def step_writes_to_stdout_and_fails(context, text):
                sys.stdout.write("stdout:%s;\n" % text)
                assert False, "XFAIL, step with: %s;" % text
            """
        And a file named "features/capture_stdout.example1.feature" with:
            """
            Feature:
                Scenario:
                    Given a step writes "Alice" to stdout and passes
                    When a step writes "Bob" to stdout and passes
                    Then a step writes "Charly" to stdout and passes
            """
        And a file named "features/capture_stdout.example2.feature" with:
            """
            Feature:
                Scenario:
                    Given a step writes "Alice" to stdout and passes
                    When a step writes "Bob" to stdout and fails
                    Then a step writes "Charly" to stdout and fails
            """


    @capture
    Scenario: Captured output is suppressed if scenario passes
        When I run "behave -f plain -T --capture features/capture_stdout.example1.feature"
        Then it should pass
        And the command output should contain:
            """
            Feature:
                Scenario:
                    Given a step writes "Alice" to stdout and passes ... passed
                    When a step writes "Bob" to stdout and passes ... passed
                    Then a step writes "Charly" to stdout and passes ... passed
            """
        But the command output should not contain:
            """
            stdout:Alice;
            """

    @capture
    Scenario: Captured output is shown up to first failure if scenario fails
        When I run "behave -f plain -T --capture features/capture_stdout.example2.feature"
        Then it should fail with:
            """
            0 scenarios passed, 1 failed, 0 skipped
            1 step passed, 1 failed, 1 skipped, 0 undefined
            """
        And the command output should contain:
            """
            Feature:
                Scenario:
                    Given a step writes "Alice" to stdout and passes ... passed
                    When a step writes "Bob" to stdout and fails ... failed
            Assertion Failed: XFAIL, step with: Bob;
            Captured stdout:
            stdout:Alice;
            stdout:Bob;
            """
        But the command output should not contain:
            """
            stdout:Charly;
            """

    @no_capture
    Scenario: All output is shown when --no-capture is used and all steps pass (CASE 1)
        When I run "behave -f plain -T --no-capture features/capture_stdout.example1.feature"
        Then it should pass
        And the command output should contain:
            """
            Feature:
                Scenario:
                    stdout:Alice;
                    Given a step writes "Alice" to stdout and passes ... passed
                    stdout:Bob;
                    When a step writes "Bob" to stdout and passes ... passed
                    stdout:Charly;
                    Then a step writes "Charly" to stdout and passes ... passed
            """


    @no_capture
    Scenario: All output is shown up to first failing step when --no-capture is used (CASE 2)
        When I run "behave -f plain -T --no-capture features/capture_stdout.example2.feature"
        Then it should fail with:
            """
            0 scenarios passed, 1 failed, 0 skipped
            1 step passed, 1 failed, 1 skipped, 0 undefined
            """
        And the command output should contain:
            """
            Feature:
                Scenario:
                    stdout:Alice;
                    Given a step writes "Alice" to stdout and passes ... passed
                    stdout:Bob;
                    When a step writes "Bob" to stdout and fails ... failed
            """
        But the command output should not contain:
            """
            stdout:Charly;
            """
