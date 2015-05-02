Feature: Exclude Scenario from Test Run

    As a test writer
    I want sometimes to decide at runtime
    that a scenario is excluded from a test run
    So that the command-line configuration becomes simpler
    (and auto-configuration is supported).

    . MECHANISM:
    .   The "before_scenario()" hook can decide just before a scenario should run
    .   that the scenario should be excluded from the test-run.
    .   NOTE: Hooks are not called in dry-run mode.
    .
    . RATIONALE:
    .   There are certain situations where it is better to skip a scenario
    .   than to run and fail the scenario.
    .
    .   Reasons for these cases are of often test environment related:
    .     * test environment does not fulfill the desired criteria
    .     * used testbed does not fulfill test requirements
    .
    .   Instead of providing the exclude-scenario selection on the command-line,
    .   the test (environment) and configuration logic should determine
    .   if a test should be excluded (as auto-configuration functionality).
    .
    . EXAMPLE:
    .   Certain scenarios should not run on Windows (or Linux, ...).
    .
    . EVALUATION ORDER:
    .   Before the user can exclude a scenario from a test-run,
    .   additional mechanisms decide, if the scenario is part of the selected run-set.
    .   These are:
    .     * tags
    .     * ...
    .
    . RELATED:
    .   * features/feature.exclude_from_run.feature


    @setup
    Scenario:
        Given a new working directory
        And a file named "features/example.feature" with:
            """
            Feature:

              Scenario: Alice
                 Given a step passes
                  When another step passes
                  Then some step passes

              Scenario: Bob and Alice
                 Given some step passes

              Scenario: Bob
                 Given another step passes
            """
        And a file named "features/steps/steps.py" with:
            """
            from behave import step

            @step('{word:w} step passes')
            def step_passes(context, word):
                pass

            @step('{word:w} step fails')
            def step_fails(context, word):
                assert False, "XFAIL-STEP"
            """

    @use_hook.before_scenario
    Scenario: Exclude a scenario from the test run (using: before_scenario() hook)
        Given a file named "features/environment.py" with:
            """
            import sys

            def should_exclude_scenario(context, scenario):
                if scenario.name.startswith("Alice"):
                    return True
                return False

            def before_scenario(context, scenario):
                if should_exclude_scenario(context, scenario):
                    sys.stdout.write("EXCLUDED-BY-USER: Scenario %s\n" % scenario.name)
                    scenario.skip()
            """
        When I run "behave -f plain -T features/example.feature"
        Then it should pass with:
            """
            2 scenarios passed, 0 failed, 1 skipped
            2 steps passed, 0 failed, 3 skipped, 0 undefined
            """
        And the command output should contain:
            """
            EXCLUDED-BY-USER: Scenario Alice
            """


    @use_hook.before_feature
    Scenario: Exclude a scenario from the test run (using: before_feature() hook)
        Given a file named "features/environment.py" with:
            """
            import sys

            def should_exclude_scenario(scenario):
                if "Alice" in scenario.name:  # MATCHES: Alice, Bob and Alice
                    return True
                return False

            def before_feature(context, feature):
                # -- NOTE: walk_scenarios() flattens ScenarioOutline.scenarios
                for scenario in feature.walk_scenarios():
                    if should_exclude_scenario(scenario):
                        sys.stdout.write("EXCLUDED-BEFORE-FEATURE: Scenario %s\n" % scenario.name)
                        scenario.skip()
            """
        When I run "behave -f plain -T features/example.feature"
        Then it should pass with:
            """
            1 scenario passed, 0 failed, 2 skipped
            1 step passed, 0 failed, 4 skipped, 0 undefined
            """
        And the command output should contain:
            """
            EXCLUDED-BEFORE-FEATURE: Scenario Alice
            EXCLUDED-BEFORE-FEATURE: Scenario Bob and Alice
            """


    Scenario: Skip scenario in a step

      Expect that remaining steps of the scenario are skipped.
      The skipping step is also marked as skipped
      to better detect scenarios that are partly executed and then skipped
      (otherwise a passed step would hide that the remaining steps are skipped).

        Given a file named "features/skip_scenario.feature" with:
            """
            Feature:

              Scenario: Alice2
                 Given a step passes
                 And the assumption "location:Wonderland" is not met
                 When another step passes
                 Then some step passes

              Scenario: Bob and Alice2
                 Given some step passes
                 When I skip the remaining scenario
                 Then another step passes
            """
        And a file named "features/steps/skip_scenario_steps.py" with:
            """
            from behave import given, step

            @given('the assumption "{name}" is not met')
            def step_assumption_not_met(context, name):
                context.scenario.skip("Assumption %s not met" % name)

            @step('I skip the remaining scenario')
            def step_skip_scenario(context):
                context.scenario.skip()
            """
        And a file named "features/environment.py" with:
            """
            # -- OVERRIDE WITH EMPTY-ENVIRONMENT.
            """
        When I run "behave -f plain -T features/skip_scenario.feature"
        Then it should pass with:
            """
            0 scenarios passed, 0 failed, 2 skipped
            2 steps passed, 0 failed, 5 skipped, 0 undefined
            """
        And the command output should contain:
            """
            Scenario: Alice2
              Given a step passes ... passed
              And the assumption "location:Wonderland" is not met ... skipped

            Scenario: Bob and Alice2
              Given some step passes ... passed
              When I skip the remaining scenario ... skipped
            """
        But note that "the step that skipped the scenario is also marked as skipped"


    Scenario: Skip scenario in after_scenario hook

      Expect that scenario is not marked as skipped
      because it was already executed (with status: passed, failed, ...).

        Given a file named "features/pass_and_fail.feature" with:
            """
            Feature:

              Scenario: Passing
                 Given a step passes

              Scenario: Failing
                 Given some step passes
                 When a step fails
            """
        And a file named "features/environment.py" with:
            """
            def before_all(context):
                context.config.setup_logging()

            def after_scenario(context, scenario):
                scenario.skip("AFTER-SCENARIO")
            """
        When I run "behave -f plain -T features/pass_and_fail.feature"
        Then it should fail with:
            """
            1 scenario passed, 1 failed, 0 skipped
            2 steps passed, 1 failed, 0 skipped, 0 undefined
            """
        But note that "the scenarios are not marked as skipped (SKIP-TOO-LATE)"
