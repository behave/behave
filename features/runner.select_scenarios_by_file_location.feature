@sequential
Feature: Select Scenarios by File Location

    To simplify running only one scenario in a feature (or some scenarios)
    As a tester
    I want to select a scenario by using its file location,
    like: "alice.feature:10"   (schema: {filename}:{line})


    | CONCEPT: File Location
    |   * A file location consists of file name and a positive line number
    |   * A file location is represented as "{filename}:{line}" (or "{filename}")
    |   * A file location with filename but without line number
    |     refers to the complete file
    |   * A file location with line number 0 (zero) refers to the complete file
    |
    | SPECIFICATION: Scenario selection by file locations
    |   * scenario.line == file_location.line selects scenario (preferred method).
    |   * Any line number in the following range is acceptable:
    |        scenario.line <= file_location.line < next_scenario.line
    |   * The first scenario is selected,
    |     if the file location line number is less than first scenario.line.
    |   * The last scenario is selected,
    |     if the file location line number is greater than the lines in the file.
    |
    | SPECIFICATION: Runner with scenario locations (file locations)
    |   * Adjacent file locations are merged if they refer to the same file, like:
    |
    |       alice.feature:10
    |       alice.feature:20
    |
    |       => MERGED: Selects/runs "alice.feature" with 2 scenarios.
    |
    |       alice.feature
    |       alice.feature:20
    |
    |       => MERGED: Selects "alice.feature" with all scenarios.
    |
    |       alice.feature:10
    |       bob.feature:20
    |       alice.feature:20
    |
    |       => NOT MERGED: Selects/runs "alice.feature" twice.
    |
    |   * If file locations (scenario locations) are used,
    |     scenarios with @setup or @teardown tags are selected, too.
    |
    |     REASON: Simplifies to use a Setup Scenario instead of a Background.
    |
    |   * Additional scenario selection mechanisms, like tags, names,
    |     are applied afterwards.


    @setup
    Scenario: Feature Setup
        Given a new working directory
        And a file named "features/steps/steps.py" with:
            """
            from behave import step

            @step('a step passes')
            def step_passes(context):
                pass
            """
        And a file named "features/alice.feature" with:
            """
            Feature: Alice

              Scenario: Alice First
                When a step passes

              Scenario: Alice Last
                Then a step passes
            """
        And a file named "features/bob.feature" with:
            """
            Feature: Bob

              @setup
              Scenario: Setup Bob
                Given a step passes

              Scenario: Bob in Berlin
                When a step passes

              Scenario: Bob in Paris
                Then a step passes

              @teardown
              Scenario: Teardown Bob
                Then a step passes
            """


    @file_location.select
    Scenario: Select one scenario with its exact file location

      CASE: scenario.line == file_location.line

        When I run "behave -f plain --dry-run --no-skipped features/alice.feature:3"
        Then it should pass with:
            """
            0 features passed, 0 failed, 0 skipped, 1 untested
            0 scenarios passed, 0 failed, 1 skipped, 1 untested
            """
        And the command output should contain:
            """
            Feature: Alice
              Scenario: Alice First
            """
        But the command output should not contain:
            """
            Scenario: Alice Last
            """

    @file_location.select
    Scenario: Select one scenario with a larger file location

      CASE: scenario.line <= file_location.line < next_scenario.line

        When I run "behave -f plain --dry-run --no-skipped features/alice.feature:4"
        Then it should pass with:
            """
            0 features passed, 0 failed, 0 skipped, 1 untested
            0 scenarios passed, 0 failed, 1 skipped, 1 untested
            """
        And the command output should contain:
            """
            Feature: Alice
              Scenario: Alice First
            """
        But the command output should not contain:
            """
            Scenario: Alice Last
            """

    @file_location.select
    Scenario: Select next scenario with its exact location

      CASE: scenario.line < file_location.line == next_scenario.line

        When I run "behave -f plain --dry-run --no-skipped features/alice.feature:6"
        Then it should pass with:
            """
            0 features passed, 0 failed, 0 skipped, 1 untested
            0 scenarios passed, 0 failed, 1 skipped, 1 untested
            """
        And the command output should contain:
            """
            Feature: Alice
              Scenario: Alice Last
            """
        But the command output should not contain:
            """
            Scenario: Alice First
            """

    @file_location.select_first
    Scenario: Select first scenario if line number is smaller than first scenario line

      CASE: 0 < file_location.line < first_scenario.line

        When I run "behave -f plain --dry-run --no-skipped features/alice.feature:1"
        Then it should pass with:
            """
            0 features passed, 0 failed, 0 skipped, 1 untested
            0 scenarios passed, 0 failed, 1 skipped, 1 untested
            """
        And the command output should contain:
            """
            Feature: Alice
              Scenario: Alice First
            """
        But the command output should not contain:
            """
            Scenario: Alice Last
            """

    @file_location.select_last
    Scenario: Select last scenario when line number is too large

      CASE: last_scenario.line < file.last_line < file_location.line

        When I run "behave -f plain --dry-run --no-skipped features/alice.feature:100"
        Then it should pass with:
            """
            0 features passed, 0 failed, 0 skipped, 1 untested
            0 scenarios passed, 0 failed, 1 skipped, 1 untested
            """
        And the command output should contain:
            """
            Feature: Alice
              Scenario: Alice Last
            """
        But the command output should not contain:
            """
            Scenario: Alice First
            """


    @file_location.select_all
    Scenario: Select all scenarios with line number 0 (zero)
        When I run "behave -f plain --dry-run --no-skipped features/alice.feature:0"
        Then it should pass with:
            """
            0 features passed, 0 failed, 0 skipped, 1 untested
            0 scenarios passed, 0 failed, 0 skipped, 2 untested
            """
        And the command output should contain:
            """
            Feature: Alice
              Scenario: Alice First
              Scenario: Alice Last
            """

    @file_location.select
    @with.feature_configfile
    Scenario: Select a scenario by using file locations from a features configfile
        Given a file named "alice1.txt" with:
            """
            # -- FEATURES CONFIGFILE:
            # Selects Alice First
            features/alice.feature:3
            """
        When I run "behave -f plain --dry-run --no-skipped @alice1.txt"
        Then it should pass with:
            """
            0 features passed, 0 failed, 0 skipped, 1 untested
            0 scenarios passed, 0 failed, 1 skipped, 1 untested
            """
        And the command output should contain:
            """
            Feature: Alice
              Scenario: Alice First
            """
        But the command output should not contain:
            """
            Scenario: Alice Last
            """

    @file_location.autoselect_setup_teardown
    Scenario: Auto-select scenarios tagged with @setup or @teardown if file location is used
        When I run "behave -f plain --dry-run --no-skipped features/bob.feature:7"
        Then it should pass with:
            """
            0 features passed, 0 failed, 0 skipped, 1 untested
            0 scenarios passed, 0 failed, 1 skipped, 3 untested
            """
        And the command output should contain:
            """
            Feature: Bob
              Scenario: Setup Bob
              Scenario: Bob in Berlin
              Scenario: Teardown Bob
            """
        But the command output should not contain:
            """
            Scenario: Bob in Paris
            """

    @merge.file_locations
    Scenario: Merge 2 adjacent file locations that refer to the same file
        When I run "behave -f plain --dry-run --no-skipped features/alice.feature:3 features/alice.feature:6"
        Then it should pass with:
            """
            0 features passed, 0 failed, 0 skipped, 1 untested
            0 scenarios passed, 0 failed, 0 skipped, 2 untested
            """
        And the command output should contain:
            """
            Feature: Alice
              Scenario: Alice First
              Scenario: Alice Last
            """
        But the command output should not contain:
            """
            Feature: Alice
              Scenario: Alice First

            Feature: Alice
              Scenario: Alice Last
            """

    @merge.file_locations
    @file_location.select_all
    Scenario: Merge filename and adjacent file location that refer to the same file
        When I run "behave -f plain --dry-run --no-skipped features/alice.feature:3 features/alice.feature"
        Then it should pass with:
            """
            0 features passed, 0 failed, 0 skipped, 1 untested
            0 scenarios passed, 0 failed, 0 skipped, 2 untested
            """
        And the command output should contain:
            """
            Feature: Alice
              Scenario: Alice First
              Scenario: Alice Last
            """
        But the command output should not contain:
            """
            Feature: Alice
              Scenario: Alice First

            Feature: Alice
              Scenario: Alice First
              Scenario: Alice Last
            """

    @merge.file_locations
    @with.feature_configfile
    Scenario: Merge 2 adjacent file locations to same file from features configfile
        Given a file named "alice1_and_alice2.txt" with:
            """
            # -- FEATURES CONFIGFILE:
            # Selects Alice First, Alice Last
            features/alice.feature:3
            features/alice.feature:6
            """
        When I run "behave -f plain --dry-run --no-skipped @alice1_and_alice2.txt"
        Then it should pass with:
            """
            0 features passed, 0 failed, 0 skipped, 1 untested
            0 scenarios passed, 0 failed, 0 skipped, 2 untested
            """
        And the command output should contain:
            """
            Feature: Alice
              Scenario: Alice First
              Scenario: Alice Last
            """
        But the command output should not contain:
            """
            Feature: Alice
              Scenario: Alice First

            Feature: Alice
              Scenario: Alice Last
            """

    @no_merge.file_locations
    @with.feature_configfile
    Scenario: No merge occurs if file locations to same file are not adjacent
        Given a file named "alice1_bob2_and_alice2.txt" with:
            """
            # -- FEATURES CONFIGFILE:
            # Selects Alice First, Bob in Paris (Setup, Teardown), Alice Last
            features/alice.feature:3
            features/bob.feature:10
            features/alice.feature:6
            """
        When I run "behave -f plain --dry-run --no-skipped @alice1_bob2_and_alice2.txt"
        Then it should pass with:
            """
            0 features passed, 0 failed, 0 skipped, 3 untested
            0 scenarios passed, 0 failed, 3 skipped, 5 untested
            """
        And the command output should contain:
            """
            Feature: Alice
              Scenario: Alice First

            Feature: Bob
              Scenario: Setup Bob
              Scenario: Bob in Paris
              Scenario: Teardown Bob

            Feature: Alice
              Scenario: Alice Last
            """
        But the command output should not contain:
            """
            Feature: Alice
              Scenario: Alice First
              Scenario: Alice Last
            """
