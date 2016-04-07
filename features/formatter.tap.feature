@sequential
Feature: Tap Formatter

    In order to effectively integrate with Tap (Test Anything Protocal)
    As a tester
    I want that behave outputs Tap

    @setup
    Scenario: Feature Setup
        Given a new working directory
        And a file named "features/steps/steps.py" with:
            """
            from behave import step

            @step('{word:w} step passes')
            def step_passes(context, word):
                pass

            @step('{word:w} step fails')
            def step_fails(context, word):
                assert False, "XFAIL-STEP"

            @step(u'a step raises an error "{message}"')
            def step_raises_exception(context, message):
                raise RuntimeError(message)
            """

    Scenario: Use Tap formatter on simple feature
        Given a file named "features/simple_feature_with_name.feature" with:
            """
            Feature: Simple, empty Feature
            """
        When I run "behave -f tap features/simple_feature_with_name.feature"
        Then it should pass with:
            """
            0 features passed, 0 failed, 1 skipped
            0 scenarios passed, 0 failed, 0 skipped
            """
        Then the tap command output should contain:
            """
            # Feature - Simple, empty Feature
            # ... features/simple_feature_with_name.feature:1
              1..0
            ok 1 Feature: Simple, empty Feature                                              # Skipped
            """

    Scenario: Use Tap formatter with feature and one scenario without steps
        Given a file named "features/simple_scenario.feature" with:
            """
            Feature: Simple feature with one scenario
              Scenario: Simple scenario without steps
            """
        When I run "behave -f tap features/simple_scenario.feature"
        Then it should pass with:
            """
            1 feature passed, 0 failed, 0 skipped
            1 scenario passed, 0 failed, 0 skipped
            """
        And the tap command output should contain:
            """
            # ... features/simple_scenario.feature:1
              # Scenario - Simple scenario without steps
              # ... features/simple_scenario.feature:2
                1..0
              ok 1 Scenario: Simple scenario without steps                                     # 
              1..1
            ok 1 Feature: Simple feature with one scenario                                   # 
            1..1
            """

    Scenario: Use Tap formatter with feature and one scenario with all passing steps
        Given a file named "features/scenario_with_steps.feature" with:
            """
            Feature: Feature with scenario
              Scenario: Simple scenario with passing steps
                  Given a step passes
                  When another step passes
                  Then third step passes
                  And fourth step passes
                  But fifth step passes
            """
        When I run "behave -f tap features/scenario_with_steps.feature"
        Then it should pass with:
            """
            1 feature passed, 0 failed, 0 skipped
            1 scenario passed, 0 failed, 0 skipped
            """
        And the tap command output should contain:
				    """
             # ... features/scenario_with_steps.feature:1
               # Scenario - Simple scenario with passing steps
               # ... features/scenario_with_steps.feature:2
                 ok 1 Given a step passes                                                         # 
                 ok 2 When another step passes                                                    # 
                 ok 3 Then third step passes                                                      # 
                 ok 4 And fourth step passes                                                      # 
                 ok 5 But fifth step passes                                                       # 
                 1..5
               ok 1 Scenario: Simple scenario with passing steps                                # 
               1..1
             ok 1 Feature: Feature with scenario                                              # 
             1..1
            """

    Scenario: Use Tap formatter with feature and one scenario with a failing step
        Given a file named "features/scenario_with_steps.feature" with:
            """
            Feature: Feature with scenario
              Scenario: Simple scenario with last failing step
                  Given a step passes
                  When second step passes
                  Then third step passes
                  And another step passes
                  But last step fails
            """
        When I run "behave -f tap features/scenario_with_steps.feature"
        Then it should fail with:
            """
            0 features passed, 1 failed, 0 skipped
            0 scenarios passed, 1 failed, 0 skipped
            """
        And the tap command output should contain:
            """
             # Feature - Feature with scenario
             # ... features/scenario_with_steps.feature:1
               # Scenario - Simple scenario with last failing step
               # ... features/scenario_with_steps.feature:2
                 ok 1 Given a step passes                                                         # 
                 ok 2 When second step passes                                                     # 
                 ok 3 Then third step passes                                                      # 
                 ok 4 And another step passes                                                     # 
                 not ok 5 But last step fails                                                     # 
                 # Assertion Failed: XFAIL-STEP
                 1..5
               not ok 1 Scenario: Simple scenario with last failing step                        # 
               1..1
             not ok 1 Feature: Feature with scenario                                          # 
             1..1
            """

    Scenario: Use Tap formatter with feature and one scenario with an exception in the step
        Given a file named "features/scenario_with_steps.feature" with:
            """
            Feature: Feature with scenario
              Scenario: Simple scenario with error in the step
                  Given a step passes
                  When second step passes
                  Then third step passes
                  And another step passes
                  But a step raises an error "Error message here"
            """
        When I run "behave -f tap features/scenario_with_steps.feature"
        Then it should fail with:
            """
            0 features passed, 1 failed, 0 skipped
            0 scenarios passed, 1 failed, 0 skipped
            """
        And the tap command output should contain:
            """
             # Feature - Feature with scenario
             # ... features/scenario_with_steps.feature:1
               # Scenario - Simple scenario with error in the step
               # ... features/scenario_with_steps.feature:2
                 ok 1 Given a step passes                                                         # 
                 ok 2 When second step passes                                                     # 
                 ok 3 Then third step passes                                                      # 
                 ok 4 And another step passes                                                     # 
                 not ok 5 But a step raises an error "Error message here"                         # 
                 # Traceback (most recent call last):
               File "/home/jgowan/opensource/behave/behave/model.py", line 1279, in run
                 match.run(runner.context)
               File "/home/jgowan/opensource/behave/behave/matchers.py", line 98, in run
                 self.func(context, *args, **kwargs)
               File "features/steps/steps.py", line 13, in step_raises_exception
                 raise RuntimeError(message)
             RuntimeError: Error message here
             
                 1..5
               not ok 1 Scenario: Simple scenario with error in the step                        # 
               1..1
             not ok 1 Feature: Feature with scenario                                          # 
             1..1
            """

    Scenario: Use Tap formatter with feature and three scenarios with all passing steps
        Given a file named "features/scenario_with_steps.feature" with:
            """
            Feature: Feature with three scenarios
              Scenario: First scenario with passing steps
                  Given a step passes
                  When second step passes
                  Then third step passes
                  And another step passes
                  But last step passes

              Scenario: Second scenario with passing steps
                  Given a step passes
                  When second step passes
                  Then third step passes
                  And another step passes
                  But last step passes

              Scenario: Third scenario with passing steps
                  Given a step passes
                  When second step passes
                  Then third step passes
                  And another step passes
                  But last step passes
            """
        When I run "behave -f tap features/scenario_with_steps.feature"
        Then it should pass with:
            """
            1 feature passed, 0 failed, 0 skipped
            3 scenarios passed, 0 failed, 0 skipped
            15 steps passed, 0 failed, 0 skipped, 0 undefined
            """
        And the tap command output should contain:
            """
             # Feature - Feature with three scenarios
             # ... features/scenario_with_steps.feature:1
               # Scenario - First scenario with passing steps
               # ... features/scenario_with_steps.feature:2
                 ok 1 Given a step passes                                                         # 
                 ok 2 When second step passes                                                     # 
                 ok 3 Then third step passes                                                      # 
                 ok 4 And another step passes                                                     # 
                 ok 5 But last step passes                                                        # 
                 1..5
               ok 1 Scenario: First scenario with passing steps                                 # 
               # Scenario - Second scenario with passing steps
               # ... features/scenario_with_steps.feature:9
                 ok 1 Given a step passes                                                         # 
                 ok 2 When second step passes                                                     # 
                 ok 3 Then third step passes                                                      # 
                 ok 4 And another step passes                                                     # 
                 ok 5 But last step passes                                                        # 
                 1..5
               ok 2 Scenario: Second scenario with passing steps                                # 
               # Scenario - Third scenario with passing steps
               # ... features/scenario_with_steps.feature:16
                 ok 1 Given a step passes                                                         # 
                 ok 2 When second step passes                                                     # 
                 ok 3 Then third step passes                                                      # 
                 ok 4 And another step passes                                                     # 
                 ok 5 But last step passes                                                        # 
                 1..5
               ok 3 Scenario: Third scenario with passing steps                                 # 
               1..3
             ok 1 Feature: Feature with three scenarios                                       # 
             1..1
            """

    Scenario: Use Tap formatter with feature and three scenarios with a failing step
        Given a file named "features/scenario_with_steps.feature" with:
            """
            Feature: Feature with various results in scenarios
              Scenario: First scenario with passing steps
                  Given a step passes
                  When second step passes
                  Then third step passes
                  And another step passes
                  But last step passes

              Scenario: Second scenario with second failing step
                  Given a step passes
                  When second step fails
                  Then third step passes
                  And another step passes
                  But last step passes

              Scenario: Third scenario with fourth failing step
                  Given a step passes
                  When second step passes
                  Then third step passes
                  And fourth step fails
                  But last step passes
            """
        When I run "behave -f tap features/scenario_with_steps.feature"
        Then it should fail with:
            """
            0 features passed, 1 failed, 0 skipped
            1 scenario passed, 2 failed, 0 skipped
            9 steps passed, 2 failed, 4 skipped, 0 undefined
            """
        And the tap command output should contain:
            """
            # Feature - Feature with various results in scenarios
            # ... features/scenario_with_steps.feature:1
              # Scenario - First scenario with passing steps
              # ... features/scenario_with_steps.feature:2
                ok 1 Given a step passes                                                         # 
                ok 2 When second step passes                                                     # 
                ok 3 Then third step passes                                                      # 
                ok 4 And another step passes                                                     # 
                ok 5 But last step passes                                                        # 
                1..5
              ok 1 Scenario: First scenario with passing steps                                 # 
              # Scenario - Second scenario with second failing step
              # ... features/scenario_with_steps.feature:9
                ok 1 Given a step passes                                                         # 
                not ok 2 When second step fails                                                  # 
                # Assertion Failed: XFAIL-STEP
                1..2
              not ok 2 Scenario: Second scenario with second failing step                      # 
              # Scenario - Third scenario with fourth failing step
              # ... features/scenario_with_steps.feature:16
                ok 1 Given a step passes                                                         # 
                ok 2 When second step passes                                                     # 
                ok 3 Then third step passes                                                      # 
                not ok 4 And fourth step fails                                                   # 
                # Assertion Failed: XFAIL-STEP
                1..4
              not ok 3 Scenario: Third scenario with fourth failing step                       # 
              1..3
            not ok 1 Feature: Feature with various results in scenarios                      # 
            1..1
            """

    Scenario: Use Tap formatter with feature and three scenarios with a skipped scenario
        Given a file named "features/scenario_with_steps.feature" with:
            """
            Feature: Feature with various results in scenarios
              Scenario: First scenario with passing steps
                  Given a step passes
                  When second step passes
                  Then third step passes
                  And another step passes
                  But last step passes

              @skip
              Scenario: Second scenario with second failing step
                  Given a step passes
                  When second step fails
                  Then third step passes
                  And another step passes
                  But last step passes

              Scenario: Third scenario with fourth failing step
                  Given a step passes
                  When second step passes
                  Then third step passes
                  And fourth step fails
                  But last step passes
            """
        When I run "behave --tags ~@skip -f tap features/scenario_with_steps.feature"
        Then it should fail with:
            """
            0 features passed, 1 failed, 0 skipped
            1 scenario passed, 1 failed, 1 skipped
            8 steps passed, 1 failed, 6 skipped, 0 undefined
            """
        And the tap command output should contain:
            """
            # Feature - Feature with various results in scenarios
            # ... features/scenario_with_steps.feature:1
              # Scenario - First scenario with passing steps
              # ... features/scenario_with_steps.feature:2
                ok 1 Given a step passes                                                         # 
                ok 2 When second step passes                                                     # 
                ok 3 Then third step passes                                                      # 
                ok 4 And another step passes                                                     # 
                ok 5 But last step passes                                                        # 
                1..5
              ok 1 Scenario: First scenario with passing steps                                 # 
              # Scenario - Second scenario with second failing step
              # ... features/scenario_with_steps.feature:10
                1..0 # Skipped
              ok 2 Scenario: Second scenario with second failing step                          # Skipped 
              # Scenario - Third scenario with fourth failing step
              # ... features/scenario_with_steps.feature:17
                ok 1 Given a step passes                                                         # 
                ok 2 When second step passes                                                     # 
                ok 3 Then third step passes                                                      # 
                not ok 4 And fourth step fails                                                   # 
                # Assertion Failed: XFAIL-STEP
                1..4
              not ok 3 Scenario: Third scenario with fourth failing step                       # 
              1..3
            not ok 1 Feature: Feature with various results in scenarios                      # 
            1..1
            """

    Scenario: Use Tap formatter with feature and three scenarios with a skipped feature
        Given a file named "features/scenario_with_steps.feature" with:
            """
            @skip
            Feature: Feature with various results in scenarios
              Scenario: First scenario with passing steps
                  Given a step passes
                  When second step passes
                  Then third step passes
                  And another step passes
                  But last step passes

              Scenario: Third scenario with fourth failing step
                  Given a step passes
                  When second step passes
                  Then third step passes
                  And fourth step fails
                  But last step passes
            """
        When I run "behave --tags ~@skip -f tap features/scenario_with_steps.feature"
        Then it should pass with:
            """
            0 features passed, 0 failed, 1 skipped
            0 scenarios passed, 0 failed, 2 skipped
            0 steps passed, 0 failed, 10 skipped, 0 undefined
            """
        And the tap command output should contain:
            """
            # Feature - Feature with various results in scenarios
            # ... features/scenario_with_steps.feature:2
              # Scenario - First scenario with passing steps
              # ... features/scenario_with_steps.feature:3
                1..0 # Skipped
              ok 1 Scenario: First scenario with passing steps                                 # Skipped 
              # Scenario - Third scenario with fourth failing step
              # ... features/scenario_with_steps.feature:10
                1..0 # Skipped
              ok 2 Scenario: Third scenario with fourth failing step                           # Skipped 
              1..2
            ok 1 Feature: Feature with various results in scenarios                          # Skipped 
            1..1
            """
