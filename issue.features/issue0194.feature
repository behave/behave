@issue
Feature: Issue #194: Nested steps prevent that original stdout/stderr is restored

  . When nested steps are used,
  . the original stdout/stderr streams are not restored after the scenario.
  . This is caused by starting/stopping capture again while executing nested steps.
  .
  . ENSURE THAT:
  .   * Original streams are restored in after_scenario() hook.
  .   * Nested steps should not replace existing capture objects.

  @setup
  Scenario: Feature Setup
    Given a new working directory
    And a file named "behave.ini" with:
        """
        [behave]
        log_capture = false
        logging_level  = INFO
        logging_format = LOG.%(levelname)-8s  %(name)s: %(message)s
        """
    And a file named "features/steps/use_behave4cmd_steps.py" with:
        """
        import behave4cmd0.passing_steps
        import behave4cmd0.failing_steps
        import behave4cmd0.note_steps
        """
    And a file named "features/steps/stdout_steps.py" with:
        """
        from behave import given, when, then, step, matchers
        import parse
        import sys

        # -- USER-DEFINED DATA TYPES:
        @parse.with_pattern(r"stdout|stderr")
        def parse_stream_name(text):
            assert text in ("stdout", "stderr")
            return text

        matchers.register_type(StreamName=parse_stream_name)

        # -- UTILITY FUNCTIONS:
        def write_text_to(stream, text, enforce_newline=True):
            if enforce_newline and not text.endswith("\n"):
                text += "\n"
            stream.write(text)

        # -- STEP DEFINITIONS:
        @step('I write "{text}" to {stream_name:StreamName}')
        def step_write_text_to_stdxxx(context, text, stream_name):
            stream = getattr(sys, stream_name)
            write_text_to(stream, text)

        @step('I execute the following steps')
        def step_execute_steps(context):
            assert context.text, "REQUIRE: context.text"
            context.execute_steps(context.text)
            sys.stdout.write("STDOUT:AFTER-EXECUTE-STEPS\n")
            sys.stderr.write("STDERR:AFTER-EXECUTE-STEPS\n")
        """
    And a file named "features/environment.py" with:
        """
        import sys

        stdout_id = 0
        stderr_id = 0

        def stdout_print(text):
            sys.__stdout__.write(text + "\n")

        def inspect_stdout(context, scope, statement):
            global stdout_id
            stream_id = id(sys.stdout)
            stream_class = sys.stdout.__class__.__name__
            expected_id = stdout_id
            if stream_id != expected_id:
                name = statement.name
                stdout_print("CHANGED-STDOUT %s:%s: stream.id=%s:%d (was: %d)" % \
                            (scope, name, stream_class, stream_id, expected_id))
                stdout_id = stream_id

        def inspect_stderr(context, scope, statement):
            global stderr_id
            stream_id = id(sys.stderr)
            stream_class = sys.stderr.__class__.__name__
            expected_id = stderr_id
            if stream_id != expected_id:
                name = statement.name
                stdout_print("CHANGED-STDERR %s:%s: stream.id=%s:%d (was: %d)" % \
                            (scope, name, stream_class, stream_id, expected_id))
                stderr_id = stream_id

        def inspect_stdxxx(context, scope, statement):
            inspect_stdout(context, scope, statement)
            inspect_stderr(context, scope, statement)

        def before_all(context):
            context.config.setup_logging(filename="behave.log")

        def before_scenario(context, scenario):
            inspect_stdxxx(context, "before_scenario", scenario)

        def after_scenario(context, scenario):
            inspect_stdxxx(context, "after_scenario", scenario)
            # -- ENSURE: Original streams are restored.
            assert sys.stdout is sys.__stdout__
            assert sys.stderr is sys.__stderr__
            stdout_print("AFTER-SCENARIO %s: Streams are restored." % scenario.name)

        def before_step(context, step):
            inspect_stdxxx(context, "before_step", step)

        def after_step(context, step):
            inspect_stdxxx(context, "after_step", step)
        """

  Scenario: Stdout capture works with nested steps
    Given a file named "features/stdout.failing_with_nested.feature" with
        """
        Feature:
          Scenario: Failing with nested steps
            Given I write "STDOUT:Hello Alice" to stdout
            When  I write "STDOUT:Hello Bob" to stdout
            Then  I execute the following steps:
              '''
              * I write "STDOUT:Hello nested.Alice" to stdout
              * I write "STDOUT:Hello nested.Bob" to stdout
              '''
            And I write "STDOUT:Hello Charly" to stdout
            And another step fails

          Scenario: Another failing
            Given I write "STDOUT:Hello Dora" to stdout
            And another step fails
        """
    When I run "behave -f plain features/stdout.failing_with_nested.feature"
    Then it should fail with:
        """
        0 scenarios passed, 2 failed, 0 skipped
        5 steps passed, 2 failed, 0 skipped, 0 undefined
        """
    And note that "the summary is only shown if hooks have no errors"
    And the command output should contain:
        """
        Captured stdout:
        STDOUT:Hello Alice
        STDOUT:Hello Bob
        STDOUT:Hello nested.Alice
        STDOUT:Hello nested.Bob
        STDOUT:AFTER-EXECUTE-STEPS
        STDOUT:Hello Charly
        """
    And the command output should contain:
        """
        Captured stdout:
        STDOUT:Hello Dora
        """
    And the command output should contain:
        """
        AFTER-SCENARIO Failing with nested steps: Streams are restored.
        """
    And the command output should contain:
        """
        AFTER-SCENARIO Another failing: Streams are restored.
        """

  Scenario: Stderr capture works with nested steps
    Given a file named "features/stderr.failing_with_nested.feature" with
        """
        Feature:
          Scenario: Failing with nested steps
            Given I write "STDERR:Hello Alice" to stderr
            When  I write "STDERR:Hello Bob" to stderr
            Then  I execute the following steps:
              '''
              * I write "STDERR:Hello nested.Alice" to stderr
              * I write "STDERR:Hello nested.Bob" to stderr
              '''
            And I write "STDERR:Hello Charly" to stderr
            And another step fails

          Scenario: Another failing
            Given I write "STDERR:Hello Dora" to stderr
            And another step fails
        """
    When I run "behave -f plain features/stderr.failing_with_nested.feature"
    Then it should fail with:
        """
        0 scenarios passed, 2 failed, 0 skipped
        5 steps passed, 2 failed, 0 skipped, 0 undefined
        """
    And note that "the summary is only shown if hooks have no errors"
    And the command output should contain:
        """
        Captured stderr:
        STDERR:Hello Alice
        STDERR:Hello Bob
        STDERR:Hello nested.Alice
        STDERR:Hello nested.Bob
        STDERR:AFTER-EXECUTE-STEPS
        STDERR:Hello Charly
        """
    And the command output should contain:
        """
        Captured stderr:
        STDERR:Hello Dora
        """
    And the command output should contain:
        """
        AFTER-SCENARIO Failing with nested steps: Streams are restored.
        """
    And the command output should contain:
        """
        AFTER-SCENARIO Another failing: Streams are restored.
        """
