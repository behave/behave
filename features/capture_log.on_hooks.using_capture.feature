@logging
@capture
Feature: Capture log output on hooks -- USING: @capture

  As a tester
  I want to capture log output in hooks
  So that failure diagnostics are simplified
  But log-records are only shown when failures/errors occur

  NOTE: No longer needed.
  BETTER USE: --capture-hooks mode or @capture_output decorator

  . SPECIFICATION: @capture decorator on hooks
  .  * Hooks are normally captured now
  .  * USE WITH: "capture_hooks = false" or "--no-capture-hooks" CLI option
  .  * Use @capture decorator on a hook to capture logging
  .  * With @capture decorator, captured records are shown on hook error
  .  * With @capture(show_on_success=True), captured records are always shown
  .
  . RELATED FEATURES:
  .  * capture_log.*.feature
  .  * logging.no_capture.on_hooks.feature
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
        capture_hooks = false
        capture_log = false
        """

    Rule: Use @capture on hook

      NOTE: Captured log-records are only shown if hook fails.

      Background:
        And a file named "features/environment.py" with:
            """
            from behave.log_capture import capture
            from example4me.fixture import use_fixture_by_tag

            # -- HOOKS:
            def before_all(ctx):
                ctx.config.setup_logging(filename="behave.log")

            @capture
            def before_tag(ctx, tag):
                use_fixture_by_tag(tag)
            """

      Scenario: Use @capture on Hook without error
        Given a file named "features/capture_hook.good.feature" with:
            """
            Feature: Passing

              @good_fixture
              Scenario: Passing -- GOOD
                Given a step passes
                When another step passes
            """
        When I run "behave -f plain features/capture_hook.good.feature"
        Then it should pass
        And the command output should not contain "CAPTURED LOG:"
        And the file "behave.log" should contain:
            """
            LOG_INFO:example4me: GOOD_FIXTURE: tag=good_fixture
            """
        But note that "captured logs in hooks are only shown on HOOK-ERROR"

      Scenario: Use @capture on hook with error
        Given  a file named "features/capture_hook.bad.feature" with:
            """
            Feature: Hook error in before_tag hook

              @bad_fixture
              Scenario: Passing -- BAD
                Given a step passes
                When other step passes
            """
        When I run "behave -f plain features/capture_hook.bad.feature"
        Then it should fail
        And the command output should contain:
            """
            CAPTURED LOG:
            LOG_WARNING:example4me: BAD_FIXTURE: tag=bad_fixture
            LOG_ERROR:behave.run: OOPS, BAD_FIXTURE: tag=bad_fixture
            Traceback (most recent call last):
            """
        And the command output should contain:
            """
              File "{__WORKDIR__}/example4me/fixture.py", line 9, in use_bad_fixture
                raise RuntimeError("OOPS, BAD_FIXTURE: tag={}".format(tag))
            RuntimeError: OOPS, BAD_FIXTURE: tag=bad_fixture
            HOOK-ERROR in before_tag(tag=bad_fixture): RuntimeError: OOPS, BAD_FIXTURE: tag=bad_fixture
            """
        And the file "behave.log" should contain:
            """
            LOG_WARNING:example4me: BAD_FIXTURE: tag=bad_fixture
            LOG_ERROR:behave.run: OOPS, BAD_FIXTURE: tag=bad_fixture
            Traceback (most recent call last):
            """
        And the file "behave.log" should contain:
            """
              File "{__WORKDIR__}/example4me/fixture.py", line 9, in use_bad_fixture
                raise RuntimeError("OOPS, BAD_FIXTURE: tag={}".format(tag))
            RuntimeError: OOPS, BAD_FIXTURE: tag=bad_fixture
          """

    Rule: Use @capture(show_on_success=true) on hook
      NOTE: Captured log-records are always shown.

      Background:
        And a file named "features/environment.py" with:
            """
            from behave.log_capture import capture
            from example4me.fixture import use_fixture_by_tag

            # -- HOOKS:
            def before_all(ctx):
                ctx.config.setup_logging(filename="behave.log")

            @capture(show_on_success=True)
            def before_tag(ctx, tag):
                use_fixture_by_tag(tag)
            """

      Scenario: Use @capture(show_on_success) on hook without error

        NOTE: Captured logs are always shown in this case, even on success.

        Given a file named "features/capture_hook.good.feature" with:
            """
            Feature: Passing

              @good_fixture
              Scenario: Passing -- GOOD
                Given a step passes
                When another step passes
            """
        When I run "behave -f plain features/capture_hook.good.feature"
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

    Rule: Use @capture on "before_all" hook

      Background:
        And a file named "features/passing.feature" with:
            """
            Feature: Passing
              Scenario: Passing
                Given a step passes
                When some step passes
            """
        And a file named "features/environment.py" with:
            """
            from behave.log_capture import capture
            from example4me.fixture import use_fixture_by_tag
            import os

            BEFORE_ALL_TAG = os.environ.get("BEFORE_ALL_TAG", "good_before_all")

            # -- HOOKS:
            @capture
            def before_all(ctx):
                ctx.config.setup_logging(filename="behave.log")
                use_fixture_by_tag(BEFORE_ALL_TAG)
            """

      Scenario: Use @capture on "before_all" hook without error
        Given I set the environment variable "BEFORE_ALL_TAG" to "good_before_all"
        When I run "behave -f plain features/passing.feature"
        Then it should pass
        And the command output should not contain "CAPTURED LOG:"
        And the file "behave.log" should contain:
            """
            LOG_INFO:example4me: GOOD_FIXTURE: tag=good_before_all
            """
        And the file "behave.log" should not contain "Traceback"
        But note that "captured logs are shown on HOOK-ERROR"


      Scenario: Use @capture on "before_all" hook with error
        Given I set the environment variable "BEFORE_ALL_TAG" to "bad_before_all"
        When I run "behave -f plain features/passing.feature"
        Then it should fail with:
            """
            HOOK-ERROR in before_all: RuntimeError: OOPS, BAD_FIXTURE: tag=bad_before_all
            """
        And the command output should contain:
            """
            CAPTURED LOG:
            LOG_WARNING:example4me: BAD_FIXTURE: tag=bad_before_all
            LOG_ERROR:behave.run: OOPS, BAD_FIXTURE: tag=bad_before_all
            """
        And the command output should contain "Traceback"
        And the command output should contain:
            """
            File "features/environment.py", line 11, in before_all
              use_fixture_by_tag(BEFORE_ALL_TAG)
            """
        And the command output should contain:
            """
            File "{__WORKDIR__}/example4me/fixture.py", line 9, in use_bad_fixture
              raise RuntimeError("OOPS, BAD_FIXTURE: tag={}".format(tag))
            RuntimeError: OOPS, BAD_FIXTURE: tag=bad_before_all
            """
        And the file "behave.log" should contain:
            """
            LOG_WARNING:example4me: BAD_FIXTURE: tag=bad_before_all
            """
        And the file "behave.log" should contain:
            """
            LOG_ERROR:behave.run: OOPS, BAD_FIXTURE: tag=bad_before_all
            Traceback (most recent call last):
            """
        And the file "behave.log" should contain:
            """
              File "{__WORKDIR__}/example4me/fixture.py", line 9, in use_bad_fixture
                raise RuntimeError("OOPS, BAD_FIXTURE: tag={}".format(tag))
            RuntimeError: OOPS, BAD_FIXTURE: tag=bad_before_all
            """
        But note that "captured logs are shown with stacktrace on HOOK-ERROR"
