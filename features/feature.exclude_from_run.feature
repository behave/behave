Feature: Exclude Feature from Test Run

    As a test writer
    I want sometimes to decide at runtime
    that a feature is excluded from a test run
    So that the command-line configuration becomes simpler
    (and auto-configuration is supported).

    . MECHANISM:
    .   The "before_feature()" hook can decide just before a feature should run
    .   that the feature should be excluded from the test-run.
    .   NOTE: Hooks are not called in dry-run mode.
    .
    . RATIONALE:
    .   There are certain situations where it is better to skip a feature
    .   than to run and fail the feature.
    .
    .   Reasons for these cases are of often test environment related:
    .     * test environment does not fulfill the desired criteria
    .     * used testbed does not fulfill test requirements
    .
    .   Instead of providing the exclude-feature selection on the command-line,
    .   the test (environment) and configuration logic should determine
    .   if a test should be excluded (as auto-configuration functionality).
    .
    . EXAMPLE:
    .   Certain features should not run on Windows (or Linux, ...).
    .
    . EVALUATION ORDER:
    .   Before the user can exclude a feature from a test-run,
    .   additional mechanisms decide, if the feature is part of the selected run-set.
    .   These are:
    .     * tags
    .     * ...
    .
    . RELATED:
    .   * features/scenario.exclude_from_run.feature


    @setup
    Scenario:
        Given a new working directory
        And a file named "features/alice.feature" with:
            """
            Feature: Alice
              Scenario: Alice in Wonderland
                 Given a step passes
                  When another step passes
                  Then some step passes

              Scenario: Alice and Bob
                 Given another step passes
            """
        And a file named "features/bob.feature" with:
            """
            Feature: Bob
              Scenario: Bob in Berlin
                 Given some step passes
                 When another step passes
            """
        And a file named "features/steps/steps.py" with:
            """
            from behave import step

            @step('{word:w} step passes')
            def step_passes(context, word):
                pass
            """


    Scenario: Exclude a feature from the test run (using: before_feature() hook)
        Given a file named "features/environment.py" with:
            """
            import sys

            def should_exclude_feature(feature):
                if "Alice" in feature.name:
                    return True
                return False

            def before_feature(context, feature):
                if should_exclude_feature(feature):
                    sys.stdout.write("EXCLUDED-BY-USER: Feature %s\n" % feature.name)
                    feature.skip()
            """
        When I run "behave -f plain -T features/"
        Then it should pass with:
            """
            1 feature passed, 0 failed, 1 skipped
            1 scenario passed, 0 failed, 2 skipped
            2 steps passed, 0 failed, 4 skipped, 0 undefined
            """
        And the command output should contain:
            """
            EXCLUDED-BY-USER: Feature Alice
            """
