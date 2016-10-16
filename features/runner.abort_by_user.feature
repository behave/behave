Feature: Test run can be aborted by the user

  As a tester
  I want sometimes to abort a test run (because it is anyway failing, etc.)
  So that I am more productive.

  . NOTES:
  .  * The test runner should fail gracefully (most of the times)
  .  * At least some cleanup hooks should be called (in general)


  @setup
  Scenario: Feature Setup
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
          Scenario:
            Given a step passes
            When another step passes

          Scenario: User aborts here
            Given first step passes
            When the user aborts the test run
            Then third step passes

          Scenario:
            Then last step passes
        """
    And an empty file named "features/environment.py"
    When I run "behave -f plain -T features/aborting_in_step.feature"
    Then it should fail with:
        """
        0 features passed, 1 failed, 0 skipped
        1 scenario passed, 1 failed, 0 skipped, 1 untested
        3 steps passed, 1 failed, 1 skipped, 0 undefined, 1 untested
        """
    And the command output should contain:
        """
        Feature: User aborts test run in a step definition

        Scenario:
          Given a step passes ... passed
          When another step passes ... passed

        Scenario: User aborts here
          Given first step passes ... passed
          When the user aborts the test run ... failed
        ABORTED: By user (KeyboardInterrupt).

        ABORTED: By user.

        Failing scenarios:
          features/aborting_in_step.feature:6  User aborts here
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
        ABORTED: By user.
        0 features passed, 1 failed, 0 skipped
        1 scenario passed, 0 failed, 0 skipped, 2 untested
        2 steps passed, 0 failed, 0 skipped, 0 undefined, 4 untested
        """
    And the command output should contain:
        """
        Feature: User aborts test run in before_scenario hook of S2

          Scenario: S1
            Given a step passes ... passed
            When another step passes ... passed
        """
    But the command output should not contain "Scenario: S2 -- User aborts here"
    But the command output should not contain "Scenario: S3"
    And note that "the second and third scenario is not run"


  Scenario: Abort test run in after_scenario hook
    Given a file named "features/aborting_in_after_scenario_hook.feature" with:
        """
        Feature: User aborts test run in after_scenario hook
          Scenario:
            Given a step passes
            When another step passes

          @user.aborts.after_scenario
          Scenario: User aborts here
            Given first step passes
            When second step passes
            Then third step passes

          Scenario:
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
        ABORTED: By user.
        0 features passed, 1 failed, 0 skipped
        2 scenarios passed, 0 failed, 0 skipped, 1 untested
        5 steps passed, 0 failed, 0 skipped, 0 undefined, 1 untested
        """
    And the command output should contain:
        """
        Feature: User aborts test run in after_scenario hook

          Scenario:
            Given a step passes ... passed
            When another step passes ... passed

          Scenario: User aborts here
            Given first step passes ... passed
            When second step passes ... passed
            Then third step passes ... passed
        """
    But the command output should not contain:
        """
          Scenario:
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
        ABORTED in before_feature: features/aborting_in_before_feature_hook.feature:2

        ABORTED: By user.
        0 features passed, 0 failed, 0 skipped, 1 untested
        0 scenarios passed, 0 failed, 0 skipped, 3 untested
        0 steps passed, 0 failed, 0 skipped, 0 undefined, 6 untested
        """
    But note that "the feature is not run"
    And note that "the formatters are not informed of this feature"


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
        ABORTED: By user.
        1 feature passed, 0 failed, 0 skipped
        3 scenarios passed, 0 failed, 0 skipped
        6 steps passed, 0 failed, 0 skipped, 0 undefined
        """
    But note that "the behave command fails, but all features/scenarios passed"


  Scenario: Abort test run in before_all hook

    Note that this situation is not handled very gracefully (yet).

      Given a file named "features/scenarios_pass3.feature" exists
      And a file named "features/environment.py" with:
        """
        def before_all(context):
            raise KeyboardInterrupt()   #< ABORT-HERE
        """
      When I run "behave -f plain -T features/scenarios_pass3.feature"
      Then it should fail with:
        """
        Traceback (most recent call last):
        """
      And the command output should contain:
        """
        File "features/environment.py", line 2, in before_all
          raise KeyboardInterrupt()   #< ABORT-HERE
        """
      And note that "no feature is not run"


  Scenario: Abort test run in after_all hook

    Note that this situation is not handled very gracefully (yet).

      Given a file named "features/scenarios_pass3.feature" exists
      And a file named "features/environment.py" with:
        """
        def after_all(context):
            raise KeyboardInterrupt()   #< ABORT-HERE
        """
      When I run "behave -f plain -T features/scenarios_pass3.feature"
      Then it should fail with:
        """
        Traceback (most recent call last):
        """
      And the command output should contain:
        """
        File "features/environment.py", line 2, in after_all
          raise KeyboardInterrupt()   #< ABORT-HERE
        """
      And note that "all features are run"
