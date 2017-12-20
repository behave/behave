@issue
Feature: Issue #462-- Invalid JSON output when --include option selects no features

  . Invalid JSON output is generated when no features are selected in a test-run.
  . For example, this may be the case when the --include option is used.


    Background:
      Given a new working directory
      And a file named "features/steps/pass_steps.py" with:
        """
        from behave import step

        @step('{word:w} step passes')
        def step_passes(context, word):
            pass
        """
      And a file named "features/passing.feature" with:
        """
        Feature:
          Scenario:
            Given a step passes
        """


    Scenario: Include Option selects no feature files
      When I run "behave -f json -i __unknown__.feature"
      Then it should pass with:
        """
        0 features passed, 0 failed, 0 skipped
        0 scenarios passed, 0 failed, 0 skipped
        """
      And the command output should contain:
        """
        [
        ]
        """

