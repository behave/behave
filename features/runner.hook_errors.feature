Feature: Hooks Processing in case of Errors

  . SPECIFICATION:
  .   * Hook errors in before_all/after_all hook aborts the test run (and fail).
  .   * Hook errors in before_feature/after_feature causes the feature to fail.
  .   * Hook errors in before_feature causes feature scenarios to be skipped (untested).
  .   * Hook errors in before_scenario/after_scenario causes the scenario to fail.
  .   * Hook errors in before_scenario causes scenario steps to be skipped (untested).
  .   * Hook errors in before_step/after_step causes step to fail.
  .   * Hook errors in before_tag/after_tag of a feature  causes feature  to fail.
  .   * Hook errors in before_tag/after_tag of a scenario causes scenario to fail.
  .   * If a hook error occurs in a "before_xxx" hook,
  .     then the "after_xxx" hook will also be called (to cleanup some stuff).
  .
  . NOTE:
  . The --verbose flag can be used to show the exception traceback.

  Background:
    Given a new working directory
    And a file named "features/steps/steps.py" with:
      """
      from behave import step

      @step(u'{word:w} step passes')
      def step(context, word):
          pass
      """
    And   a file named "features/passing.feature" with:
        """
        @foo
        Feature: Alice
          @bar
          Scenario: A1
            Given a step passes
        """
    And an empty file named "example4me/__init__.py"
    And a file named "example4me/hooks.py" with:
        """
        class SomeError(RuntimeError): pass

        def cause_hook_to_fail():
            raise SomeError("FAIL")

        def process_hook_error_location(ctx, hook_name):
            userdata = ctx.config.userdata
            if userdata.get("HOOK_ERROR_LOC") == hook_name:
                cause_hook_to_fail()

        def process_hook_error_location_with_tag(ctx, hook_name, tag):
            userdata = ctx.config.userdata
            if userdata.get("HOOK_ERROR_LOC") == hook_name:
                error_tag = userdata.get("HOOK_ERROR_TAG")
                if not error_tag or tag == error_tag:
                    cause_hook_to_fail()

        def print_after_hook_location(ctx, hook_name):
            before_hook_name = hook_name.replace("after_", "before_")
            userdata = ctx.config.userdata
            if userdata.get("HOOK_ERROR_LOC") == before_hook_name:
                print("called_hook:{hook}".format(hook=hook_name))
        """
    And a file named "features/environment.py" with:
        """
        from __future__ import absolute_import, print_function
        from behave.capture import any_hook
        from example4me.hooks import (
            print_after_hook_location,
            process_hook_error_location,
            process_hook_error_location_with_tag,
        )

        any_hook.show_capture_on_success = True

        # -- HOOKS:
        def before_all(ctx):
            process_hook_error_location(ctx, "before_all")

        def after_all(ctx):
            print_after_hook_location(ctx, "after_all")
            process_hook_error_location(ctx, "after_all")

        def before_feature(ctx, feature):
            process_hook_error_location(ctx, "before_feature")

        def after_feature(ctx, feature):
            print_after_hook_location(ctx, "after_feature")
            process_hook_error_location(ctx, "after_feature")

        def before_scenario(ctx, scenario):
            process_hook_error_location(ctx, "before_scenario")

        def after_scenario(ctx, scenario):
            print_after_hook_location(ctx, "after_scenario")
            process_hook_error_location(ctx, "after_scenario")

        def before_step(ctx, step):
            process_hook_error_location(ctx, "before_step")

        def after_step(ctx, step):
            print_after_hook_location(ctx, "after_step")
            process_hook_error_location(ctx, "after_step")

        def before_tag(ctx, tag):
            process_hook_error_location_with_tag(ctx, "before_tag", tag)

        def after_tag(ctx, tag):
            userdata = ctx.config.userdata
            if userdata.get("HOOK_ERROR_LOC") == "before_tag":
                error_tag = userdata.get("HOOK_ERROR_TAG")
                if tag == error_tag:
                    print("called_hook:after_tag: tag=%s" % tag)
            process_hook_error_location_with_tag(ctx, "after_tag", tag)

        # DISABLED: after_tag.show_capture_on_success = True
        """
    And a file named "behave.ini" with:
        """
        [behave]
        show_skipped = false
        show_timings = false
        """

  Rule: Hook-Error Basics
    @hook.before_all
    Scenario: Hook error in before_all
      When I run "behave -f plain -D HOOK_ERROR_LOC=before_all features/passing.feature"
      Then it should fail with
          """
          HOOK-ERROR in before_all: SomeError: FAIL
          ----
          CAPTURED STDOUT: after_all
          called_hook:after_all
          ----
          """
      And the command output should contain:
          """
          ABORTED: By user.
          0 features passed, 0 failed, 0 skipped, 1 untested
          0 scenarios passed, 0 failed, 0 skipped, 1 untested
          0 steps passed, 0 failed, 0 skipped, 1 untested
          """
      And the command output should contain:
          """
          ABORTED: HOOK-ERROR in hook=before_all
          """
      But note that "the after_all hook is called even if a HOOK-ERROR occurs"

    @hook.after_all
    Scenario: Hook error in after_all
      When I run "behave -f plain -D HOOK_ERROR_LOC=after_all features/passing.feature"
      Then it should fail with:
          """
          Feature: Alice

            Scenario: A1
              Given a step passes ... passed
          ----
          CAPTURED STDOUT: after_all
          HOOK-ERROR in after_all: SomeError: FAIL
          ----

          1 feature passed, 0 failed, 0 skipped
          1 scenario passed, 0 failed, 0 skipped
          1 step passed, 0 failed, 0 skipped
          """


    @hook.before_feature
    Scenario: Hook error in before_feature
      When I run "behave -f plain -D HOOK_ERROR_LOC=before_feature features/passing.feature"
      Then it should fail with:
          """
          0 features passed, 0 failed, 1 hook_error, 0 skipped
          0 scenarios passed, 0 failed, 0 skipped, 1 untested
          0 steps passed, 0 failed, 0 skipped, 1 untested
          """
      And the command output should contain:
          """
          Feature: Alice
          ----
          CAPTURED STDOUT: before_feature
          HOOK-ERROR in before_feature: SomeError: FAIL
          ----
          ----
          CAPTURED STDOUT: after_feature
          called_hook:after_feature
          ----
          """
      But note that "the after_feature hook is called, too."


    @hook.after_feature
    Scenario: Hook error in after_feature
      When I run "behave -f plain -D HOOK_ERROR_LOC=after_feature features/passing.feature"
      Then it should fail with:
          """
          0 features passed, 0 failed, 1 hook_error, 0 skipped
          1 scenario passed, 0 failed, 0 skipped
          1 step passed, 0 failed, 0 skipped
          """
      And the command output should contain:
          """
          Feature: Alice
            Scenario: A1
              Given a step passes ... passed
          ----
          CAPTURED STDOUT: after_feature
          HOOK-ERROR in after_feature: SomeError: FAIL
          ----
          """


    @hook.before_scenario
    Scenario: Hook error in before_scenario
      When I run "behave -f plain -D HOOK_ERROR_LOC=before_scenario features/passing.feature"
      Then it should fail with:
          """
          HOOK-ERROR in before_scenario: SomeError: FAIL
          """
      And the command output should contain:
          """
          Errored scenarios:
            features/passing.feature:4  A1

          0 features passed, 0 failed, 1 error, 0 skipped
          0 scenarios passed, 0 failed, 1 hook_error, 0 skipped
          0 steps passed, 0 failed, 0 skipped, 1 untested
          """
      And the command output should contain:
          """
            Scenario: A1
          ----
          CAPTURED STDOUT: before_scenario
          HOOK-ERROR in before_scenario: SomeError: FAIL
          ----
          ----
          CAPTURED STDOUT: after_scenario
          called_hook:after_scenario
          ----
          """
      But note that "the after_scenario hook is called, too."


    @hook.after_scenario
    Scenario: Hook error in after_scenario
      When I run "behave -f plain -D HOOK_ERROR_LOC=after_scenario features/passing.feature"
      Then it should fail with:
          """
          HOOK-ERROR in after_scenario: SomeError: FAIL
          """
      And the command output should contain:
          """
          Feature: Alice

            Scenario: A1
              Given a step passes ... passed
          ----
          CAPTURED STDOUT: after_scenario
          HOOK-ERROR in after_scenario: SomeError: FAIL
          ----
          """
      And the command output should contain:
          """
          Errored scenarios:
            features/passing.feature:4  A1

          0 features passed, 0 failed, 1 error, 0 skipped
          0 scenarios passed, 0 failed, 1 hook_error, 0 skipped
          1 step passed, 0 failed, 0 skipped
          """

    @hook.before_step
    Scenario: Hook error in before_step
      When I run "behave -f plain -D HOOK_ERROR_LOC=before_step features/passing.feature"
      Then it should fail with:
          """
          HOOK-ERROR in before_step: SomeError: FAIL
          """
      And the command output should contain:
          """
          Feature: Alice

            Scenario: A1
              Given a step passes ... hook_error
          ----
          CAPTURED STDOUT: scenario
          HOOK-ERROR in before_step: SomeError: FAIL
          called_hook:after_step
          ----
          """
      And the command output should contain:
          """
          Errored scenarios:
            features/passing.feature:4  A1

          0 features passed, 0 failed, 1 error, 0 skipped
          0 scenarios passed, 0 failed, 1 error, 0 skipped
          0 steps passed, 0 failed, 1 hook_error, 0 skipped
          """
      But note that "the after_step hook is called, too."


    @hook.after_step
    Scenario: Hook error in after_step
      When I run "behave -f plain -D HOOK_ERROR_LOC=after_step features/passing.feature"
      Then it should fail with:
          """
          HOOK-ERROR in after_step: SomeError: FAIL
          """
      And the command output should contain:
          """
          Feature: Alice

            Scenario: A1
              Given a step passes ... hook_error
          ----
          CAPTURED STDOUT: scenario
          HOOK-ERROR in after_step: SomeError: FAIL
          ----
          """
      And the command output should contain:
          """
          Errored scenarios:
            features/passing.feature:4  A1

          0 features passed, 0 failed, 1 error, 0 skipped
          0 scenarios passed, 0 failed, 1 error, 0 skipped
          0 steps passed, 0 failed, 1 hook_error, 0 skipped
          """


    @hook.before_tag
    Scenario: Hook error in before_tag for feature
      When I run "behave -f plain -D HOOK_ERROR_LOC=before_tag -D HOOK_ERROR_TAG=foo features/passing.feature"
      Then it should fail with:
          """
          HOOK-ERROR in before_tag(tag=foo): SomeError: FAIL
          """
      And the command output should contain:
          """
          Feature: Alice
          ----
          CAPTURED STDOUT: before_tag
          HOOK-ERROR in before_tag(tag=foo): SomeError: FAIL
          ----
          ----
          CAPTURED STDOUT: after_tag
          called_hook:after_tag: tag=foo
          ----

          0 features passed, 0 failed, 1 hook_error, 0 skipped
          0 scenarios passed, 0 failed, 0 skipped, 1 untested
          0 steps passed, 0 failed, 0 skipped, 1 untested
          """
      But note that "the hook-error in before_tag of the feature causes it to fail and be skipped (untested)"
      And note that "the after_tag hook is still called"


    @hook.after_tag
    Scenario: Hook error in after_tag for feature
      When I run "behave -f plain -D HOOK_ERROR_LOC=after_tag -D HOOK_ERROR_TAG=foo features/passing.feature"
      Then it should fail with:
          """
          Feature: Alice

            Scenario: A1
              Given a step passes ... passed
          ----
          CAPTURED STDOUT: after_tag
          HOOK-ERROR in after_tag(tag=foo): SomeError: FAIL
          ----

          0 features passed, 0 failed, 1 hook_error, 0 skipped
          1 scenario passed, 0 failed, 0 skipped
          1 step passed, 0 failed, 0 skipped
          """
      But note that "the hook-error in after_tag of the scenario causes it to fail"


    @hook.before_tag
    Scenario: Hook error in before_tag for scenario
      When I run "behave -f plain -D HOOK_ERROR_LOC=before_tag -D HOOK_ERROR_TAG=bar features/passing.feature"
      Then it should fail with:
          """
          Errored scenarios:
            features/passing.feature:4  A1

          0 features passed, 0 failed, 1 error, 0 skipped
          0 scenarios passed, 0 failed, 1 hook_error, 0 skipped
          0 steps passed, 0 failed, 0 skipped, 1 untested
          """
      And the command output should contain:
          """
          Feature: Alice
            Scenario: A1
          ----
          CAPTURED STDOUT: before_tag
          HOOK-ERROR in before_tag(tag=bar): SomeError: FAIL
          ----
          ----
          CAPTURED STDOUT: after_tag
          called_hook:after_tag: tag=bar
          ----

          """
      But note that "the hook-error in before_tag of the scenario causes it to fail and be skipped (untested)"
      And note that "the after_tag hook is still called"


    @hook.after_tag
    Scenario: Hook error in after_tag for scenario
      When I run "behave -f plain -D HOOK_ERROR_LOC=after_tag -D HOOK_ERROR_TAG=bar features/passing.feature"
      Then it should fail with:
          """
          HOOK-ERROR in after_tag(tag=bar): SomeError: FAIL
          """
      And the command output should contain:
          """
          Feature: Alice

            Scenario: A1
              Given a step passes ... passed
          ----
          CAPTURED STDOUT: after_tag
          HOOK-ERROR in after_tag(tag=bar): SomeError: FAIL
          ----
          """
      And the command output should contain:
          """
          Errored scenarios:
            features/passing.feature:4  A1

          0 features passed, 0 failed, 1 error, 0 skipped
          0 scenarios passed, 0 failed, 1 hook_error, 0 skipped
          1 step passed, 0 failed, 0 skipped
          """
      But note that "the hook-error in after_tag of the scenario causes it to fail"


  Rule: Hook-Error Details

    HINT: Verbose mode enables that stacktrace/traceback is shown.

    Scenario: Hook-Error with Stacktrace (in: before_all)
      When I run "behave --verbose -f plain -D HOOK_ERROR_LOC=before_all features/passing.feature"
      Then it should fail with
          """
          HOOK-ERROR in before_all: SomeError: FAIL
          """
      And the command output should contain:
          """
          File "{__WORKDIR__}/example4me/hooks.py", line 4, in cause_hook_to_fail
            raise SomeError("FAIL")
          """
      And the command output should contain:
          """
          ----
          CAPTURED STDOUT: after_all
          called_hook:after_all
          ----

          ABORTED: By user.
          0 features passed, 0 failed, 0 skipped, 1 untested
          0 scenarios passed, 0 failed, 0 skipped, 1 untested
          0 steps passed, 0 failed, 0 skipped, 1 untested
          """
      But note that "the after_all hook is called even if a HOOK-ERROR occurs"
      # -- HINT: NOT_SHOWN: ABORTED: HOOK-ERROR in hook=before_all

    Scenario: Hook-Error with Stacktrace (in: before_feature)
      When I run "behave --verbose -f plain -D HOOK_ERROR_LOC=before_feature features/passing.feature"
      Then it should fail with:
          """
          CAPTURED STDOUT: before_feature
          HOOK-ERROR in before_feature: SomeError: FAIL
          """
      And the command output should contain:
          """
          File "features/environment.py", line 20, in before_feature
            process_hook_error_location(ctx, "before_feature")
          """
      And the command output should contain:
          """
          File "{__WORKDIR__}/example4me/hooks.py", line 9, in process_hook_error_location
            cause_hook_to_fail()
          """
      And the command output should contain:
          """
            File "{__WORKDIR__}/example4me/hooks.py", line 4, in cause_hook_to_fail
              raise SomeError("FAIL")
          """
      But note that "the traceback caused by the hook-error is shown"


  Rule: Skipped with Hook-Error

    This goes unnoticed because hooks are not run for a skipped feature/scenario.
    NOTE: Except if before_feature(), before_scenario() hook skips the feature/scenario.

    Scenario: Skipped Feature with Hook-Error (IGNORED)
      When I run `behave -f plain -D HOOK_ERROR_LOC=after_feature -tags="not @foo" features/passing.feature`
      Then it should pass with:
          """
          0 features passed, 0 failed, 1 skipped
          0 scenarios passed, 0 failed, 1 skipped
          0 steps passed, 0 failed, 1 skipped
          """
      But note that "hooks are not executed for skipped features/scenarios"
