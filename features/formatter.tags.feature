@sequential
Feature: Tags Formatter (Tag Counts)

    As a tester
    I want to obtain a quick overview which tags are used (and how often)
    So that I can better use tags on command-line

    NOTE: Primarily intended for dry-run mode.

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
            @one
            Feature: Alice

              @setup
              Scenario: Setup Feature
                Given a step passes

              @wip
              Scenario: A1 with tags: @wip (inherited: @one)
                Given a step passes

              @foo
              @wip
              Scenario: A2 with tags: @foo, @wip (inherited: @one)
                When a step passes

              @foo @bar
              Scenario: A3 with tags: @foo, @bar (inherited: @one)
                Then a step passes
            """
        And a file named "features/bob.feature" with:
            """
            @two
            Feature: Bob

              Scenario: B1 without tags (inherited: @two)
                Given a step passes

              @foo @one
              Scenario: B2 with tags: @foo, @one (inherited: @two)
                When a step passes
            """


    Scenario: Use Tags formatter to get an overview of used tags
        When I run "behave -f tags --dry-run features/"
        Then it should pass with:
            """
            0 features passed, 0 failed, 0 skipped, 2 untested
            0 scenarios passed, 0 failed, 0 skipped, 6 untested
            """
        And the command output should contain:
            """
            TAG COUNTS (alphabetically sorted):
              @bar      1    (used for scenario)
              @foo      3    (used for scenario)
              @one      2    (used for feature: 1, scenario: 1)
              @setup    1    (used for scenario)
              @two      1    (used for feature)
              @wip      2    (used for scenario)
            """
        But note that "tags inherited from its feature are (normally) not counted."


    Scenario: Use Tags formatter together with another formatter
        When I run "behave -f tags -f plain -T features/"
        Then it should pass with:
            """
            2 features passed, 0 failed, 0 skipped
            6 scenarios passed, 0 failed, 0 skipped
            """
        And the command output should contain:
            """
            Feature: Alice

              Scenario: Setup Feature
                Given a step passes ... passed

              Scenario: A1 with tags: @wip (inherited: @one)
                Given a step passes ... passed

              Scenario: A2 with tags: @foo, @wip (inherited: @one)
                When a step passes ... passed

              Scenario: A3 with tags: @foo, @bar (inherited: @one)
                Then a step passes ... passed

            Feature: Bob

              Scenario: B1 without tags (inherited: @two)
                Given a step passes ... passed

              Scenario: B2 with tags: @foo, @one (inherited: @two)
                When a step passes ... passed

            TAG COUNTS (alphabetically sorted):
              @bar      1    (used for scenario)
              @foo      3    (used for scenario)
              @one      2    (used for feature: 1, scenario: 1)
              @setup    1    (used for scenario)
              @two      1    (used for feature)
              @wip      2    (used for scenario)
            """

    Scenario: Use Tags formatter when tags are selected
        When I run "behave -f tags --tags=@setup,@wip features/"
        Then it should pass with:
            """
            1 feature passed, 0 failed, 1 skipped
            3 scenarios passed, 0 failed, 3 skipped
            """
        And the command output should contain:
            """
            TAG COUNTS (alphabetically sorted):
              @bar      1    (used for scenario)
              @foo      3    (used for scenario)
              @one      2    (used for feature: 1, scenario: 1)
              @setup    1    (used for scenario)
              @two      1    (used for feature)
              @wip      2    (used for scenario)
            """
        And note that "all tags are detected even from skipped features and scenarios"
