@issue
@mistaken
Feature: Issue #673 -- @given and @Given step decorators with wildcard import


    Scenario: Ensure that wildcard imports work for step decorators
      Given a new working directory
      And a file named "features/steps/wildcard_import_steps.py" with:
        """
        from behave import *

        @given(u'a step passes')
        def given_step_passes(context):
            pass

        @Given(u'another step passes')
        def given_step_passes2(context):
            pass

        @step('{word:w} step passes')
        def step_passes(context, word):
            pass
        """
      And a file named "features/basic.feature" with:
        """
        Feature:
          Scenario:
            Given a step passes
            And another step passes
            When some step passes
        """
      When I run "behave -f pretty --no-color features/basic.feature"
      Then it should pass with:
        """
        3 steps passed, 0 failed, 0 skipped, 0 undefined
        """
      And the command output should contain:
        """
        Scenario:                 # features/basic.feature:2
          Given a step passes     # features/steps/wildcard_import_steps.py:3
          And another step passes # features/steps/wildcard_import_steps.py:7
          When some step passes   # features/steps/wildcard_import_steps.py:11
        """
