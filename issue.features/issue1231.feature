@issue
Feature: Issue #1231 -- TypeConverter Error causes Error in pretty Formatter

  . DESCRIPTION:
  . If a type-converter raises an exception,
  . the "pretty" formatter runs into a problem (same for: "json").
  .
  . SEE ALSO:
  .   * https://github.com/behave/behave/issues/1231

  Background:
    Given a new working directory
    And a file named "features/steps/syndrome_steps.py" with:
      """
      from behave import when, register_type

      def parse_bad_type(text):
          raise Exception("OOPS")

      register_type(T=parse_bad_type)

      @when(u'something happens with param={x:T}')
      def when_something_happens(context, x):
          pass
      """
    And a file named "features/syndrome_1231.feature" with:
      """
      Feature: Syndrome
        Scenario: TypeConverter raises Error
          When something happens with param=SOME_VALUE
      """

  @format.plain
  Scenario: TypeConverter Error with "plain" formatter (NORMAL CASE)
    When I run "behave -f plain features/syndrome_1231.feature"
    Then it should fail with:
      """
      0 scenarios passed, 0 failed, 1 error, 0 skipped
      0 steps passed, 0 failed, 1 error, 0 skipped
      """
    And the command output should contain:
      """
      File "features/steps/syndrome_steps.py", line 4, in parse_bad_type
        raise Exception("OOPS")
      Exception: OOPS
      """
    And the command output should contain:
      """
      behave.matchers.StepParseError: OOPS
      """

  @format.<Formatter>
  Scenario Outline: Check Formatter "<Formatter>"
    When I run "behave -f <Formatter> features/syndrome_1231.feature"
    Then it should fail with:
      """
      0 scenarios passed, 0 failed, 1 error, 0 skipped
      0 steps passed, 0 failed, 1 error, 0 skipped
      """
    And the command output should not contain:
      """
      TypeError: 'NoneType' object is not iterable
      """
    And the command output should contain:
      """
      Errored scenarios:
        features/syndrome_1231.feature:2  TypeConverter raises Error
      """

    Examples:
      | Formatter |
      | json |
      | plain |
      | pretty |
      | progress |
      | progress2 |
      | progress3 |
      | steps |
      | tags |
