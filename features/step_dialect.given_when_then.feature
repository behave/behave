Feature: Step Dialect for BDD Steps with Given/When/Then Keywords

  In order to execute a sequence of steps with BDD keywords (Given/When/Then)
  As a test/story writer
  I want to have the possibility to express myself.

  | NOTE:
  |   * More details are provided in other features.


  Scenario: Simple example

    Normally preferred style with BDD keywords.
    Note that BDD keywords are dependent on language settings.

      Given a step passes
      When a step passes
      And a step passes
      Then a step passes
      And a step passes
      But a step passes


  Scenario: Simple example (with lower-case keywords)

    Alternative style with lower-case BDD keywords.

      given a step passes
      when a step passes
      and a step passes
      then a step passes
      and a step passes
      but a step passes


  Scenario: Step usage example with details by running behave
    Given a new working directory
    And a file named "features/steps/steps.py" with:
        """
        from behave import given, when, then, step

        @given('a step passes')
        def given_step_passes(context):
            pass

        @when('a step passes')
        def when_step_passes(context):
            pass

        @then('a step passes')
        def then_step_passes(context):
            pass

        @step('a step passes with "{param}"')
        def step_passes_with_param(context, param):
            pass

        @step('another step passes')
        def step_passes(context):
            pass

        @step('another step passes with "{param}"')
        def step_passes(context, param):
            pass
        """
    And a file named "features/basic_steps.feature" with:
        """
        Feature:
          Scenario:
            Given a step passes
            And another step passes
            When a step passes with "Alice"
            Then another step passes with "Bob"
        """
    When I run "behave -f plain -T features/basic_steps.feature"
    Then it should pass with:
        """
        1 scenario passed, 0 failed, 0 skipped
        4 steps passed, 0 failed, 0 skipped
        """
    And the command output should contain:
        """
        Feature:
          Scenario:
            Given a step passes ... passed
            And another step passes ... passed
            When a step passes with "Alice" ... passed
            Then another step passes with "Bob" ... passed
        """