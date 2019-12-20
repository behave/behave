Feature: Parsing a Feature File without a Feature or with several Features


    @setup
    Scenario: Feature Setup
      Given a new working directory
      And an empty file named "features/steps/empty_steps.py"
      And a file named "features/steps/passing_steps.py" with:
        """
        from behave import step

        @step('a step passes')
        def step_passes(context):
            pass
        """

    @no_feature
    Scenario: Empty Feature File
      Given an empty file named "features/empty.feature"
      When I run "behave -f plain features/empty.feature"
      Then it should pass with:
          """
          0 features passed, 0 failed, 0 skipped
          0 scenarios passed, 0 failed, 0 skipped
          0 steps passed, 0 failed, 0 skipped, 0 undefined
          """


    @no_feature
    Scenario: Feature File without Feature, only with Comments
      Given a file named "features/only_comments.feature" with:
        """
        # COMMENT: Comment starts at begin of line.
            # INDENTED-COMMENT: Comment starts after some whitespace.
        """
      When I run "behave -f plain features/only_comments.feature"
      Then it should pass with:
        """
        0 features passed, 0 failed, 0 skipped
        0 scenarios passed, 0 failed, 0 skipped
        0 steps passed, 0 failed, 0 skipped, 0 undefined
        """


    @no_feature
    Scenario: Feature File without Feature, only with Empty Lines
      Given a file named "features/only_empty_lines.feature" with:
        """

        """
      When I run "behave -f plain features/only_empty_lines.feature"
      Then it should pass with:
        """
        0 features passed, 0 failed, 0 skipped
        0 scenarios passed, 0 failed, 0 skipped
        0 steps passed, 0 failed, 0 skipped, 0 undefined
        """


    @no_feature
    Scenario: Feature File without Feature, only with Tags
      Given a file named "features/only_tags.feature" with:
        """
        @weird
        @no_feature
        """
      When I run "behave -f plain features/only_tags.feature"
      Then it should pass with:
        """
        0 features passed, 0 failed, 0 skipped
        0 scenarios passed, 0 failed, 0 skipped
        0 steps passed, 0 failed, 0 skipped, 0 undefined
        """

    @no_feature
    @parser.with_parse_error
    Scenario: Feature File with Text
      Given a file named "features/only_text.feature" with:
        """
        This File: Contains only text without keywords.
        OOPS.
        """
      When I run "behave -f plain features/only_text.feature"
      Then it should fail with:
        """
        Failed to parse "{__WORKDIR__}/features/only_text.feature":
        Parser failure in state=init at line 1: "This File: Contains only text without keywords."
        REASON: No feature found.
        """


    @no_feature
    @parser.with_parse_error
    Scenario: Feature File with Scenario, but without Feature keyword
      Given a file named "features/naked_scenario_only.feature" with:
        """
          Scenario:
            Given a step passes
            When a step passes
            Then a step passes
        """
      When I run "behave -f plain features/naked_scenario_only.feature"
      Then it should fail with:
        """
        Failed to parse "{__WORKDIR__}/features/naked_scenario_only.feature":
        Parser failure in state=init at line 1: "Scenario:"
        REASON: Scenario may not occur before Feature.
        """


    @many_features
    @parser.with_parse_error
    Scenario: Feature file with 2 features

       NOTE: Gherkin parser supports only one feature per feature file.

          Given a file named "features/steps/passing_steps.py" with:
            """
            from behave import step

            @step('a step passes')
            def step_passes(context):
                pass
            """
          And a file named "features/two_features.feature" with:
            """
            Feature: F1
              Scenario: F1.1
                Given a step passes
                When a step passes
                Then a step passes

            Feature: F2
              Scenario: F2.1
                Given a step passes
                Then a step passes
            """
          When I run "behave -f plain features/two_features.feature"
          Then it should fail with:
            """
            Failed to parse "{__WORKDIR__}/features/two_features.feature":
            Parser failure in state=steps at line 7: "Feature: F2"
            REASON: Multiple features in one file are not supported.
            """
