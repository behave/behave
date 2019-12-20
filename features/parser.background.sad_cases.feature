Feature: Ensure that BAD/SAD Use cases of Background are detected

  To improve diagnostics when parser failures occur
  As a test writer
  I expect reasonable explanations what went wrong.

    @setup
    Scenario: Feature Setup
      Given a new working directory
      And a file named "features/steps/passing_steps.py" with
        """
        from behave import step

        @step('a step passes')
        def step_passes(context):
            pass

        @step('a step passes with "{text}"')
        def step_passes(context, text):
            pass
        """


    Scenario: Background with tags is not supported
      Given a file named "features/syndrome.background_with_tags.feature" with
        """
        Feature: Ensure this fails

          @tags_are @not_supported @here
          Background: Oops...
            Given a step passes

          Scenario: More...
            Given a step passes
        """
      When I run "behave -f plain -T features/syndrome.background_with_tags.feature"
      Then it should fail with
        """
        Failed to parse "{__WORKDIR__}/features/syndrome.background_with_tags.feature":
        Parser failure in state=taggable_statement at line 4: "Background: Oops..."
        REASON: Background does not support tags.
        """


    Scenario: Background should not occur after a Scenario
      Given a file named "features/syndrome.background_after_scenario.feature" with
        """
        Feature: Ensure this fails1

          Scenario: One...
            Given a step passes

          Background: Oops, too late (after Scenario)
            When a step passes
        """
      When I run "behave -f plain -T features/syndrome.background_after_scenario.feature"
      Then it should fail with
        """
        Failed to parse "{__WORKDIR__}/features/syndrome.background_after_scenario.feature":
        Parser failure in state=steps at line 6: "Background: Oops, too late (after Scenario)"
        REASON: Background may not occur after Scenario/ScenarioOutline.
        """


    Scenario: Tagged Background should not occur after a Scenario
      Given a file named "features/syndrome.tagged_background_after_scenario.feature" with
        """
        Feature: Ensure this fails1

          Scenario: One...
            Given a step passes

          @tags_are @not_supported @here
          Background: Oops, too late (after Scenario)
            When a step passes
        """
      When I run "behave -f plain -T features/syndrome.tagged_background_after_scenario.feature"
      Then it should fail with
        """
        Parser failure in state=taggable_statement at line 7: "Background: Oops, too late (after Scenario)"
        REASON: Background may not occur after Scenario/ScenarioOutline.
        """


    Scenario: Background should not occur after a Scenario Outline
      Given a file named "features/syndrome.background_after_scenario_outline.feature" with
        """
        Feature: Ensure this fails3

          Scenario Outline: Two...
            Given a step passes with "<name>"

            Examples:
              | name  |
              | Alice |

          Background: Oops, too late (after Scenario Outline)
            When a step passes
        """
      When I run "behave -f plain -T features/syndrome.background_after_scenario_outline.feature"
      Then it should fail with
        """
        Parser failure in state=steps at line 10: "Background: Oops, too late (after Scenario Outline)"
        REASON: Background may not occur after Scenario/ScenarioOutline.
        """


    Scenario: Tagged Background should not occur after a Scenario Outline
      Given a file named "features/syndrome.background_after_scenario_outline.feature" with
        """
        Feature: Ensure this fails4

          Scenario Outline: Two...
            Given a step passes with "<name>"

            Examples:
              | name  |
              | Alice |

          @tags_are @not_supported @here
          Background: Oops, too late (after Scenario Outline)
            When a step passes
        """
      When I run "behave -f plain -T features/syndrome.background_after_scenario_outline.feature"
      Then it should fail with
        """
        Parser failure in state=taggable_statement at line 11: "Background: Oops, too late (after Scenario Outline)"
        REASON: Background may not occur after Scenario/ScenarioOutline.
        """
