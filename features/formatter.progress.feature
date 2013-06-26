@sequential
Feature: Progress3 Formatter

    In order to effectively analyze output of many runs
    As a tester
    I want that behave generates to present results for each scenario

    @setup
    Scenario: Feature Setup
        Given a new working directory
        And a file named "features/steps/steps.py" with:
            """
            from behave import step

            @step('a step passes')
            def step_passes(context):
                pass

            @step('a step fails')
            def step_fails(context):
                assert False, "XFAIL-STEP"

            @step(u'a step raises an error "{message}"')
            def step_raises_exception(context, message):
                raise RuntimeError(message)
            """

    Scenario: Use Progress3 formatter on simple feature
        Given a file named "features/simple_feature_with_name.feature" with:
            """
            Feature: Simple, empty Feature
            """
        When I run "behave -f progress3 features/simple_feature_with_name.feature"
        Then it should pass with:
            """
            0 features passed, 0 failed, 1 skipped
            0 scenarios passed, 0 failed, 0 skipped
            """
        And the command output should contain:
            """
            Simple, empty Feature (features/simple_feature_with_name.feature):
            """

    Scenario: Use Progress3 formatter with feature and one scenario without steps
        Given a file named "features/simple_scenario.feature" with:
            """
            Feature: Simple feature with one scenario
              Scenario: Simple scenario without steps
            """
        When I run "behave -f progress3 features/simple_scenario.feature"
        Then it should pass with:
            """
            1 feature passed, 0 failed, 0 skipped
            1 scenario passed, 0 failed, 0 skipped
            """
        And the command output should contain:
            """
            Simple feature with one scenario (features/simple_scenario.feature):
                Simple scenario without steps: 
            """

    Scenario: Use Progress3 formatter with feature and one scenario with all passing steps
        Given a file named "features/scenario_with_steps.feature" with:
            """
            Feature: Feature with scenario
              Scenario: Simple scenario with passing steps
                  Given a step passes
                  When a step passes
                  Then a step passes
                  And a step passes
                  But a step passes
            """
        When I run "behave -f progress3 features/scenario_with_steps.feature"
        Then it should pass with:
            """
            1 feature passed, 0 failed, 0 skipped
            1 scenario passed, 0 failed, 0 skipped
            """
        And the command output should contain:
            """
            Feature with scenario (features/scenario_with_steps.feature):
                Simple scenario with passing steps: .....
            """

    Scenario: Use Progress3 formatter with feature and one scenario with a failing step
        Given a file named "features/scenario_with_steps.feature" with:
            """
            Feature: Feature with scenario
              Scenario: Simple scenario with last failing step
                  Given a step passes
                  When a step passes
                  Then a step passes
                  And a step passes
                  But a step fails
            """
        When I run "behave -f progress3 features/scenario_with_steps.feature"
        Then it should fail with:
            """
            0 features passed, 1 failed, 0 skipped
            0 scenarios passed, 1 failed, 0 skipped
            """
        And the command output should contain:
            """
            Feature with scenario (features/scenario_with_steps.feature):
                Simple scenario with last failing step: ....F
            --------------------------------------------------------------------------------
            FAILURE in step 'a step fails' (features/scenario_with_steps.feature:7):
            Assertion Failed: XFAIL-STEP
            --------------------------------------------------------------------------------
            """

    Scenario: Use Progress3 formatter with feature and one scenario with an exception in the step
        Given a file named "features/scenario_with_steps.feature" with:
            """
            Feature: Feature with scenario
              Scenario: Simple scenario with error in the step
                  Given a step passes
                  When a step passes
                  Then a step passes
                  And a step passes
                  But a step raises an error "Error message here"
            """
        When I run "behave -f progress3 features/scenario_with_steps.feature"
        Then it should fail with:
            """
            0 features passed, 1 failed, 0 skipped
            0 scenarios passed, 1 failed, 0 skipped
            """
        And the command output should contain:
            """
            Feature with scenario (features/scenario_with_steps.feature):
                Simple scenario with error in the step: ....E
            --------------------------------------------------------------------------------
            FAILURE in step 'a step raises an error "Error message here"' (features/scenario_with_steps.feature:7):
            """
        And the command output should contain:
            """
            RuntimeError: Error message here
            
            --------------------------------------------------------------------------------
            """

    Scenario: Use Progress3 formatter with feature and three scenarios with all passing steps
        Given a file named "features/scenario_with_steps.feature" with:
            """
            Feature: Feature with three scenarios
              Scenario: Simple scenario with passing steps
                  Given a step passes
                  When a step passes
                  Then a step passes
                  And a step passes
                  But a step passes
              Scenario: Another scenario with passing steps
                  Given a step passes
                  When a step passes
                  Then a step passes
                  And a step passes
                  But a step passes
              Scenario: One more scenario with passing steps
                  Given a step passes
                  When a step passes
                  Then a step passes
                  And a step passes
                  But a step passes
            """
        When I run "behave -f progress3 features/scenario_with_steps.feature"
        Then it should pass with:
            """
            1 feature passed, 0 failed, 0 skipped
            3 scenarios passed, 0 failed, 0 skipped
            15 steps passed, 0 failed, 0 skipped, 0 undefined
            """
        And the command output should contain:
            """
            Feature with three scenarios (features/scenario_with_steps.feature):
                Simple scenario with passing steps: .....
                Another scenario with passing steps: .....
                One more scenario with passing steps: .....
            """

    Scenario: Use Progress3 formatter with feature and three scenarios with a failing step
        Given a file named "features/scenario_with_steps.feature" with:
            """
            Feature: Feature with various results in scenarios
              Scenario: Simple scenario with passing steps
                  Given a step passes
                  When a step passes
                  Then a step passes
                  And a step passes
                  But a step passes
              Scenario: Simple scenario with second failing step
                  Given a step passes
                  When a step fails
                  Then a step passes
                  And a step passes
                  But a step passes
              Scenario: Simple scenario with fourth failing step
                  Given a step passes
                  When a step passes
                  Then a step passes
                  And a step fails
                  But a step passes
            """
        When I run "behave -f progress3 features/scenario_with_steps.feature"
        Then it should fail with:
            """
            0 features passed, 1 failed, 0 skipped
            1 scenario passed, 2 failed, 0 skipped
            9 steps passed, 2 failed, 4 skipped, 0 undefined
            """
        And the command output should contain:
            """
            Feature with various results in scenarios (features/scenario_with_steps.feature):
                Simple scenario with passing steps: .....
                Simple scenario with second failing step: .F
            --------------------------------------------------------------------------------
            FAILURE in step 'a step fails' (features/scenario_with_steps.feature:10):
            Assertion Failed: XFAIL-STEP
            --------------------------------------------------------------------------------
            
                Simple scenario with fourth failing step: ...F
            --------------------------------------------------------------------------------
            FAILURE in step 'a step fails' (features/scenario_with_steps.feature:18):
            Assertion Failed: XFAIL-STEP
            --------------------------------------------------------------------------------
            
            
            Failing scenarios:
              features/scenario_with_steps.feature:8  Simple scenario with second failing step
              features/scenario_with_steps.feature:14  Simple scenario with fourth failing step
            """
