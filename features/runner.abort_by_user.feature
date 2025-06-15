Feature: Test run can be aborted by the user

  As a tester
  I want sometimes to abort a test run (because it is anyway failing, etc.)
  So that I am more productive.

  . NOTES:
  .  * The test runner should fail gracefully (most of the times)
  .  * At least some cleanup hooks should be called (in general)


  Background:
    Given a new working directory
    And a file named "features/steps/aborting_steps.py" with:
        """
        from behave import step

        @step('{word:w} step passes')
        def step_passes(context, word):
            pass

        @step('the user aborts the test run')
        def step_user_aborts_testrun(context):
            raise KeyboardInterrupt()
        """
    And a file named "features/scenarios_pass3.feature" with:
        """
        Feature:
          Scenario:
            Given a step passes
            When another step passes

          Scenario:
            Given first step passes
            When second step passes
            Then third step passes

          Scenario:
            Then last step passes
        """


  Scenario: Abort test run in step definition
    Given a file named "features/aborting_in_step.feature" with:
        """
        Feature: User aborts test run in a step definition
          Scenario: One
            Given a step passes
            When another step passes

          Scenario: User aborts here
            Given first step passes
            When the user aborts the test run
            Then third step passes

          Scenario: Third
            Then last step passes
        """
    And an empty file named "features/environment.py"
    When I run "behave -f plain -T features/aborting_in_step.feature"
    Then it should fail with:
        """
        ABORTED: KeyboardInterrupt
        """
    And the command output should contain:
        """
        ABORTED: By user.

        Errored scenarios:
          features/aborting_in_step.feature:6  User aborts here

        0 features passed, 0 failed, 1 error, 0 skipped
        1 scenario passed, 0 failed, 1 error, 0 skipped, 1 untested
        3 steps passed, 0 failed, 1 error, 1 skipped, 1 untested
        """
    And the command output should contain:
        """
        Feature: User aborts test run in a step definition

          Scenario: One
            Given a step passes ... passed
            When another step passes ... passed

          Scenario: User aborts here
            Given first step passes ... passed
            When the user aborts the test run ... error
        ABORTED: By user (KeyboardInterrupt).
        """
    But note that "the last scenario is untested (not-run) due to the user abort"


  Scenario: Abort test run in before_scenario hook
    Given a file named "features/aborting_in_before_scenario_hook.feature" with:
        """
        Feature: User aborts test run in before_scenario hook of S2
          Scenario: S1
            Given a step passes
            When another step passes

          @user.aborts.before_scenario
          Scenario: S2 -- User aborts here
            Given first step passes
            When second step passes
            Then third step passes

          Scenario: S3
            Then last step passes
        """
    And a file named "features/environment.py" with:
        """
        def before_scenario(context, scenario):
            if "user.aborts.before_scenario" in scenario.tags:
                user_aborts_testrun_here()

        def user_aborts_testrun_here():
            raise KeyboardInterrupt()
        """
    When I run "behave -f plain -T features/aborting_in_before_scenario_hook.feature"
    Then it should fail with:
        """
        ABORTED: HOOK-ERROR in before_scenario: KeyboardInterrupt
        """
    And the command output should contain:
        """
        ABORTED: By user.

        Errored scenarios:
          features/aborting_in_before_scenario_hook.feature:7  S2 -- User aborts here

        0 features passed, 0 failed, 1 error, 0 skipped
        1 scenario passed, 0 failed, 1 hook_error, 0 skipped, 1 untested
        2 steps passed, 0 failed, 0 skipped, 4 untested
        """
    And the command output should contain:
        """
        Feature: User aborts test run in before_scenario hook of S2

          Scenario: S1
            Given a step passes ... passed
            When another step passes ... passed
        """
    But the command output should contain "Scenario: S2 -- User aborts here"
    But the command output should not contain "Scenario: S3"
    And note that "second scenario: only before_scenario hook is run"
    And note that "the third scenario is not run"


  Scenario: Abort test run in after_scenario hook
    Given a file named "features/aborting_in_after_scenario_hook.feature" with:
        """
        Feature: User aborts test run in after_scenario hook
          Scenario: S1
            Given a step passes
            When another step passes

          @user.aborts.after_scenario
          Scenario: S2 -- User aborts here
            Given first step passes
            When second step passes
            Then third step passes

          Scenario: S3
            Then last step passes
        """
    And a file named "features/environment.py" with:
        """
        def after_scenario(context, scenario):
            if "user.aborts.after_scenario" in scenario.tags:
                raise KeyboardInterrupt()
        """
    When I run "behave -f plain -T features/aborting_in_after_scenario_hook.feature"
    Then it should fail with:
        """
        ABORTED: HOOK-ERROR in after_scenario: KeyboardInterrupt
        """
    And the command output should contain:
        """
        ABORTED: By user.

        Errored scenarios:
          features/aborting_in_after_scenario_hook.feature:7  S2 -- User aborts here

        0 features passed, 0 failed, 1 error, 0 skipped
        1 scenario passed, 0 failed, 1 hook_error, 0 skipped, 1 untested
        5 steps passed, 0 failed, 0 skipped, 1 untested
        """
    But note that "the failing scenario is marked with hook_error"
    And the command output should contain:
        """
        Feature: User aborts test run in after_scenario hook

          Scenario: S1
            Given a step passes ... passed
            When another step passes ... passed

          Scenario: S2 -- User aborts here
            Given first step passes ... passed
            When second step passes ... passed
            Then third step passes ... passed
        """
    But the command output should not contain:
        """
          Scenario: S3
            Then last step passes ... passed
        """
    And note that "the last scenario is not run"


  Scenario: Abort test run in before_feature hook
    Given a file named "features/aborting_in_before_feature_hook.feature" with:
        """
        @user.aborts.before_feature
        Feature: User aborts test HERE
          Scenario:
            Given a step passes
            When another step passes

          Scenario:
            Given first step passes
            When second step passes
            Then third step passes

          Scenario:
            Then last step passes
        """
    And a file named "features/environment.py" with:
        """
        from __future__ import print_function

        def before_feature(context, feature):
            if "user.aborts.before_feature" in feature.tags:
                print("ABORTED in before_feature: %s" % feature.location)
                raise KeyboardInterrupt()
        """
    When I run "behave -f plain -T features/aborting_in_before_feature_hook.feature"
    Then it should fail with:
        """
        ABORTED: HOOK-ERROR in before_feature: KeyboardInterrupt
        """
    And the command output should contain:
        """
        ABORTED in before_feature: features/aborting_in_before_feature_hook.feature:2
        """
    And the command output should contain:
        """
        ABORTED: By user.
        0 features passed, 0 failed, 1 hook_error, 0 skipped
        0 scenarios passed, 0 failed, 0 skipped, 3 untested
        0 steps passed, 0 failed, 0 skipped, 6 untested
        """
    But note that "the feature fails with hook_error and is not run"


  Scenario: Abort test run in after_feature hook
    Given a file named "features/aborting_in_after_feature_hook.feature" with:
        """
        @user.aborts.after_feature
        Feature: User aborts test after HERE
          Scenario:
            Given a step passes
            When another step passes

          Scenario:
            Given first step passes
            When second step passes
            Then third step passes

          Scenario:
            Then last step passes
        """
    And a file named "features/environment.py" with:
        """
        def after_feature(context, feature):
            if "user.aborts.after_feature" in feature.tags:
                raise KeyboardInterrupt()
        """
    When I run "behave -f plain -T features/aborting_in_after_feature_hook.feature"
    Then it should fail with:
        """
        ABORTED: HOOK-ERROR in after_feature: KeyboardInterrupt
        """
    And the command output should contain:
        """
        ABORTED: By user.
        0 features passed, 0 failed, 1 hook_error, 0 skipped
        3 scenarios passed, 0 failed, 0 skipped
        6 steps passed, 0 failed, 0 skipped
        """
    But note that "the feature fails with hook_error"


  Scenario: Abort test run in before_all hook
    Given a file named "features/scenarios_pass3.feature" exists
    And a file named "features/environment.py" with:
      """
      def before_all(context):
          raise KeyboardInterrupt()   #< ABORT-HERE
      """
    When I run "behave -f plain -T features/scenarios_pass3.feature"
    Then it should fail with:
      """
      HOOK-ERROR in before_all: KeyboardInterrupt
      """
    And the command output should contain:
      """
      ABORTED: By user.
      0 features passed, 0 failed, 0 skipped, 1 untested
      0 scenarios passed, 0 failed, 0 skipped, 3 untested
      0 steps passed, 0 failed, 0 skipped, 6 untested
      """
    And note that "no features/scenarios/steps are run"


  Scenario: Abort test run in after_all hook
    Given a file named "features/scenarios_pass3.feature" exists
    And a file named "features/environment.py" with:
      """
      def after_all(context):
          raise KeyboardInterrupt()   #< ABORT-HERE
      """
    When I run "behave -f plain -T features/scenarios_pass3.feature"
    Then it should fail with:
      """
      HOOK-ERROR in after_all: KeyboardInterrupt
      """
    And the command output should contain:
      """
      ABORTED: By user.
      1 feature passed, 0 failed, 0 skipped
      3 scenarios passed, 0 failed, 0 skipped
      6 steps passed, 0 failed, 0 skipped
      """
    And note that "all features/scenarios/steps were run"
