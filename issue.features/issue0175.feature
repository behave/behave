@issue
Feature: Issue #175: Scenario isn't marked as 'failed' when Background step fails

  Scenario has currently status "skipped" when a background step fails.
  Expected is that scenario status should be "failed".
  Ensure that this is the case.

  RELATED: features/background.feature
  REUSE:   Scenario from there (as copy).

  | NOTE:
  |     Cucumber has a slightly different behaviour.
  |     When a background step fails the first scenario is marked as failed.
  |     But the remaining scenarios are marked as skipped.
  |
  |     This can lead to problems when you have sporadic background step failures.
  |     For this reason, behave retries the background steps for each scenario.
  |
  | SEE ALSO:
  |   * https://github.com/cucumber/cucumber/blob/master/features/docs/gherkin/background.feature


  @setup
  Scenario: Feature Setup
    Given a new working directory
    And a file named "features/steps/background_steps.py" with:
        """
        from behave import step

        @step('{word} background step {outcome}')
        def step_background_step_passes_or_fails(context, word, outcome):
            if outcome == "fails":
                assert False, "XFAIL: background step"
            elif outcome == "passes":
                pass
            else:
                message = "Unexpected outcome=%s. Use: passes, fails"
                raise RuntimeError(message % outcome)
        """
    And a file named "features/steps/passing_steps.py" with:
        """
        from behave import step

        @step('{word} step passes')
        def step_passes(context, word):
            pass

        @step('{word} step fails')
        def step_passes(context, word):
            assert False, "XFAIL"
        """


  Scenario: Failing Background Step causes all Scenarios to fail
    Given a file named "features/example.background_step_fails.feature" with:
        """
        Feature:

          Background: B1
            Given a background step passes
            And a background step fails
            And another background step passes

          Scenario: S1
            When a step passes

          Scenario: S2
            Then a step passes
            And another step passes
        """
    When I run "behave -f plain -T features/example.background_step_fails.feature"
    Then it should fail with:
        """
        0 scenarios passed, 2 failed, 0 skipped
        2 steps passed, 2 failed, 5 skipped, 0 undefined
        """
    And the command output should contain:
        """
        Feature:
          Background: B1

          Scenario: S1
            Given a background step passes ... passed
            And a background step fails ... failed
        Assertion Failed: XFAIL: background step

          Scenario: S2
            Given a background step passes ... passed
            And a background step fails ... failed
        Assertion Failed: XFAIL: background step
        """
