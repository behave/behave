Feature: Background

  As a test writer
  I want to run a number of steps in each scenario
  And I want to avoid duplicating these steps for each scenario
  So that I write these steps only once (DRY principle).

  | SPECIFICATION:
  |   * A feature can have an optional "Background" section
  |   * The Background must be specified before any Scenario/ScenarioOutline
  |   * The Background may occur at most once
  |   * The Background steps are executed in each Scenario/ScenarioOutline
  |   * The Background steps are executed before any Scenario steps
  |   * If a Background step fails then the is marked as scenario failed
  |   * If a Background fails in a scenario then other scenarios are still executed.
  |
  | RELATED:
  |   * parser.background.sad_cases.feature
  |
  | NOTE:
  |   Cucumber has a slightly different runtime behaviour.
  |   When a background step fails the first scenario is marked as failed.
  |   But the remaining scenarios are marked as skipped.
  |
  |   This can lead to problems when you have sporadic background step failures.
  |   For this reason, behave retries the background steps for each scenario.
  |   But this may lead to an increased test duration if a systematic failure
  |   occurs in the failing background step.
  |
  | SEE ALSO:
  |   * https://github.com/cucumber/cucumber/blob/master/features/docs/gherkin/background.feature

  @setup
  Scenario: Feature Setup
    Given a new working directory
    And a file named "features/steps/background_steps.py" with:
        """
        from behave import step

        @step('{word} background step passes')
        def step_background_step_passes(context, word):
            pass

        @step('{word} background step fails')
        def step_background_step_fails(context, word):
            assert False, "XFAIL: background step"

        @step('{word} background step fails sometimes')
        def step_background_step_fails_sometimes(context, word):
            should_fail = (context.scenarios_count % 2) == 0
            if should_fail:
                step_background_step_fails(context, word)
        """
    And a file named "features/steps/passing_steps.py" with:
        """
        from behave import step

        @step('{word} step passes')
        def step_passes(context, word):
            pass

        @step('{word} step fails')
        def step_fails(context, word):
            assert False, "XFAIL"
        """

  Scenario: Feature with a Background and Scenarios
    Given a file named "features/background_example1.feature" with:
        """
        Feature:
          Background:
            Given a background step passes
            And another background step passes

          Scenario: S1
            When a step passes

          Scenario: S2
            Then a step passes
            And another step passes
        """
    When I run "behave -f plain -T features/background_example1.feature"
    Then it should pass with:
        """
        2 scenarios passed, 0 failed, 0 skipped
        7 steps passed, 0 failed, 0 skipped, 0 undefined
        """
    And the command output should contain:
        """
        Feature:
          Background:

          Scenario: S1
            Given a background step passes ... passed
            And another background step passes ... passed
            When a step passes ... passed

          Scenario: S2
            Given a background step passes ... passed
            And another background step passes ... passed
            Then a step passes ... passed
            And another step passes ... passed
        """
    But note that "the Background steps are injected into each Scenario"
    And note that "the Background steps are executed before any Scenario steps"


  Scenario: Failing Background Step causes all Scenarios to fail
    Given a file named "features/background_fail_example.feature" with:
        """
        Feature:

          Background: B1
            Given a background step passes
            And a background step fails
            And another background step passes

          Scenario: S1
            When a step passes

          Scenario: S2
            Then a step passes
            And another step passes
        """
    When I run "behave -f plain -T features/background_fail_example.feature"
    Then it should fail with:
        """
        0 scenarios passed, 2 failed, 0 skipped
        2 steps passed, 2 failed, 5 skipped, 0 undefined
        """
    And the command output should contain:
        """
        Feature:
          Background: B1

          Scenario: S1
            Given a background step passes ... passed
            And a background step fails ... failed
        Assertion Failed: XFAIL: background step

          Scenario: S2
            Given a background step passes ... passed
            And a background step fails ... failed
        Assertion Failed: XFAIL: background step
        """
    And note that "the failing Background step causes all Scenarios to fail"


  Scenario: Failing Background Step does not prevent that other Scenarios are executed

    If a Background step fails sometimes
    it should be retried in the remaining Scenarios where it might pass.

    Given a file named "features/background_fails_sometimes_example.feature" with:
        """
        Feature:

          Background: B2
            Given a background step fails sometimes

          Scenario: S1
            Given a step passes

          Scenario: S2
            When another step passes

          Scenario: S3
            Then another step passes
        """
    And a file named "features/environment.py" with:
        """
        scenarios_count = 0

        def before_scenario(context, scenario):
            global scenarios_count
            context.scenarios_count = scenarios_count
            scenarios_count += 1
        """
    When I run "behave -f plain -T features/background_fails_sometimes_example.feature"
    Then it should fail with:
        """
        1 scenario passed, 2 failed, 0 skipped
        2 steps passed, 2 failed, 2 skipped, 0 undefined
        """
    And the command output should contain:
        """
        Feature:
            Background: B2

            Scenario: S1
              Given a background step fails sometimes ... failed
          Assertion Failed: XFAIL: background step

            Scenario: S2
              Given a background step fails sometimes ... passed
              When another step passes ... passed

            Scenario: S3
              Given a background step fails sometimes ... failed
          Assertion Failed: XFAIL: background step
        """


  Scenario: Feature with a Background and ScenarioOutlines
    Given a file named "features/background_outline_example.feature" with:
        """
        Feature:
          Background:
            Given a background step passes
            And another background step passes

          Scenario Outline: SO1
            When a step <outcome1>
            Then another step <outcome2>

            Examples:
              | outcome1 | outcome2 |
              | passes   | passes   |
              | passes   | passes   |

          Scenario Outline: SO2
            Given <word1> step passes
            Then <word2> step passes

            Examples:
              | word1   | word2   |
              | a       | a       |
              | a       | another |
              | another | a       |
        """
    When I run "behave -f plain -T features/background_outline_example.feature"
    Then it should pass with:
        """
        5 scenarios passed, 0 failed, 0 skipped
        20 steps passed, 0 failed, 0 skipped, 0 undefined
        """
    And the command output should contain:
        """
        Feature:
          Background:

          Scenario Outline: SO1
            Given a background step passes ... passed
            And another background step passes ... passed
            When a step passes ... passed
            Then another step passes ... passed

          Scenario Outline: SO1
            Given a background step passes ... passed
            And another background step passes ... passed
            When a step passes ... passed
            Then another step passes ... passed

          Scenario Outline: SO2
            Given a background step passes ... passed
            And another background step passes ... passed
            Given a step passes ... passed
            Then a step passes ... passed

          Scenario Outline: SO2
            Given a background step passes ... passed
            And another background step passes ... passed
            Given a step passes ... passed
            Then another step passes ... passed

          Scenario Outline: SO2
            Given a background step passes ... passed
            And another background step passes ... passed
            Given another step passes ... passed
            Then a step passes ... passed
        """
    But note that "the Background steps are injected into each ScenarioOutline"
    And note that "the Background steps are executed before any ScenarioOutline steps"


  Scenario: Failing Background Step causes all ScenarioOutlines to fail
    Given a file named "features/background_fail_outline_example.feature" with:
        """
        Feature:
          Background:
            Given a background step passes
            And a background step fails
            But another background step passes

          Scenario Outline: SO1
            When a step <outcome1>
            Then another step <outcome2>

            Examples:
              | outcome1 | outcome2 |
              | passes   | passes   |
              | passes   | fails    |
              | fails    | passes   |
              | fails    | fails    |

          Scenario Outline: SO2
              When <word1> step passes

            Examples:
              | word1   |
              | a       |
              | another |
        """
    When I run "behave -f plain -T features/background_fail_outline_example.feature"
    Then it should fail with:
        """
        0 scenarios passed, 6 failed, 0 skipped
        6 steps passed, 6 failed, 16 skipped, 0 undefined
        """
    And the command output should contain:
        """
        Feature:
          Background:

          Scenario Outline: SO1
            Given a background step passes ... passed
            And a background step fails ... failed
        Assertion Failed: XFAIL: background step

          Scenario Outline: SO1
            Given a background step passes ... passed
            And a background step fails ... failed
        Assertion Failed: XFAIL: background step

          Scenario Outline: SO1
            Given a background step passes ... passed
            And a background step fails ... failed
        Assertion Failed: XFAIL: background step

          Scenario Outline: SO1
            Given a background step passes ... passed
            And a background step fails ... failed
        Assertion Failed: XFAIL: background step

          Scenario Outline: SO2
            Given a background step passes ... passed
            And a background step fails ... failed
        Assertion Failed: XFAIL: background step

          Scenario Outline: SO2
            Given a background step passes ... passed
            And a background step fails ... failed
        Assertion Failed: XFAIL: background step
        """
    But note that "the failing Background step causes each ScenarioOutline to be marked as skipped"


  Scenario: Feature with Background after first Scenario should fail (SAD CASE)
    Given a file named "features/background_sad_example1.feature" with:
        """
        Feature:
          Scenario: S1
            When a step passes

          Background: B1
            Given a background step passes

          Scenario: S2
            Then a step passes
            And another step passes
        """
    When I run "behave -f plain -T features/background_sad_example1.feature"
    Then it should fail with:
        """
        Parser failure in state steps, at line 5: 'Background: B1'
        REASON: Background may not occur after Scenario/ScenarioOutline.
        """


  Scenario: Feature with two Backgrounds should fail (SAD CASE)
    Given a file named "features/background_sad_example2.feature" with:
        """
        Feature:
          Background: B1
            Given a background step passes

          Background: B2 (XFAIL)
            Given another background step passes

          Scenario: S1
            When a step passes

          Scenario: S2
            Then a step passes
            And another step passes
        """
    When I run "behave -f plain -T features/background_sad_example2.feature"
    Then it should fail with:
        """
        Parser failure in state steps, at line 5: 'Background: B2 (XFAIL)'
        REASON: Background should not be used here.
        """
