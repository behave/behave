Feature: Runner should continue after a failed step

    As a tester or test writer
    I want that the remaining scenario steps are executed even when a step fails
    So that I see all remaining failures.

    . NOTES:
    .  This may cause a number of correlated failures in the remaining steps.
    .  Therefore the default behavior of the runner is to skip the
    .  remaining scenario steps after a failure has occurred.
    .
    . RELATED TO: CR #299 (duplicated: #314)

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

            @step('{word:w} step fails')
            def step_fails(context, word):
                assert False, "XFAIL (in: %s step)" % word
            """
        And a file named "features/alice.feature" with:
            """
            Feature: Alice
              Scenario: Passing
                Given first step passes
                When second step passes
                Then third step passes

              Scenario: Fails in second step
                Given a step passes
                When second step fails
                Then another step passes

              @runner.continue_after_failed_step
              Scenario: Fails in first and third step
                Given first step fails
                When second step passes
                Then third step fails
            """


    Scenario: Runner continues after failed step in all scenarios
      Given a file named "features/environment.py" with:
          """
          from behave.model import Scenario

          def before_all(context):
              userdata = context.config.userdata
              continue_after_failed = userdata.getbool("runner.continue_after_failed_step", False)
              Scenario.continue_after_failed_step = continue_after_failed
          """
      And a file named "behave.ini" with:
          """
          [behave]
          show_timings = false

          [behave.userdata]
          runner.continue_after_failed_step = true
          """
      When I run "behave -f plain features/alice.feature"
      Then it should fail with:
          """
          Failing scenarios:
            features/alice.feature:7  Fails in second step
            features/alice.feature:13  Fails in first and third step

          0 features passed, 1 failed, 0 skipped
          1 scenario passed, 2 failed, 0 skipped
          6 steps passed, 3 failed, 0 skipped, 0 undefined
          """
      And the command output should contain:
          """
          Scenario: Fails in second step
              Given a step passes ... passed
              When second step fails ... failed
                Assertion Failed: XFAIL (in: second step)
              Then another step passes ... passed

          Scenario: Fails in first and third step
            Given first step fails ... failed
              Assertion Failed: XFAIL (in: first step)
            When second step passes ... passed
            Then third step fails ... failed
              Assertion Failed: XFAIL (in: third step)
          """
      But note that "step execution continues after failed step(s)"
      And note that "no steps are skipped"


    Scenario: Runner continues after failed step in some scenarios

      Enable this feature only on tagged scenarios (or features).

      Given a file named "features/environment.py" with:
          """
          def before_scenario(context, scenario):
              if "runner.continue_after_failed_step" in scenario.effective_tags:
                  scenario.continue_after_failed_step = True
          """
      When I run "behave -f plain -T features/alice.feature"
      Then it should fail with:
          """
          Failing scenarios:
            features/alice.feature:7  Fails in second step
            features/alice.feature:13  Fails in first and third step

          0 features passed, 1 failed, 0 skipped
          1 scenario passed, 2 failed, 0 skipped
          5 steps passed, 3 failed, 1 skipped, 0 undefined
          """
      And the command output should contain:
          """
          Scenario: Fails in second step
            Given a step passes ... passed
            When second step fails ... failed
              Assertion Failed: XFAIL (in: second step)

          Scenario: Fails in first and third step
            Given first step fails ... failed
              Assertion Failed: XFAIL (in: first step)
            When second step passes ... passed
            Then third step fails ... failed
              Assertion Failed: XFAIL (in: third step)
          """
      But note that "step execution continues after failed step in tagged scenario only"
      And note that "some steps are skipped (in 2nd, untagged scenario)"

