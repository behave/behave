@issue
@unicode
Feature: Assert with non-ASCII char causes UnicodeDecodeError

  . Failing assert with non-ASCII character in its message
  . causes UnicodeDecodeError and silent exit in Python2.
  .
  . RELATED:
  .   * features/i18n.unicode_problems.feature

  @setup
  Scenario: Feature Setup
    Given a new working directory
    And a file named "features/steps/steps.py" with:
      """
      from behave import step

      @step(u'a step fails with non-ASCII character "{char_code:d}"')
      def step_fails_with_non_ascii_text(context, char_code):
          assert 0 <= char_code <= 255, "RANGE-ERROR: char_code=%s" % char_code
          assert False, "FAIL:"+ chr(char_code) +";"
      """

  Scenario Outline: Syndrome with non-ASCII char <char_code> (format=<format>)
    Given a file named "features/syndrome_0230_<char_code>.feature" with:
      """
      Feature:
        Scenario:
          Given a step fails with non-ASCII character "<char_code>"
      """
    When I run "behave -f <format> features/syndrome_0230_<char_code>.feature"
    Then it should fail with:
      """
      0 scenarios passed, 1 failed, 0 skipped
      0 steps passed, 1 failed, 0 skipped, 0 undefined
      """
    And the command output should not contain "UnicodeDecodeError"
    But the command output should contain:
      """
      Assertion Failed: FAIL:
      """

    Examples:
      | format | char_code |
      | plain  |    130    |
      | pretty |    190    |
