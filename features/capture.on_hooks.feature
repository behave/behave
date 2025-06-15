@logging
@capture
Feature: Capture output on Hooks -- USING: capture_hooks=true

  As a tester
  I want to capture stdout/stderr/log output in hooks
  So that failure diagnostics are simplified
  But captured output is only shown when failures/errors occur

  . SPECIFICATION: capture_hooks = true (default now)
  .  * REQUIRES: Some capture-mode must be enabled: stdout/stderr/log
  .  * USE: "behave --capture-hooks" on command line
  .  * USE: "capture_hooks = true" in config-file
  .
  . DETAILS:
  .  * All hooks except "before_all" are captured.
  .  * Use "@capture_output" decorator on "before_all" hook (if needed)
  .  * Captured output is only shown if a HOOK-ERROR occurs (by default)
  .
  . ASPECT: Show HOOK-ERROR Details -- Stacktrace/Traceback
  .  * HOOK-ERROR Details are normally disabled.
  .  * Use verbose mode to enable that the stacktrace is shown.
  .
  . ASPECT: Show captured output on success
  .  * Use "<HOOK_FUNCTION>.show_capture_on_success = True"
  .  * Use "any_hook.show_capture_on_success = True" (module: behave.capture)
  .
  . ASPECT: Show captured cleanup output on success
  .  * Use "any_hook.show_cleanup_on_success = True" (module: behave.capture)
  .
  . RELATED FEATURES:
  .  * capture_log.on_hooks.feature
  .  * logging.on_hooks.without_capture.feature
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

        def use_special_fixture_by_tag(tag):
            if tag.startswith("bad_"):
                use_bad_fixture(tag)
            elif tag.startswith("good_"):
                use_good_fixture(tag)
        """
    And a file named "behave.ini" with:
        """
        [behave]
        capture = true
        capture_hooks = true
        """

    Rule: Use capture-hooks

      NOTE: Captured output is only shown on HOOK-ERROR(s).

      Background:
        Given a file named "features/environment.py" with:
            """
            from behave.capture import capture_output
            from example4me.fixture import use_special_fixture_by_tag

            # -- HOOKS:
            def before_all(ctx):
                ctx.config.setup_logging(filename="behave.log")

            # XXX_DISABLED: @capture_output
            def before_tag(ctx, tag):
                use_special_fixture_by_tag(tag)
            """

      Scenario: Use capture-hooks on Hook without error
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

      Scenario: Use capture-hooks on hook with error
        Given  a file named "features/capture_hook.bad.feature" with:
            """
            Feature: Hook error in before_tag hook

              @bad_fixture
              Scenario: Passing -- BAD
                Given a step passes
                When other step passes
            """
        When I run "behave -f plain --capture features/capture_hook.bad.feature"
        Then it should fail
        And the command output should contain:
            """
            CAPTURED LOG: before_tag
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


    Rule: Use show_capture_on_success=true
      NOTE: Captured output is always shown on one hook/any_hook.

      Scenario: Use show_on_success on one hook without error
        Given a file named "features/environment.py" with:
            """
            from example4me.fixture import use_special_fixture_by_tag

            # -- HOOKS:
            def before_all(ctx):
                ctx.config.setup_logging(filename="behave.log")

            def before_tag(ctx, tag):
                use_special_fixture_by_tag(tag)

            def after_scenario(ctx, scenario):
                print("HOOK: after_scenario -- {}".format(scenario.name))

            before_tag.show_capture_on_success = True
            """
        And a file named "features/capture_hook.good.feature" with:
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
          CAPTURED LOG: before_tag
          LOG_INFO:example4me: GOOD_FIXTURE: tag=good_fixture
          """
        And the file "behave.log" should contain:
            """
            LOG_INFO:example4me: GOOD_FIXTURE: tag=good_fixture
            """
        But note that "captured logs in hooks are shown on HOOK-SUCCESS"
        And the command output should contain:
            """
              Scenario: Passing -- GOOD
            ----
            CAPTURED LOG: before_tag
            LOG_INFO:example4me: GOOD_FIXTURE: tag=good_fixture
            ----
                Given a step passes ... passed
                When another step passes ... passed
            """
        But the command output should not contain "HOOK: after_scenario"
        And note that "show_capture_on_success is not enabled on OTHER_HOOK"


      Scenario: Use show_on_success on ANY_HOOK without error
        Given a file named "features/environment.py" with:
            """
            from behave.capture import any_hook
            from example4me.fixture import use_special_fixture_by_tag

            any_hook.show_capture_on_success = True

            # -- HOOKS:
            def before_all(ctx):
                ctx.config.setup_logging(filename="behave.log")

            def before_tag(ctx, tag):
                use_special_fixture_by_tag(tag)

            def after_scenario(ctx, scenario):
                print("HOOK: after_scenario -- {}".format(scenario.name))
            """
        And a file named "features/capture_hook.good.feature" with:
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
          CAPTURED LOG: before_tag
          LOG_INFO:example4me: GOOD_FIXTURE: tag=good_fixture
          """
        And the file "behave.log" should contain:
            """
            LOG_INFO:example4me: GOOD_FIXTURE: tag=good_fixture
            """
        But note that "captured output on hooks are shown on HOOK-SUCCESS"
        And note that "ANY_HOOK captured output is shown (see below)"
        And the command output should contain:
            """
              Scenario: Passing -- GOOD
            ----
            CAPTURED LOG: before_tag
            LOG_INFO:example4me: GOOD_FIXTURE: tag=good_fixture
            ----
                Given a step passes ... passed
                When another step passes ... passed
            ----
            CAPTURED STDOUT: after_scenario
            HOOK: after_scenario -- Passing -- GOOD
            ----
            """

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
            from example4me.fixture import use_special_fixture_by_tag
            import os

            BEFORE_ALL_TAG = os.environ.get("BEFORE_ALL_TAG", "good_before_all")

            # -- HOOKS:
            @capture_output
            def before_all(ctx):
                ctx.config.setup_logging(filename="behave.log")
                use_special_fixture_by_tag(BEFORE_ALL_TAG)
            """

      Scenario: Use @capture_output on "before_all" hook without error
        Given I set the environment variable "BEFORE_ALL_TAG" to "good_before_all"
        When I run "behave -f plain --capture features/passing.feature"
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
        When I run "behave -f plain --capture features/passing.feature"
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
        Then it should fail with:
            """
            HOOK-ERROR in before_all: RuntimeError: OOPS, BAD_FIXTURE: tag=bad_before_all
            """
        And the command output should contain:
            """
            CAPTURED LOG:
            LOG_WARNING:example4me: BAD_FIXTURE: tag=bad_before_all
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
