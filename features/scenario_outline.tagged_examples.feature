Feature: ScenarioOutline with tagged Examples

  As a tester
  I want to select (or exclude) a specific Examples table of a ScenarioOutline
  To run only the scenarios from the Examples table of interest.

  | SPECIFICATION:
  |   Scenarios from a Examples table inherit the tags from
  |   its ScenarioOutline tags and its Examples tags:
  |
  |       scenario.tags = scenario_outline.tags + examples.tags
  |
  |   Therefore, examples.tags can easily be used to select all scenarios
  |   of this Examples table.
  |
  |   NOTE: This allows to provide multiple Examples sections,
  |     one for each stage of testing and/or one for each test team
  |     (development testing, integration testing, system tests, ...).

  @setup
  Scenario: Feature Setup
    Given a new working directory
    And a file named "behave.ini" with:
      """
      [behave]
      show_timestamps = false
      show_skipped = false
      """
    And a file named "features/steps/steps.py" with:
      """
      from behave import step

      @step('{word:w} step passes')
      def step_passes(context, word):
          pass
      """
    And a file named "features/tagged_examples.feature" with:
      """
      Feature:

        @zap
        Scenario Outline:
          Given <variant> step passes

          @foo
          Examples: Alice
            | variant | Comment |
            | a       | First  case |
            | another | Second case |

          @bar
          Examples: Bob
            | variant | Comment |
            | weird   | First case |
      """
    And a file named "behave.ini" with:
        """
        [behave]
        show_skipped = false
        show_timings = false
        """

  Scenario: Use all Examples (and Scenarios)
    When I run "behave -f plain features/tagged_examples.feature"
    Then it should pass with:
      """
      1 feature passed, 0 failed, 0 skipped
      3 scenarios passed, 0 failed, 0 skipped
      """

  Scenario: Select all Examples (and Scenarios)
    When I run "behave -f plain --tags=@zap features/tagged_examples.feature"
    Then it should pass with:
      """
      1 feature passed, 0 failed, 0 skipped
      3 scenarios passed, 0 failed, 0 skipped
      """

  Scenario: Select only first Examples table
    When I run "behave -f plain --tags=@foo features/tagged_examples.feature"
    Then it should pass with:
      """
      1 feature passed, 0 failed, 0 skipped
      2 scenarios passed, 0 failed, 1 skipped
      """
    And the command output should contain:
      """
      Scenario Outline:  -- @1.1 Alice
        Given a step passes ... passed

      Scenario Outline:  -- @1.2 Alice
        Given another step passes ... passed
      """
    But the command output should not contain:
      """
      Scenario Outline:  -- @2.1 Bob
      """

  Scenario: Select only second Examples table
    When I run "behave -f plain --tags=@bar features/tagged_examples.feature"
    Then it should pass with:
      """
      1 feature passed, 0 failed, 0 skipped
      1 scenario passed, 0 failed, 2 skipped
      """
    And the command output should contain:
      """
      Scenario Outline:  -- @2.1 Bob
        Given weird step passes ... passed
      """
    But the command output should not contain:
      """
      Scenario Outline:  -- @1.1 Alice
        Given a step passes ... passed

      Scenario Outline:  -- @1.2 Alice
        Given another step passes ... passed
      """
