Feature: Exclude Scenario from Test Run

    As a test writer
    I want sometimes to decide at runtime
    that a scenario is excluded from a test run
    So that the command-line configuration becomes simpler
    (and auto-configuration is supported).

    | MECHANISM:
    |   The "before_scenario()" hook can decide just before a scenario should run
    |   that the scenario should be excluded from the test-run.
    |   NOTE: Hooks are not called in dry-run mode.
    |
    | RATIONALE:
    |   There are certain situations where it is better to skip a scenario
    |   than to run and fail the scenario.
    |
    |   Reasons for these cases are of often test environment related:
    |     * test environment does not fulfill the desired criteria
    |     * used testbed does not fulfill test requirements
    |
    |   Instead of providing the exclude-scenario selection on the command-line,
    |   the test (environment) and configuration logic should determine
    |   if a test should be excluded (as auto-configuration functionality).
    |
    | EXAMPLE:
    |   Certain scenarios should not run on Windows (or Linux, ...).
    |
    | EVALUATION ORDER:
    |   Before the user can exclude a scenario from a test-run,
    |   additional mechanisms decide, if the scenario is part of the selected run-set.
    |   These are:
    |     * tags
    |     * ...
    |
    | RELATED:
    |   * features/feature.exclude_from_run.feature


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
                    scenario.mark_skipped()
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
                        scenario.mark_skipped()
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
