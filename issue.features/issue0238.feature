@issue
@feature_request
Feature: Issue #238 Skip a Scenario in a Scenario Outline

    Scenario:
      Given a new working directory
      And a file named "features/issue238_1.feature" with:
        """
        Feature: Testing Scenario skipping
            Scenario Outline:
                Given a set of "<thing>"
                When I ensure that "<thing>" != invalid
                Then it should pass

              Examples:
                | thing   |
                | valid   |
                | invalid |
        """
      And a file named "features/steps/steps.py" with:
        """
        @given('a set of "{thing}"')
        def step_check_thing_assumption(ctx, thing):
            if thing == "invalid":
                ctx.scenario.skip("ASSUMPTION-MISMATCH: INVALID-THING")

        @when('I ensure that "{thing}" != invalid')
        def step_ensure_that_thing_is_valid(ctx, thing):
            assert thing != "invalid"

        @then('it should pass')
        def step_passes(context):
            pass
        """
      When I run "behave -f plain --show-skipped --no-timings"
      Then it should pass with:
        """
        1 feature passed, 0 failed, 0 skipped
        1 scenario passed, 0 failed, 1 skipped
        3 steps passed, 0 failed, 3 skipped, 0 undefined
        """
      And the command output should contain:
        """
        Scenario Outline:  -- @1.1
          Given a set of "valid" ... passed
          When I ensure that "valid" != invalid ... passed
          Then it should pass ... passed

        Scenario Outline:  -- @1.2
          Given a set of "invalid" ... skipped
        """
      But note that "the step that skipped the scenario is also marked as skipped"