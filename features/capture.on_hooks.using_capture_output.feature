@logging
@capture
Feature: Capture output on Hooks -- USING: @capture_output

  As a tester
  I want to capture stdout/stderr/log output in hooks
  So that failure diagnostics are simplified
  But captured output is only shown when failures/errors occur

  . SPECIFICATION: @capture decorator on hooks
  .  * Hooks are normally already captured
  .  * USE: "behave --no-capture-hooks" on command line
  .  * USE: "capture_hooks = false" in "behave.ini" config-file
  .  * Use @capture_output decorator on a hook to capture output
  .  * With @capture_output decorator, captured output is shown on hook error
  .  * With @capture_output(show_on_success=True), captured output is always shown
  .  * REQUIRES: Some capture mode is enabled (default)
  .
  . RELATED FEATURES:
  .  * capture_log.on_hooks.feature
  .  * logging.no_capture.on_hooks.feature
  .  * capture_log.*.feature
  .  * logging.*.feature

  Background:
    Given a new working directory
    And a file named "features/steps/use_behave4cmd_steps.py" with:
        """
        import behave4cmd0.log_steps
        import behave4cmd0.failing_steps
        import behave4cmd0.passing_steps
        """
    And an empty file named "example4me/__init__.py"
    And a file named "example4me/fixture.py" with:
        """
        import logging
        logger = logging.getLogger("example4me")

        def use_good_fixture(tag):
            logger.info("GOOD_FIXTURE: tag={}".format(tag))

        def use_bad_fixture(tag):
            logger.warn("BAD_FIXTURE: tag={}".format(tag))
            raise RuntimeError("OOPS, BAD_FIXTURE: tag={}".format(tag))

        def use_fixture_by_tag(tag):
            if tag.startswith("bad_"):
                use_bad_fixture(tag)
            elif tag.startswith("good_"):
                use_good_fixture(tag)
        """
    And a file named "behave.ini" with:
        """
        [behave]
        capture = true
        capture_hooks = false
        """

    Rule: Use @capture_output on hook

      NOTE: Captured log-records are only shown if hook fails.

      Background:
        And a file named "features/environment.py" with:
            """
            from behave.capture import capture_output
            from example4me.fixture import use_fixture_by_tag

            # -- HOOKS:
            def before_all(ctx):
                ctx.config.setup_logging(filename="behave.log")

            @capture_output
            def before_tag(ctx, tag):
                use_fixture_by_tag(tag)
            """

      Scenario: Use @capture_output on Hook without error
        Given a file named "features/capture_hook.good.feature" with:
            """
            Feature: Passing

              @good_fixture
              Scenario: Passing -- GOOD
                Given a step passes
                When another step passes
            """
        When I run "behave -f plain --capture-log features/capture_hook.good.feature"
        Then it should pass
        And the command output should not contain "CAPTURED LOG:"
        And the file "behave.log" should contain:
            """
            LOG_INFO:example4me: GOOD_FIXTURE: tag=good_fixture
            """
        But note that "captured logs in hooks are only shown on HOOK-ERROR"

      Scenario: Use @capture_output on hook with error
        Given  a file named "features/capture_hook.bad.feature" with:
            """
            Feature: Hook error in before_tag hook

              @bad_fixture
              Scenario: Passing -- BAD
                Given a step passes
                When other step passes
            """
        When I run "behave -f plain --capture-log features/capture_hook.bad.feature"
        Then it should fail
        And the command output should contain:
            """
            CAPTURED LOG:
            LOG_WARNING:example4me: BAD_FIXTURE: tag=bad_fixture
            """
        And the command output should contain:
            """
            HOOK-ERROR in before_tag(tag=bad_fixture): RuntimeError: OOPS, BAD_FIXTURE: tag=bad_fixture
            """
        And the file "behave.log" should contain:
            """
            LOG_WARNING:example4me: BAD_FIXTURE: tag=bad_fixture
            """
        And the file "behave.log" should not contain "Traceback"


    Rule: Use @capture_output(show_on_success=true) on hook
      NOTE: Captured log-records are always shown.

      Scenario: Use @capture_output(show_on_success) on hook without error

        NOTE: Captured output are always shown in this case, even on success.

        Given a file named "features/environment.py" with:
            """
            from behave.capture import capture_output
            from example4me.fixture import use_fixture_by_tag

            # -- HOOKS:
            def before_all(ctx):
                ctx.config.setup_logging(filename="behave.log")

            @capture_output(show_on_success=True)
            def before_tag(ctx, tag):
                use_fixture_by_tag(tag)
            """
        And a file named "features/capture_hook.good.feature" with:
            """
            Feature: Passing

              @good_fixture
              Scenario: Passing -- GOOD
                Given a step passes
                When another step passes
            """
        When I run "behave -f plain --no-capture-hooks features/capture_hook.good.feature"
        Then it should pass
        And the command output should contain:
          """
          CAPTURED LOG:
          LOG_INFO:example4me: GOOD_FIXTURE: tag=good_fixture
          """
        And the file "behave.log" should contain:
            """
            LOG_INFO:example4me: GOOD_FIXTURE: tag=good_fixture
            """
        But note that "captured logs in hooks are shown on HOOK-SUCCESS"

    Rule: Use @capture_output on "before_all" hook

      Background:
        Given a file named "features/passing.feature" with:
            """
            Feature: Passing
              Scenario: Passing
                Given a step passes
                When some step passes
            """
        And a file named "features/environment.py" with:
            """
            from behave.capture import capture_output
            from example4me.fixture import use_fixture_by_tag
            import os

            BEFORE_ALL_TAG = os.environ.get("BEFORE_ALL_TAG", "good_before_all")

            # -- HOOKS:
            @capture_output
            def before_all(ctx):
                ctx.config.setup_logging(filename="behave.log")
                use_fixture_by_tag(BEFORE_ALL_TAG)
            """

      Scenario: Use @capture_output on "before_all" hook without error
        Given I set the environment variable "BEFORE_ALL_TAG" to "good_before_all"
        When I run "behave -f plain --capture-log features/passing.feature"
        Then it should pass
        And the command output should not contain "CAPTURED LOG:"
        And the file "behave.log" should contain:
            """
            LOG_INFO:example4me: GOOD_FIXTURE: tag=good_before_all
            """
        And the file "behave.log" should not contain "Traceback"
        But note that "captured logs are shown on HOOK-ERROR"

      Scenario: Use @capture_output on "before_all" hook with error
        Given I set the environment variable "BEFORE_ALL_TAG" to "bad_before_all"
        When I run "behave -f plain --capture-log features/passing.feature"
        Then it should fail
        And the command output should contain:
            """
            CAPTURED LOG:
            LOG_WARNING:example4me: BAD_FIXTURE: tag=bad_before_all
            """
        And the command output should contain:
            """
            HOOK-ERROR in before_all: RuntimeError: OOPS, BAD_FIXTURE: tag=bad_before_all
            """
        And the command output should not contain "Traceback"
        And the file "behave.log" should contain:
            """
            LOG_WARNING:example4me: BAD_FIXTURE: tag=bad_before_all
            """
        And the file "behave.log" should not contain "Traceback"
        But note that "captured output contains no stacktrace on HOOK-ERROR"

      Scenario: Use @capture_output on "before_all" hook with error (verbose mode)
        Given I set the environment variable "BEFORE_ALL_TAG" to "bad_before_all"
        When I run "behave -f plain --verbose features/passing.feature"
        Then it should fail
        And the command output should contain:
            """
            CAPTURED LOG:
            LOG_WARNING:example4me: BAD_FIXTURE: tag=bad_before_all
            """
        And the command output should contain:
            """
            HOOK-ERROR in before_all: RuntimeError: OOPS, BAD_FIXTURE: tag=bad_before_all
            """
        And the command output should contain:
            """
            File "{__WORKDIR__}/example4me/fixture.py", line 9, in use_bad_fixture
              raise RuntimeError("OOPS, BAD_FIXTURE: tag={}".format(tag))
            """
        And the file "behave.log" should contain:
            """
            LOG_WARNING:example4me: BAD_FIXTURE: tag=bad_before_all
            """
        But note that "captured output contains stacktraces on HOOK-ERROR in verbose mode"
