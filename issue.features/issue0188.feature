@issue
Feature: Better diagnostics if nested step is undefined

  | Currently if nested step has no match, it's shown like this:
  |
  |     Assertion Failed: Sub-step failed: When I do strange thign
  |     Substep info: None
  |
  | Took some time to find that typo.
  | The suggestion is to fill substep error_message with at least "No match for step"
  | so it would become:
  |
  |     Assertion Failed: Sub-step failed: When I do strange thign
  |     Substep info: No match for step
  |
  | IMPLEMENTATION NOTE:
  | A slightly different output is provided:
  |
  |     Assertion Failed: UNDEFINED SUB-STEP: When I do strange thign

  Scenario:
    Given a new working directory
    And a file named "features/steps/steps.py" with:
      """
      from behave import step

      @step('{word:w} step passes')
      def step_passes(context, word):
          pass

      @then('a good diagnostic message is shown')
      def step_good_diagnostic_message_is_shown(context):
          pass

      @step('I execute nested steps with an undefined step')
      def step_passes(context):
          context.execute_steps(u'''
            Given another step passes
            When an undefined, nested step is executed
            Then third step passes
          ''')
      """
    And a file named "features/example.execute_nested_undefined_step.feature" with:
      """
      Feature:
        Scenario:
          Given a step passes
          When I execute nested steps with an undefined step
          Then a good diagnostic message is shown
      """
    When I run "behave -f plain -T features/example.execute_nested_undefined_step.feature"
    Then it should fail with:
      """
      Assertion Failed: UNDEFINED SUB-STEP: When an undefined, nested step is executed
      """

