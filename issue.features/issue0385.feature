@issue
@change_request
Feature: Issue #385 -- before_scenario called too late

    . RATIONALE:
    . Due to:
    .
    .   * skip scenario/feature support in before_scenario (and before_feature) hooks
    .   * active-tags
    .
    . formatters are now called to early (for before feature/scenario functionality).
    . Formatters should be called after the before-hooks are processed.
    .
    . NOTES:
    .  * Test uses show_skipped=false to ensure that at least the
    .    scenario/feature title is shown with plain formatter.

    @setup
    Scenario:
      Given a new working directory
      And a file named "features/steps/pass_steps.py" with:
        """
        from behave import step

        @step('{word:w} step passes')
        def step_passes(context, word):
            pass
        """
      And a file named "features/environment.py" with:
        """
        from __future__ import print_function

        def before_feature(context, feature):
            if "skip" in feature.tags:
                print("SKIP-FEATURE: %s" % feature.name)
                feature.mark_skipped()

        def before_scenario(context, scenario):
            if "skip" in scenario.tags:
                print("SKIP-SCENARIO: %s" % scenario.name)
                scenario.mark_skipped()
        """
      And a file named "behave.ini" with:
        """
        [behave]
        show_skipped = false
        """

    Scenario: Formatter is not called with skip in before_scenario hook
      Given a file named "features/alice.feature" with:
        """
        Feature: Alice

          @skip
          Scenario: Alice and Bob
            Given a step passes

          Scenario: Alice in China
            When another step passes
        """
      When I run "behave -f plain features/alice.feature"
      Then it should pass with:
        """
        1 scenario passed, 0 failed, 1 skipped
        """
      And the command output should contain:
        """
        SKIP-SCENARIO: Alice and Bob

        Scenario: Alice in China
          When another step passes ... passed
        """
      But the command output should not contain:
        """
        Scenario: Alice and Bob
        SKIP-FEATURE: Alice and Bob
        """
      And the command output should not contain "Scenario: Alice and Bob"


    Scenario: Formatter is not called with skip in before_feature hook
      Given a file named "features/bob.feature" with:
        """
        @skip
        Feature: Bob

          Scenario: Bob and Alice
            Given a step passes

          Scenario: Bob in China
            When another step passes
        """
      When I run "behave -f plain features/bob.feature"
      Then it should pass with:
        """
        SKIP-FEATURE: Bob

        0 features passed, 0 failed, 1 skipped
        0 scenarios passed, 0 failed, 2 skipped
        """
      But the command output should not contain:
        """
        Feature: Bob
        SKIP-FEATURE: Bob
        """
      And the command output should not contain "Feature: Bob"
      And the command output should not contain "Scenario: Bob and Alice"
      And the command output should not contain "Scenario: Bob in China"
      And note that "all scenarios of the feature are also skipped"
