Feature: Hooks processing in case of errors (exceptions)

  . SPECIFICATION:
  .   * Hook errors in before_all/after_all hook abort the test run.
  .   * Hook errors in before_feature/after_feature mark feature as failed.
  .   * Hook errors in before_scenario/after_scenario mark scenario as failed.
  .   * Hook errors in before_step/after_step mark step as failed.
  .   * Hook errors in before_tag/after_tag mark current feature as failed.
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
        Feature:
          Scenario:
            Given a step passes
        """
    And a file named "features/environment.py" with:
        """
        def before_all(context):
            if context.config.userdata.get("HOOK_ERROR_LOC") == "before_all":
                raise RuntimeError("FAIL")

        def after_all(context):
            if context.config.userdata.get("HOOK_ERROR_LOC") == "after_all":
                raise RuntimeError("FAIL")

        def before_feature(context, feature):
            if context.config.userdata.get("HOOK_ERROR_LOC") == "before_feature":
                raise RuntimeError("FAIL")

        def after_feature(context, feature):
            if context.config.userdata.get("HOOK_ERROR_LOC") == "after_feature":
                raise RuntimeError("FAIL")

        def before_scenario(context, scenario):
            if context.config.userdata.get("HOOK_ERROR_LOC") == "before_scenario":
                raise RuntimeError("FAIL")

        def after_scenario(context, scenario):
            if context.config.userdata.get("HOOK_ERROR_LOC") == "after_scenario":
                raise RuntimeError("FAIL")

        def before_step(context, step):
            if context.config.userdata.get("HOOK_ERROR_LOC") == "before_step":
                raise RuntimeError("FAIL")

        def after_step(context, step):
            if context.config.userdata.get("HOOK_ERROR_LOC") == "after_step":
                raise RuntimeError("FAIL")

        def before_tag(context, tag):
            if context.config.userdata.get("HOOK_ERROR_LOC") == "before_tag":
                raise RuntimeError("FAIL")

        def after_tag(context, tag):
            if context.config.userdata.get("HOOK_ERROR_LOC") == "after_tag":
                raise RuntimeError("FAIL")
        """

    @hook.before_all
    Scenario: Hook error in before_all
      When I run "behave -f plain -D HOOK_ERROR_LOC=before_all features/passing.feature"
      Then it should fail with
          """
          HOOK-ERROR in before_all: RuntimeError: FAIL

          ABORTED: By user.
          0 features passed, 0 failed, 0 skipped, 1 untested
          0 scenarios passed, 0 failed, 0 skipped, 1 untested
          0 steps passed, 0 failed, 0 skipped, 0 undefined, 1 untested
          """

    @hook.after_all
    Scenario: Hook error in after_all
      When I run "behave -f plain -D HOOK_ERROR_LOC=after_all features/passing.feature"
      Then it should fail with:
          """
          Feature:

            Scenario:
              Given a step passes ... passed

          HOOK-ERROR in after_all: RuntimeError: FAIL
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

            Scenario:
              Given a step passes ... passed

          0 features passed, 1 failed, 0 skipped
          1 scenario passed, 0 failed, 0 skipped
          1 step passed, 0 failed, 0 skipped, 0 undefined
          """

    @hook.after_feature
    Scenario: Hook error in after_feature
      When I run "behave -f plain -D HOOK_ERROR_LOC=after_feature features/passing.feature"
      Then it should fail with:
          """
          Feature:
            Scenario:
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
          Feature:

            Scenario:
          HOOK-ERROR in before_scenario: RuntimeError: FAIL
              Given a step passes ... passed


          Failing scenarios:
            features/passing.feature:3

          0 features passed, 1 failed, 0 skipped
          0 scenarios passed, 1 failed, 0 skipped
          1 step passed, 0 failed, 0 skipped, 0 undefined
          """

    @hook.after_scenario
    Scenario: Hook error in after_scenario
      When I run "behave -f plain -D HOOK_ERROR_LOC=after_scenario features/passing.feature"
      Then it should fail with:
          """
          Feature:

            Scenario:
              Given a step passes ... passed
          HOOK-ERROR in after_scenario: RuntimeError: FAIL


          Failing scenarios:
            features/passing.feature:3

          0 features passed, 1 failed, 0 skipped
          0 scenarios passed, 1 failed, 0 skipped
          1 step passed, 0 failed, 0 skipped, 0 undefined
          """

    @hook.before_step
    Scenario: Hook error in before_step
      When I run "behave -f plain -D HOOK_ERROR_LOC=before_step features/passing.feature"
      Then it should fail with:
          """
          Feature:

            Scenario:
          HOOK-ERROR in before_step: RuntimeError: FAIL
              Given a step passes ... failed


          Failing scenarios:
            features/passing.feature:3

          0 features passed, 1 failed, 0 skipped
          0 scenarios passed, 1 failed, 0 skipped
          0 steps passed, 1 failed, 0 skipped, 0 undefined
          """

    @hook.after_step
    Scenario: Hook error in after_step
      When I run "behave -f plain -D HOOK_ERROR_LOC=after_step features/passing.feature"
      Then it should fail with:
          """
          Feature:

            Scenario:
          HOOK-ERROR in after_step: RuntimeError: FAIL
              Given a step passes ... failed


          Failing scenarios:
            features/passing.feature:3

          0 features passed, 1 failed, 0 skipped
          0 scenarios passed, 1 failed, 0 skipped
          0 steps passed, 1 failed, 0 skipped, 0 undefined
          """


    @hook.before_tag
    Scenario: Hook error in before_tag
      When I run "behave -f plain -D HOOK_ERROR_LOC=before_tag features/passing.feature"
      Then it should fail with:
          """
          Feature:
          HOOK-ERROR in before_tag(tag=foo): RuntimeError: FAIL

            Scenario:
              Given a step passes ... passed

          0 features passed, 1 failed, 0 skipped
          1 scenario passed, 0 failed, 0 skipped
          1 step passed, 0 failed, 0 skipped, 0 undefined
          """

    @hook.after_tag
    Scenario: Hook error in after_tag
      When I run "behave -f plain -D HOOK_ERROR_LOC=after_tag features/passing.feature"
      Then it should fail with:
          """
          Feature:

            Scenario:
              Given a step passes ... passed
          HOOK-ERROR in after_tag(tag=foo): RuntimeError: FAIL

          0 features passed, 1 failed, 0 skipped
          1 scenario passed, 0 failed, 0 skipped
          1 step passed, 0 failed, 0 skipped, 0 undefined
          """

    @skipped.hook.after_feature
    Scenario: Skipped feature with hook error
      When I run "behave -f plain -D HOOK_ERROR_LOC=after_feature -t ~@foo features/passing.feature"
      Then it should pass with:
          """
          Feature:
            Scenario:

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
          File "features/environment.py", line 11, in before_feature
            raise RuntimeError("FAIL")
          """
