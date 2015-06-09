Feature: Runner should retry failed features a specified number of times

    As a tester or test writer
    I want failed features to be executed a specified number of times until they pass or until the retry count is reached
    So that tests are more resistant to uncontrollable failures (i.e. networking connectivity)

    . NOTES:
    .  Features with lasting side-effects need to be handled by the tester sepparately.

    @setup
    Scenario: Test Setup
        Given a new working directory
        And a file named "features/steps/steps.py" with:
            """
            from behave import step
            import sys

            @step('{word:w} step passes')
            def step_passes(context, word):
                pass

            @step('{word:w} step fails odd attempts')
            def step_fails_odd_attempts(context, word):
                context.user_data['even_test_attempt'] = not context.user_data['even_test_attempt']
                assert context.user_data['even_test_attempt'], "XFAIL (in: %s step)" % word
            """
        And a file named "features/alice.feature" with:
            """
            Feature: Alice
              Scenario: Passing
                Given first step passes
                When second step passes
                Then third step passes

              Scenario: Sometimes fails in second step
                Given a step passes
                When network step fails odd attempts
                Then another step passes
            """
        Given a file named "features/environment.py" with:
            """
            def before_all(context):
                context.user_data = {'even_test_attempt': True}

            def before_feature(context, feature):
                pass

            def before_scenario(context, scenario):
                pass
            """
        And a file named "behave.ini" with:
            """
            [behave]
            show_timings = false
            """

    Scenario: Runner fails with single retry
      When I run "behave -r 1 -f plain features/alice.feature"
      Then it should fail with:
          """
          Failing scenarios:
            features/alice.feature:7  Sometimes fails in second step
      
          0 features passed, 1 failed, 0 skipped
          1 scenario passed, 1 failed, 0 skipped
          4 steps passed, 1 failed, 1 skipped, 0 undefined
          """
      And the command output should contain:
          """
          Feature: Alice
      
            Scenario: Passing
              Given first step passes ... passed
              When second step passes ... passed
              Then third step passes ... passed
      
            Scenario: Sometimes fails in second step
              Given a step passes ... passed
              When network step fails odd attempts ... failed
          Assertion Failed: XFAIL (in: network step)
      
      
          Failing scenarios:
            features/alice.feature:7  Sometimes fails in second step
      
          0 features passed, 1 failed, 0 skipped
          1 scenario passed, 1 failed, 0 skipped
          4 steps passed, 1 failed, 1 skipped, 0 undefined
          """
      But note that "step execution continues after failed step(s)"
      And note that "no steps are skipped"


    Scenario: Runner passes with two retries
      When I run "behave -r 2 -f plain features/alice.feature"
      Then it should pass with:
          """ 
          1 feature passed, 0 failed, 0 skipped
          2 scenarios passed, 0 failed, 0 skipped
          6 steps passed, 0 failed, 0 skipped, 0 undefined
          """
      And the command output should contain:
          """
          Feature: Alice
      
            Scenario: Passing
              Given first step passes ... passed
              When second step passes ... passed
              Then third step passes ... passed
      
            Scenario: Sometimes fails in second step
              Given a step passes ... passed
              When network step fails odd attempts ... failed
          Assertion Failed: XFAIL (in: network step)

          Feature: Alice
      
            Scenario: Passing
              Given first step passes ... passed
              When second step passes ... passed
              Then third step passes ... passed
      
            Scenario: Sometimes fails in second step
              Given a step passes ... passed
              When network step fails odd attempts ... passed
              Then another step passes ... passed
     
      
          1 feature passed, 0 failed, 0 skipped
          2 scenarios passed, 0 failed, 0 skipped
          6 steps passed, 0 failed, 0 skipped, 0 undefined
          """
      But note that "step execution continues after failed step(s)"
      And note that "no steps are skipped"
