@issue
Feature: Issue #467 -- Scenario status when scenario w/o steps is skipped

  . The scenario.status should be "skipped"
  . if you try to skip a scenario without any steps.


    Scenario: Skip scenario without steps
      Given a new working directory
      And a file named "features/steps/pass_steps.py" with:
        """
        from behave import step

        @step('{word:w} step passes')
        def step_passes(context, word):
            pass
        """
      And a file named "features/without_steps.feature" with:
        """
        Feature:
          @skip_this
          Scenario: Without steps
        """
      And a file named "features/environment.py" with:
        """
        def before_scenario(context, scenario):
            if "skip_this" in scenario.tags:
                scenario.skip()
        """
      When I run "behave -f plain features/without_steps.feature"
      Then it should pass with:
        """
        Feature:
          Scenario: Without steps

        0 features passed, 0 failed, 1 skipped
        0 scenarios passed, 0 failed, 1 skipped
        """
      But note that "the scenario without steps is skipped"
