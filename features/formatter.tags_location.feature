@sequential
Feature: TagsLocation Formatter

    As a tester
    I want to know where and in which context tags are used
    So that I better understand how to use tags in feature files and on command-line

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


    Scenario: Use TagsLocation formatter to get an overview where tags are used
        When I run "behave -f tags.location --dry-run features/"
        Then it should pass with:
          """
          0 features passed, 0 failed, 0 skipped, 2 untested
          0 scenarios passed, 0 failed, 0 skipped, 6 untested
          """
        And the command output should contain:
          """
          TAG LOCATIONS (alphabetically ordered):
            @bar:
              features/alice.feature:18   Scenario: A3 with tags: @foo, @bar (inherited: @one)

            @foo:
              features/alice.feature:14   Scenario: A2 with tags: @foo, @wip (inherited: @one)
              features/alice.feature:18   Scenario: A3 with tags: @foo, @bar (inherited: @one)
              features/bob.feature:8      Scenario: B2 with tags: @foo, @one (inherited: @two)

            @one:
              features/alice.feature:2    Feature: Alice
              features/bob.feature:8      Scenario: B2 with tags: @foo, @one (inherited: @two)

            @setup:
              features/alice.feature:5    Scenario: Setup Feature

            @two:
              features/bob.feature:2      Feature: Bob

            @wip:
              features/alice.feature:9    Scenario: A1 with tags: @wip (inherited: @one)
              features/alice.feature:14   Scenario: A2 with tags: @foo, @wip (inherited: @one)
          """
        But note that "tags inherited from its feature are (normally) not counted."


    Scenario: Use TagsLocation formatter together with another formatter
        When I run "behave -f tags.location -f plain -T features/"
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
          """
        And the command output should contain:
          """
          TAG LOCATIONS (alphabetically ordered):
            @bar:
              features/alice.feature:18   Scenario: A3 with tags: @foo, @bar (inherited: @one)

            @foo:
              features/alice.feature:14   Scenario: A2 with tags: @foo, @wip (inherited: @one)
              features/alice.feature:18   Scenario: A3 with tags: @foo, @bar (inherited: @one)
              features/bob.feature:8      Scenario: B2 with tags: @foo, @one (inherited: @two)

            @one:
              features/alice.feature:2    Feature: Alice
              features/bob.feature:8      Scenario: B2 with tags: @foo, @one (inherited: @two)

            @setup:
              features/alice.feature:5    Scenario: Setup Feature

            @two:
              features/bob.feature:2      Feature: Bob

            @wip:
              features/alice.feature:9    Scenario: A1 with tags: @wip (inherited: @one)
              features/alice.feature:14   Scenario: A2 with tags: @foo, @wip (inherited: @one)
          """


    Scenario: Use TagsLocation formatter when tags are selected
        When I run "behave -f tags.location --tags=@setup,@wip features/"
        Then it should pass with:
          """
          1 feature passed, 0 failed, 1 skipped
          3 scenarios passed, 0 failed, 3 skipped
          """
        And the command output should contain:
          """
          TAG LOCATIONS (alphabetically ordered):
            @bar:
              features/alice.feature:18   Scenario: A3 with tags: @foo, @bar (inherited: @one)

            @foo:
              features/alice.feature:14   Scenario: A2 with tags: @foo, @wip (inherited: @one)
              features/alice.feature:18   Scenario: A3 with tags: @foo, @bar (inherited: @one)
              features/bob.feature:8      Scenario: B2 with tags: @foo, @one (inherited: @two)

            @one:
              features/alice.feature:2    Feature: Alice
              features/bob.feature:8      Scenario: B2 with tags: @foo, @one (inherited: @two)

            @setup:
              features/alice.feature:5    Scenario: Setup Feature

            @two:
              features/bob.feature:2      Feature: Bob

            @wip:
              features/alice.feature:9    Scenario: A1 with tags: @wip (inherited: @one)
              features/alice.feature:14   Scenario: A2 with tags: @foo, @wip (inherited: @one)
          """
        And note that "all tags are detected even from skipped features and scenarios"
