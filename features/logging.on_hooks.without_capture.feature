@logging
@without_capture_decorator
Feature: Without @capture decorator on hooks

  As a tester
  I want to use logging in hooks
  So that failure diagnostics are simplified

  . NOTE: Hooks are normally not captured.
  . RELATED FEATURES:
  .  * capture_log.on_hooks.feature
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


    Rule: Without @capture on hook -- Log to file

      Background:
        And a file named "features/environment.py" with:
            """
            from behave.log_capture import capture
            from example4me.fixture import use_fixture_by_tag

            # -- HOOKS:
            def before_all(ctx):
                ctx.config.setup_logging(filename="behave.log")

            # -- DISABLED: @capture
            def before_tag(ctx, tag):
                use_fixture_by_tag(tag)
            """

      Scenario: Without @capture on hook that succeeds -- file sink
        Given a file named "features/no_capture_hook.good.feature" with:
            """
            Feature: Passing

              @good_fixture
              Scenario: Passing -- GOOD
                Given a step passes
                When another step passes
            """
          When I run "behave -f plain --capture-log features/no_capture_hook.good.feature"
          Then it should pass
          And the command output should not contain "CAPTURED LOG:"
          And the command output should contain:
              """
              Feature: Passing
                Scenario: Passing -- GOOD
                  Given a step passes ... passed
                  When another step passes ... passed
              """
          And the file "behave.log" should contain:
              """
              LOG_INFO:example4me: GOOD_FIXTURE: tag=good_fixture
              """
          But note that "logging was captured in the hook but is not shown on success"
          And note that "log-records are contained in log-file"

      Scenario: Without @capture on hook that fails -- file sink
        Given  a file named "features/no_capture_hook.bad.feature" with:
            """
            Feature: Hook error in before_tag hook

              @bad_fixture
              Scenario: Passing -- BAD
                Given a step passes
                When other step passes
            """
          When I run "behave -f plain --capture-log features/no_capture_hook.bad.feature"
          Then it should fail with:
            """
            HOOK-ERROR in before_tag(tag=bad_fixture): RuntimeError: OOPS, BAD_FIXTURE: tag=bad_fixture
            """
          And the command output should contain "CAPTURED LOG:"
          And the command output should contain:
            """
            CAPTURED LOG: before_tag
            LOG_WARNING:example4me: BAD_FIXTURE: tag=bad_fixture
            """
          And the file "behave.log" should contain:
              """
              LOG_WARNING:example4me: BAD_FIXTURE: tag=bad_fixture
              """
          But note that "logging was captured in the hook and is shown on error"
          But note that "log-records are contained in the log-file"



    Rule: Without @capture on hook -- Log to console

      Background:
        And a file named "features/environment.py" with:
            """
            from behave.log_capture import capture
            from example4me.fixture import use_fixture_by_tag

            # -- HOOKS:
            def before_all(ctx):
                ctx.config.setup_logging()

            # -- DISABLED: @capture
            def before_tag(ctx, tag):
                use_fixture_by_tag(tag)
            """

      Scenario: Without @capture on hook that succeeds -- console sink
        Given a file named "features/no_capture_hook.good.feature" with:
            """
            Feature: Passing

              @good_fixture
              Scenario: Passing -- GOOD
                Given a step passes
                When another step passes
            """
          When I run "behave -f plain --capture-log features/no_capture_hook.good.feature"
          Then it should pass
          And the command output should not contain "CAPTURED LOG:"
          And the command output should contain:
              """
              Feature: Passing
                Scenario: Passing -- GOOD
                  Given a step passes ... passed
                  When another step passes ... passed
              """
          But note that "logging was captured in the hook but is not shown on success"


      Scenario: Without @capture on hook that fails -- console sink
        Given  a file named "features/no_capture_hook.bad.feature" with:
            """
            Feature: Hook error in before_tag hook

              @bad_fixture
              Scenario: Passing -- BAD
                Given a step passes
                When other step passes
            """
          When I run "behave -f plain --capture-log features/no_capture_hook.bad.feature"
          Then it should fail with:
            """
            HOOK-ERROR in before_tag(tag=bad_fixture): RuntimeError: OOPS, BAD_FIXTURE: tag=bad_fixture
            """
          And the command output should contain:
              """
               Scenario: Passing -- BAD
              ----
              CAPTURED STDOUT: before_tag
              HOOK-ERROR in before_tag(tag=bad_fixture): RuntimeError: OOPS, BAD_FIXTURE: tag=bad_fixture

              CAPTURED LOG: before_tag
              LOG_WARNING:example4me: BAD_FIXTURE: tag=bad_fixture
              ----
              """
          But note that "logging was captured in the hook and is shown on error"

    Rule: Without @capture on "before_all" hook

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
            def before_all(ctx):
                ctx.config.setup_logging(filename="behave.log")
                use_fixture_by_tag(BEFORE_ALL_TAG)
            """

      Scenario: Use "before_all" hook without error
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

      Scenario: Use "before_all" hook with error

        NOTE: before_all hook is not captured by default.

        Given I set the environment variable "BEFORE_ALL_TAG" to "bad_before_all"
        When I run "behave --capture-log -f plain features/passing.feature"
        Then it should fail with:
            """
            HOOK-ERROR in before_all: RuntimeError: OOPS, BAD_FIXTURE: tag=bad_before_all
            """
        And the command output should not contain:
            """
            CAPTURED LOG:
            LOG_WARNING:example4me: BAD_FIXTURE: tag=bad_before_all
            """
        And the command output should not contain "Traceback"
        And the file "behave.log" should contain:
            """
            LOG_WARNING:example4me: BAD_FIXTURE: tag=bad_before_all
            """
        But note that "captured logs are shown with stacktrace on HOOK-ERROR"

      Scenario: Use "before_all" hook with error and @capture_output

        NOTE: before_all hook is not captured by default.

        Given a file named "features/environment.py" with:
            """
            from behave.capture import capture_output
            from example4me.fixture import use_fixture_by_tag
            import os

            BEFORE_ALL_TAG = os.environ.get("BEFORE_ALL_TAG", "good_before_all")

            # -- HOOKS:
            @capture_output(show_on_success=True)
            def before_all(ctx):
                ctx.config.setup_logging(filename="behave.log")
                use_fixture_by_tag(BEFORE_ALL_TAG)
            """
        And I set the environment variable "BEFORE_ALL_TAG" to "bad_before_all"
        When I run "behave --capture-log -f plain features/passing.feature"
        Then it should fail with:
            """
            HOOK-ERROR in before_all: RuntimeError: OOPS, BAD_FIXTURE: tag=bad_before_all
            """
        And the command output should contain:
            """
            ----
            CAPTURED LOG:
            LOG_WARNING:example4me: BAD_FIXTURE: tag=bad_before_all
            ----
            HOOK-ERROR in before_all: RuntimeError: OOPS, BAD_FIXTURE: tag=bad_before_all
            """
        And the file "behave.log" should contain:
            """
            LOG_WARNING:example4me: BAD_FIXTURE: tag=bad_before_all
            """
        But note that "captured logs are shown with stacktrace on HOOK-ERROR"
