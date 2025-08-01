@sequential
Feature: Capture stderr output and show it in case of failures/errors

    As a tester
    To simplify failure diagnostics
    I want that:
      - captured output is displayed only when failures/errors occur
      - all output is displayed when capture is disabled
        (but may clutter up formatter output)

    Background:
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
      And a file named "behave.ini" with:
          """
          [behave]
          capture_stdout = false
          capture_stderr = true
          capture_log = false
          """


  @capture
  @capture_stderr
  Rule: On capture-stderr enabled
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
      But the command output should not contain "stderr:Alice;"


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
      But the command output should not contain "stderr:Alice;"


    Scenario: Captured output is shown up to first failure if scenario fails (CASE 1: --capture)
      When I run "behave -f plain -T --capture features/capture_stderr.example2.feature"
      Then it should fail with:
          """
          0 scenarios passed, 1 failed, 0 skipped
          1 step passed, 1 failed, 1 skipped
          """
      And the command output should contain:
          """
          Feature:
            Scenario:
              Given a step writes "Alice" to stderr and passes ... passed
              When a step writes "Bob" to stderr and fails ... failed
          ASSERT FAILED: XFAIL, step with: Bob;
          """
      And the command output should contain:
          """
          ----
          CAPTURED STDERR: scenario
          stderr:Alice;
          stderr:Bob;
          ----
          """
      But the command output should not contain "stderr:Charly;"


    Scenario: Captured output is shown if scenario fails up to first failure (CASE 2: --capture-stderr)
        When I run "behave -f plain -T --capture-stderr features/capture_stderr.example2.feature"
        Then it should fail with:
            """
            0 scenarios passed, 1 failed, 0 skipped
            1 step passed, 1 failed, 1 skipped
            """
        And the command output should contain:
            """
            Feature:
              Scenario:
                Given a step writes "Alice" to stderr and passes ... passed
                When a step writes "Bob" to stderr and fails ... failed
            ASSERT FAILED: XFAIL, step with: Bob;
            """
        And the command output should contain:
            """
            ----
            CAPTURED STDERR: scenario
            stderr:Alice;
            stderr:Bob;
            ----
            """
        But the command output should not contain "stderr:Charly;"


  @no_capture
  @no_capture_stderr
  Rule: If capture-stderr is disabled
    Scenario: On capture disabled, all output is shown if steps pass (CASE 1)
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
      And the command output should not contain "CAPTURED STDERR:"


    Scenario: On capture disabled, all output is shown until first step fails (CASE 2)
        When I run "behave -f plain -T --no-capture-stderr features/capture_stderr.example2.feature"
        Then it should fail with:
            """
            0 scenarios passed, 1 failed, 0 skipped
            1 step passed, 1 failed, 1 skipped
            """
        And the command output should contain:
            """
            Feature:
              Scenario:
                Given a step writes "Alice" to stderr and passes ... passed
                When a step writes "Bob" to stderr and fails ... failed
            ASSERT FAILED: XFAIL, step with: Bob;
            """
        And the command output should contain:
            """
            stderr:Alice;
            stderr:Bob;
            """
        But the command output should not contain "stderr:Charly;"
        And the command output should not contain "CAPTURED STDERR:"
