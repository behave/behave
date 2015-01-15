@feature_request
@background_hook
Feature: Issue #290: Call before/after_background_hooks when running backgrounds

  Provide environment hooks before_background and after_background to
  allow eg. caching of complicated backgrounds

  Background:
    Given a new working directory
    And a file named "features/steps/steps.py" with:
        """
        from behave import step

        @step('a background step')
        def background_step(context):
            print ('background_step')

        @step('{step_name} step fails')
        def step_fails(context, step_name):
            print (step_name+' step')
            assert False

        @step('{step_name} step succeeds')
        def step_fails(context, step_name):
            print (step_name+' step')
        """
    And a file named "features/backgroundhook_example.feature" with
        """
        Feature:

          Background:
            Given a background step

          Scenario: A scenario
            Given a step succeeds

          Scenario: Another scenario to check hook fired twice
            Given another step fails
        """

  Scenario: before_background_hook is called before given step
    Given a file named "features/environment.py" with
        """
        def before_background(context, background):
            print ('before_background hook called')
        """
    When I run "behave -f plain --no-capture features/backgroundhook_example.feature"
    Then it should fail
    And the command output should contain:
        """
        Scenario: A scenario
        before_background hook called
        background_step
        Given a background step ... passed
        a step
        Given a step succeeds ... passed
        """
        
     And the command output should contain:
        """
        Scenario: Another scenario to check hook fired twice
        before_background hook called
        background_step
        Given a background step ... passed
        another step
        Given another step fails ... failed
        """

    And the command output should contain:
        """
        0 features passed, 1 failed, 0 skipped
        1 scenario passed, 1 failed, 0 skipped
        3 steps passed, 1 failed, 0 skipped, 0 undefined
        """

  Scenario: after_background_hook is called after given step
    Given a file named "features/environment.py" with
        """
        def after_background(context, background):
            print ("after_background hook called")
        """
    When I run "behave -f plain --no-capture features/backgroundhook_example.feature"
    Then it should fail
     And the command output should contain:
        """
        Scenario: A scenario
        background_step
        Given a background step ... passed
        after_background hook called
        a step
        Given a step succeeds ... passed
        """

     And the command output should contain:
        """
        Scenario: Another scenario to check hook fired twice
        background_step
        Given a background step ... passed
        after_background hook called
        another step
        Given another step fails ... failed
        """

    And the command output should contain:
        """
        0 features passed, 1 failed, 0 skipped
        1 scenario passed, 1 failed, 0 skipped
        3 steps passed, 1 failed, 0 skipped, 0 undefined
        """
