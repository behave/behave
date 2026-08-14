@issue
@autoretry
Feature: Issue #1128 -- scenario_autoretry does not reset runner.hook_failures

  Ensure that "patch_scenario_with_autoretry()" restores the test-runner state
  (the "runner.hook_failures" counter) between retry attempts.

  . REGRESSION: The "scenario_autoretry" monkey-patch retried a failed scenario,
  .   but did not reset "runner.hook_failures". If a "before_scenario" or
  .   "after_scenario" hook failed on the first attempt and then passed on the
  .   retry, the scenario was reported as PASSED, but behave still exited with
  .   failure because "runner.hook_failures" remained non-zero.
  .
  . RELATED:
  .  * features/runner.scenario_autoretry.feature
  .  * behave/contrib/scenario_autoretry.py

  Background:
    Given a new working directory
    And a file named "features/steps/reuse_steps.py" with:
        """
        import behave4cmd0.passing_steps
        """
    And a file named "features/environment.py" with:
        """
        from behave.contrib.scenario_autoretry import patch_scenario_with_autoretry

        # -- FAULT-INJECTION: Fail the "before_scenario" hook on the first
        # attempt only; it passes on the retry.
        before_scenario_calls = 0

        def before_feature(context, feature):
            for scenario in feature.scenarios:
                if "autoretry" in scenario.effective_tags:
                    patch_scenario_with_autoretry(scenario, max_attempts=2)

        def before_scenario(context, scenario):
            global before_scenario_calls
            before_scenario_calls += 1
            if before_scenario_calls == 1:
                raise RuntimeError("OOPS, before_scenario failed (first attempt)")
        """
    And a file named "features/unreliable_hook.feature" with:
        """
        @autoretry
        Feature: Alice
            Scenario: A1
              Given a step passes
        """
    And a file named "behave.ini" with:
        """
        [behave]
        show_timings = false
        """

  Scenario: Retry recovers from a hook failure and the test-run passes
    When I run "behave -f plain features/unreliable_hook.feature"
    Then it should pass with:
        """
        1 scenario passed, 0 failed, 0 skipped
        """
    And the command output should contain:
        """
        AUTO-RETRY SCENARIO (attempt 1)
        """
    But the command output should not contain:
        """
        AUTO-RETRY SCENARIO FAILED
        """
