@feature_request
@issue
Feature: Issue #228: Allow before_scenario to determine whether steps should be run.

  Allow before_scenario to call mark_skipped() and early out if the current
  scenario should be skipped.

  Scenario: Allow before_scenario to skip the current scenario

    Given a new working directory
    And a file named "features/steps/steps.py" with:
        """
        from behave import step

        @step('a step passes')
        def step_passes(context):
            pass
        """
    And a file named "features/environment.py" with
        """
        def before_scenario(context, scenario):
            if scenario.name == 'Skip this scenario':
                scenario.skip()
        """
    And a file named "features/issue228_example.feature" with
        """
        Feature:
          Scenario: Skip this scenario
            Given I'm using an "undefined step"

          Scenario: Run this scenario
            Given a step passes
        """
    When I run "behave -f plain features/issue228_example.feature"
    Then it should pass
     And the command output should contain:
        """
        1 feature passed, 0 failed, 0 skipped
        1 scenario passed, 0 failed, 1 skipped
        1 step passed, 0 failed, 1 skipped, 0 undefined
        """
