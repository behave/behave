Feature: Parsing a File without a Feature


    @setup
    Scenario: Test Setup
      Given a new working directory
      And   an empty file named "features/steps/empty_steps.py"


    Scenario: Empty Feature File
      Given an empty file named "features/empty.feature"
      When I run "behave -f plain features/empty.feature"
      Then it should pass with:
          """
          0 features passed, 0 failed, 0 skipped
          0 scenarios passed, 0 failed, 0 skipped
          0 steps passed, 0 failed, 0 skipped, 0 undefined
          """


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
        Failed to parse "{__WORKDIR__}/features/only_text.feature": Parser failure in state init
        """

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
        Failed to parse "{__WORKDIR__}/features/naked_scenario_only.feature": Parser failure in state init
        """
