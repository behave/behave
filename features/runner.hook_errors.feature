Feature: Hooks processing in case of errors (exceptions)

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

  @setup
  Scenario: Feature Setup
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
          @soo
          Scenario: A1
            Given a step passes
        """
    And a file named "features/environment.py" with:
        """
        from __future__ import print_function

        def cause_hook_to_fail():
            raise RuntimeError("FAIL")

        def before_all(context):
            userdata = context.config.userdata
            if userdata.get("HOOK_ERROR_LOC") == "before_all":
                cause_hook_to_fail()

        def after_all(context):
            userdata = context.config.userdata
            if userdata.get("HOOK_ERROR_LOC") == "before_all":
                print("called_hook:after_all")
            if userdata.get("HOOK_ERROR_LOC") == "after_all":
                cause_hook_to_fail()

        def before_feature(context, feature):
            userdata = context.config.userdata
            if userdata.get("HOOK_ERROR_LOC") == "before_feature":
                cause_hook_to_fail()

        def after_feature(context, feature):
            userdata = context.config.userdata
            if userdata.get("HOOK_ERROR_LOC") == "before_feature":
                print("called_hook:after_feature")
            if userdata.get("HOOK_ERROR_LOC") == "after_feature":
                cause_hook_to_fail()

        def before_scenario(context, scenario):
            userdata = context.config.userdata
            if userdata.get("HOOK_ERROR_LOC") == "before_scenario":
                cause_hook_to_fail()

        def after_scenario(context, scenario):
            userdata = context.config.userdata
            if userdata.get("HOOK_ERROR_LOC") == "before_scenario":
                print("called_hook:after_scenario")
            if userdata.get("HOOK_ERROR_LOC") == "after_scenario":
                cause_hook_to_fail()

        def before_step(context, step):
            userdata = context.config.userdata
            if userdata.get("HOOK_ERROR_LOC") == "before_step":
                cause_hook_to_fail()

        def after_step(context, step):
            userdata = context.config.userdata
            if userdata.get("HOOK_ERROR_LOC") == "before_step":
                print("called_hook:after_step")
            if userdata.get("HOOK_ERROR_LOC") == "after_step":
                cause_hook_to_fail()

        def before_tag(context, tag):
            userdata = context.config.userdata
            if userdata.get("HOOK_ERROR_LOC") == "before_tag":
                error_tag = userdata.get("HOOK_ERROR_TAG")
                if not error_tag or tag == error_tag:
                    cause_hook_to_fail()

        def after_tag(context, tag):
            userdata = context.config.userdata
            if userdata.get("HOOK_ERROR_LOC") == "before_tag":
                error_tag = userdata.get("HOOK_ERROR_TAG")
                if tag == error_tag:
                    print("called_hook:after_tag: tag=%s" % tag)
            if userdata.get("HOOK_ERROR_LOC") == "after_tag":
                error_tag = userdata.get("HOOK_ERROR_TAG")
                if not error_tag or tag == error_tag:
                    cause_hook_to_fail()
        """
    And a file named "behave.ini" with:
        """
        [behave]
        show_skipped = false
        show_timings = false
        """


    @hook.before_all
    Scenario: Hook error in before_all
      When I run "behave -f plain -D HOOK_ERROR_LOC=before_all features/passing.feature"
      Then it should fail with
          """
          HOOK-ERROR in before_all: RuntimeError: FAIL
          called_hook:after_all

          ABORTED: By user.
          0 features passed, 0 failed, 0 skipped, 1 untested
          0 scenarios passed, 0 failed, 0 skipped, 1 untested
          0 steps passed, 0 failed, 0 skipped, 0 undefined, 1 untested
          """
      But note that "the after_all hook is called, too"


    @hook.after_all
    Scenario: Hook error in after_all
      When I run "behave -f plain -D HOOK_ERROR_LOC=after_all features/passing.feature"
      Then it should fail with:
          """
          Feature: Alice

            Scenario: A1
              Given a step passes ... passed

          HOOK-ERROR in after_all: RuntimeError: FAIL
          ABORTED: By user.
          1 feature passed, 0 failed, 0 skipped
          1 scenario passed, 0 failed, 0 skipped
          1 step passed, 0 failed, 0 skipped, 0 undefined
          """


    @hook.before_feature
    Scenario: Hook error in before_feature
      When I run "behave -f plain -D HOOK_ERROR_LOC=before_feature features/passing.feature"
      Then it should fail with:
          """
          HOOK-ERROR in before_feature: RuntimeError: FAIL
          Feature: Alice
          called_hook:after_feature

          0 features passed, 1 failed, 0 skipped
          0 scenarios passed, 0 failed, 0 skipped, 1 untested
          0 steps passed, 0 failed, 0 skipped, 0 undefined, 1 untested
          """
      But note that "the after_feature hook is called, too."


    @hook.after_feature
    Scenario: Hook error in after_feature
      When I run "behave -f plain -D HOOK_ERROR_LOC=after_feature features/passing.feature"
      Then it should fail with:
          """
          Feature: Alice
            Scenario: A1
              Given a step passes ... passed
          HOOK-ERROR in after_feature: RuntimeError: FAIL

          0 features passed, 1 failed, 0 skipped
          1 scenario passed, 0 failed, 0 skipped
          1 step passed, 0 failed, 0 skipped, 0 undefined
          """


    @hook.before_scenario
    Scenario: Hook error in before_scenario
      When I run "behave -f plain -D HOOK_ERROR_LOC=before_scenario features/passing.feature"
      Then it should fail with:
          """
          Feature: Alice

          HOOK-ERROR in before_scenario: RuntimeError: FAIL
            Scenario: A1
          called_hook:after_scenario

          Failing scenarios:
            features/passing.feature:4  A1

          0 features passed, 1 failed, 0 skipped
          0 scenarios passed, 1 failed, 0 skipped
          0 steps passed, 0 failed, 0 skipped, 0 undefined, 1 untested
          """
      But note that "the after_scenario hook is called, too."


    @hook.after_scenario
    Scenario: Hook error in after_scenario
      When I run "behave -f plain -D HOOK_ERROR_LOC=after_scenario features/passing.feature"
      Then it should fail with:
          """
          Feature: Alice

            Scenario: A1
              Given a step passes ... passed
          HOOK-ERROR in after_scenario: RuntimeError: FAIL


          Failing scenarios:
            features/passing.feature:4  A1

          0 features passed, 1 failed, 0 skipped
          0 scenarios passed, 1 failed, 0 skipped
          1 step passed, 0 failed, 0 skipped, 0 undefined
          """

    @hook.before_step
    Scenario: Hook error in before_step
      When I run "behave -f plain -D HOOK_ERROR_LOC=before_step features/passing.feature"
      Then it should fail with:
          """
          Feature: Alice

            Scenario: A1
              Given a step passes ... failed

          Captured stdout:
            HOOK-ERROR in before_step: RuntimeError: FAIL
            called_hook:after_step

          Failing scenarios:
            features/passing.feature:4  A1

          0 features passed, 1 failed, 0 skipped
          0 scenarios passed, 1 failed, 0 skipped
          0 steps passed, 1 failed, 0 skipped, 0 undefined
          """
      But note that "the after_step hook is called, too."


    @hook.after_step
    Scenario: Hook error in after_step
      When I run "behave -f plain -D HOOK_ERROR_LOC=after_step features/passing.feature"
      Then it should fail with:
          """
          Feature: Alice

            Scenario: A1
              Given a step passes ... failed

          Captured stdout:
            HOOK-ERROR in after_step: RuntimeError: FAIL

          Failing scenarios:
            features/passing.feature:4  A1

          0 features passed, 1 failed, 0 skipped
          0 scenarios passed, 1 failed, 0 skipped
          0 steps passed, 1 failed, 0 skipped, 0 undefined
          """


    @hook.before_tag
    Scenario: Hook error in before_tag for feature
      When I run "behave -f plain -D HOOK_ERROR_LOC=before_tag -D HOOK_ERROR_TAG=foo features/passing.feature"
      Then it should fail with:
          """
          HOOK-ERROR in before_tag(tag=foo): RuntimeError: FAIL
          Feature: Alice
          called_hook:after_tag: tag=foo

          0 features passed, 1 failed, 0 skipped
          0 scenarios passed, 0 failed, 0 skipped, 1 untested
          0 steps passed, 0 failed, 0 skipped, 0 undefined, 1 untested
          """
      And the command output should contain:
          """
          HOOK-ERROR in before_tag(tag=foo): RuntimeError: FAIL
          Feature: Alice
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
          HOOK-ERROR in after_tag(tag=foo): RuntimeError: FAIL

          0 features passed, 1 failed, 0 skipped
          1 scenario passed, 0 failed, 0 skipped
          1 step passed, 0 failed, 0 skipped, 0 undefined
          """
      But note that "the hook-error in after_tag of the scenario causes it to fail"


    @hook.before_tag
    Scenario: Hook error in before_tag for scenario
      When I run "behave -f plain -D HOOK_ERROR_LOC=before_tag -D HOOK_ERROR_TAG=soo features/passing.feature"
      Then it should fail with:
          """
          Feature: Alice
          HOOK-ERROR in before_tag(tag=soo): RuntimeError: FAIL
            Scenario: A1
          called_hook:after_tag: tag=soo

          Failing scenarios:
            features/passing.feature:4  A1

          0 features passed, 1 failed, 0 skipped
          0 scenarios passed, 1 failed, 0 skipped
          0 steps passed, 0 failed, 0 skipped, 0 undefined, 1 untested
          """
      But note that "the hook-error in before_tag of the scenario causes it to fail and be skipped (untested)"
      And note that "the after_tag hook is still called"


    @hook.after_tag
    Scenario: Hook error in after_tag for scenario
      When I run "behave -f plain -D HOOK_ERROR_LOC=after_tag -D HOOK_ERROR_TAG=soo features/passing.feature"
      Then it should fail with:
          """
          Feature: Alice

            Scenario: A1
              Given a step passes ... passed
          HOOK-ERROR in after_tag(tag=soo): RuntimeError: FAIL

          Failing scenarios:
            features/passing.feature:4  A1

          0 features passed, 1 failed, 0 skipped
          0 scenarios passed, 1 failed, 0 skipped
          1 step passed, 0 failed, 0 skipped, 0 undefined
          """
      But note that "the hook-error in after_tag of the scenario causes it to fail"


    @skipped.hook.after_feature
    Scenario: Skipped feature with potential hook error (hooks are not run)

      This goes unnoticed because hooks are not run for a skipped feature/scenario.
      NOTE: Except if before_feature(), before_scenario() hook skips the feature/scenario.

      When I run "behave -f plain -D HOOK_ERROR_LOC=after_feature -t ~@foo features/passing.feature"
      Then it should pass with:
          """
          0 features passed, 0 failed, 1 skipped
          0 scenarios passed, 0 failed, 1 skipped
          0 steps passed, 0 failed, 1 skipped, 0 undefined
          """
      But note that "hooks are not executed for skipped features/scenarios"


    Scenario: Show hook error details (traceback)
      When I run "behave -f plain -D HOOK_ERROR_LOC=before_feature --verbose features/passing.feature"
      Then it should fail with:
          """
          HOOK-ERROR in before_feature: RuntimeError: FAIL
          """
      And the command output should contain:
          """
            self.hooks[name](context, *args)
          File "features/environment.py", line 21, in before_feature
            cause_hook_to_fail()
          File "features/environment.py", line 4, in cause_hook_to_fail
            raise RuntimeError("FAIL")
          """
      But note that "the traceback caused by the hook-error is shown"
