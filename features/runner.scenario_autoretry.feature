Feature: Auto-retry failed scenarios (a number of times)

  As a tester in an unreliable environment
  I want that failed scenarios are automatically retried a number of times
  So that these scenarios are passing

  NOTE: 
  This problem should occur rather seldom, but may occur when the server or 
  network infrastructure, etc. is unreliable and causes random failures.


  @setup
  Scenario: Feature Setup
    Given a new working directory
    And a file named "features/steps/unreliable_steps.py" with:
        """
        from behave import given, step

        unreliable_step_passed_calls = 0

        @step(u'{word:w} unreliable step fails sometimes')
        def step_unreliable_step_fails_sometimes(context, word):
            global unreliable_step_passed_calls
            userdata = context.config.userdata
            fault_pos = userdata.getint("UNRELIABLE_FAULTPOS", 0)
            if fault_pos <= 0:
                return

            # -- NORMAL CASE: Unreliable step should every N calls.
            unreliable_step_passed_calls += 1
            if unreliable_step_passed_calls >= fault_pos:
                unreliable_step_passed_calls = 0
                assert False, "UNRELIABLE-STEP FAILURE"
        """
    And a file named "features/steps/reuse_steps.py" with:
        """
        import behave4cmd0.passing_steps
        """
    And a file named "features/environment.py" with:
        """
        from behave.contrib.scenario_autoretry import patch_scenario_with_autoretry

        def before_feature(context, feature):
            for scenario in feature.scenarios:
                if "autoretry" in scenario.effective_tags:
                    patch_scenario_with_autoretry(scenario, max_attempts=2)
        """
    And a file named "features/unreliable.feature" with:
        """
        @autoretry
        Feature: Alice
            Scenario: A1
              Given a step passes
              When an unreliable step fails sometimes
              Then another unreliable step fails sometimes

            Scenario: A2
              Given an unreliable step fails sometimes
              Then another step passes  
        """
    And a file named "behave.ini" with:
        """
        [behave]
        show_timings = false
        """


  Scenario: Retry failed scenarios
    When I run "behave -f plain -D UNRELIABLE_FAULTPOS=3 features/unreliable.feature"
    Then it should pass with:
        """
        2 scenarios passed, 0 failed, 0 skipped
        5 steps passed, 0 failed, 0 skipped, 0 undefined
        """
    And the command output should contain:
        """
        AUTO-RETRY SCENARIO (attempt 1)
        """
    But the command output should not contain:
        """
        AUTO-RETRY SCENARIO (attempt 2)
        """
    And the command output should contain:
        """
        Scenario: A1
          Given a step passes ... passed
          When an unreliable step fails sometimes ... passed
          Then another unreliable step fails sometimes ... passed
      
        Scenario: A2
          Given an unreliable step fails sometimes ... failed
        Assertion Failed: UNRELIABLE-STEP FAILURE
        AUTO-RETRY SCENARIO (attempt 1)
      
        Scenario: A2
          Given an unreliable step fails sometimes ... passed
          Then another step passes ... passed
        """

  Scenario: Scenarios failures are accepted after N=2 attempts
    When I run "behave -f plain -D UNRELIABLE_FAULTPOS=2 features/unreliable.feature"
    Then it should fail with:
        """
        1 scenario passed, 1 failed, 0 skipped
        4 steps passed, 1 failed, 0 skipped, 0 undefined
        """
    And the command output should not contain:
        """
        AUTO-RETRY SCENARIO (attempt 2)
        SCENARIO-FAILURE ACCEPTED (after 2 attempts)
        """
    And the command output should contain:
        """
        Scenario: A1
          Given a step passes ... passed
          When an unreliable step fails sometimes ... passed
          Then another unreliable step fails sometimes ... failed
        Assertion Failed: UNRELIABLE-STEP FAILURE
        AUTO-RETRY SCENARIO (attempt 1)
        
        Scenario: A1
          Given a step passes ... passed
           When an unreliable step fails sometimes ... passed
          Then another unreliable step fails sometimes ... failed
        Assertion Failed: UNRELIABLE-STEP FAILURE
        AUTO-RETRY SCENARIO FAILED (after 2 attempts)
      
        Scenario: A2
          Given an unreliable step fails sometimes ... passed
          Then another step passes ... passed
        """        