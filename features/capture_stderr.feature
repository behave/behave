@sequential
Feature: Capture stderr output and show it in case of failures/errors

    As a tester
    To simplify failure diagnostics
    I want that:
      - captured output is displayed only when failures/errors occur
      - all output is displayed when capture is disabled
        (but may clutter up formatter output)

    @setup
    Scenario: Test Setup
        Given a new working directory
        And   a file named "features/steps/stderr_steps.py" with:
            """
            from behave import step
            import sys

            @step('a step writes "{text}" to stderr and passes')
            def step_writes_to_stderr_and_passes(context, text):
                sys.stderr.write("stderr:%s;\n" % text)

            @step('a step writes "{text}" to stderr and fails')
            def step_writes_to_stderr_and_fails(context, text):
                sys.stderr.write("stderr:%s;\n" % text)
                assert False, "XFAIL, step with: %s;" % text
            """
        And a file named "features/capture_stderr.example1.feature" with:
            """
            Feature:
                Scenario:
                    Given a step writes "Alice" to stderr and passes
                    When a step writes "Bob" to stderr and passes
                    Then a step writes "Charly" to stderr and passes
            """
        And a file named "features/capture_stderr.example2.feature" with:
            """
            Feature:
                Scenario:
                    Given a step writes "Alice" to stderr and passes
                    When a step writes "Bob" to stderr and fails
                    Then a step writes "Charly" to stderr and fails
            """


    @capture
    Scenario: Captured output is suppressed if scenario passes (CASE 1: --capture)
        When I run "behave -f plain -T --capture features/capture_stderr.example1.feature"
        Then it should pass
        And the command output should contain:
            """
            Feature:
                Scenario:
                    Given a step writes "Alice" to stderr and passes ... passed
                    When a step writes "Bob" to stderr and passes ... passed
                    Then a step writes "Charly" to stderr and passes ... passed
            """
        But the command output should not contain:
            """
            stderr:Alice;
            """

    @capture
    Scenario: Captured output is suppressed if scenario passes (CASE 2: --capture-stderr)
        When I run "behave -f plain -T --capture-stderr features/capture_stderr.example1.feature"
        Then it should pass
        And the command output should contain:
            """
            Feature:
                Scenario:
                    Given a step writes "Alice" to stderr and passes ... passed
                    When a step writes "Bob" to stderr and passes ... passed
                    Then a step writes "Charly" to stderr and passes ... passed
            """
        But the command output should not contain:
            """
            stderr:Alice;
            """

    @capture
    Scenario: Captured output is shown up to first failure if scenario fails (CASE 1: --capture)
        When I run "behave -f plain -T --capture features/capture_stderr.example2.feature"
        Then it should fail with:
            """
            0 scenarios passed, 1 failed, 0 skipped
            1 step passed, 1 failed, 1 skipped, 0 undefined
            """
        And the command output should contain:
            """
            Feature:
                Scenario:
                    Given a step writes "Alice" to stderr and passes ... passed
                    When a step writes "Bob" to stderr and fails ... failed
            Assertion Failed: XFAIL, step with: Bob;
            Captured stderr:
            stderr:Alice;
            stderr:Bob;
            """
        But the command output should not contain:
            """
            stderr:Charly;
            """

    @capture
    Scenario: Captured output is shown if scenario fails up to first failure (CASE 2: --capture-stderr)
        When I run "behave -f plain -T --capture-stderr features/capture_stderr.example2.feature"
        Then it should fail with:
            """
            0 scenarios passed, 1 failed, 0 skipped
            1 step passed, 1 failed, 1 skipped, 0 undefined
            """
        And the command output should contain:
            """
            Feature:
                Scenario:
                    Given a step writes "Alice" to stderr and passes ... passed
                    When a step writes "Bob" to stderr and fails ... failed
            Assertion Failed: XFAIL, step with: Bob;
            Captured stderr:
            stderr:Alice;
            stderr:Bob;
            """
        But the command output should not contain:
            """
            stderr:Charly;
            """

    @no_capture
    Scenario: All output is shown when --no-capture-stderr is used and all steps pass (CASE 1)
        When I run "behave -f plain -T --no-capture-stderr features/capture_stderr.example1.feature"
        Then it should pass
        And the command output should contain:
            """
            stderr:Alice;
            stderr:Bob;
            stderr:Charly;
            """
        And the command output should contain:
            """
            Feature:
                Scenario:
                    Given a step writes "Alice" to stderr and passes ... passed
                    When a step writes "Bob" to stderr and passes ... passed
                    Then a step writes "Charly" to stderr and passes ... passed
            """


    @no_capture
    Scenario: All output is shown up to first failing step when --no-capture-stderr is used (CASE 2)
        When I run "behave -f plain -T --no-capture-stderr features/capture_stderr.example2.feature"
        Then it should fail with:
            """
            0 scenarios passed, 1 failed, 0 skipped
            1 step passed, 1 failed, 1 skipped, 0 undefined
            """
        And the command output should contain:
            """
            Feature:
                Scenario:
                    Given a step writes "Alice" to stderr and passes ... passed
                    When a step writes "Bob" to stderr and fails ... failed
            Assertion Failed: XFAIL, step with: Bob;
            """
        And the command output should contain:
            """
            stderr:Alice;
            stderr:Bob;
            """
        But the command output should not contain:
            """
            stderr:Charly;
            """
