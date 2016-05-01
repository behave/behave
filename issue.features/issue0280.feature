@issue
Feature: Issue #280: AmbiguousStep error with similar step definitions and use_step_matcher("re")

  . While using the RegexMatcher with steps that have the same step prefix
  . an AmbiguousStep exception occurs if the shorter step is registered first.
  .
  . EXAMPLE:
  . Two steps with definitions that have the same step prefix:
  .
  .   * I do something
  .   * I do something more
  .
  . cause an AmbiguousStep error to be thrown:
  .
  .   behave.step_registry.AmbiguousStep: @when('I do something more') has already
  .   been defined in existing step @when('I do something') at ...
  .
  . SOLUTION: Add regex begin-/end-markers around the step text( '^'+ step + '$')
  . NOTE: Only RegexMatcher is affected.

  @setup
  Scenario: Feature Setup
    Given a new working directory
    And   a file named "features/steps/calculator_steps1.py" with:
      """
      from behave import given, then
      from hamcrest import assert_that, equal_to

      class SimpleCalculator(object):
          def __init__(self):
              self.result = 0

          def add(self, value):
              self.result += value

      @given(u'a calculator')
      def step_impl(context):
          context.calculator = SimpleCalculator()

      @then(u'the calculator result is "{expected_result:d}"')
      def step_impl(context, expected_result):
          assert_that(context.calculator.result, equal_to(expected_result))
      """

  Scenario: Ensure RegexMatcher is not ordering sensitive
    Given a file named "features/syndrome_280_1.feature" with:
      """
      Feature:
        Scenario: Use both steps
          Given I do something
          When  I do something more
      """
    And   a file named "features/steps/simple_steps.py" with:
      """
      from behave import step, use_step_matcher
      use_step_matcher("re")

      # -- ORDERING SENSITIVE PART:
      @step(u'I do something')
      def step_impl(context):
          pass

      @step(u'I do something more')
      def step_impl(context):
          pass
      """
    When I run "behave -f plain features/syndrome_280_1.feature"
    Then it should pass with:
      """
      1 scenario passed, 0 failed, 0 skipped
      """
    But the command output should not contain "AmbiguousStep:"
    And the command output should not contain:
      """
      AmbiguousStep: @step('I do something more') has already been defined in
      existing step @step('I do something') at features/steps/simple_steps.py:5'
      """

  Scenario: Ensure correct step implementation is selected
    Given a file named "features/syndrome_280_2.feature" with:
      """
      Feature: Steps with same step prefix -- Use correct step implementation
        Scenario: Use shorter step
          Given a calculator
          When I add "2" to it
          And  I add "3" to it
          Then the calculator result is "5"

        Scenario: Use longer step
          Given a calculator
          When I add "2" to it twice
          And  I add "3" to it
          Then the calculator result is "7"
      """
    And   a file named "features/steps/calculator_steps2.py" with:
      """
      from behave import when, use_step_matcher
      use_step_matcher("re")

      # -- ORDERING SENSITIVE PART:
      @when(u'I add "(?P<value>\d+)" to it')
      def step_impl(context, value):
          number_value = int(value)
          context.calculator.add(number_value)

      @when(u'I add "(?P<value>\d+)" to it twice')
      def step_impl(context, value):
          number_value = int(value)
          context.calculator.add(number_value)
          context.calculator.add(number_value)
      """
    When I run "behave -f pretty --no-color features/syndrome_280_2.feature"
    Then it should pass with:
      """
      When I add "2" to it twice        # features/steps/calculator_steps2.py:10
      And I add "3" to it               # features/steps/calculator_steps2.py:5
      """
    But the command output should not contain "AmbiguousStep"
