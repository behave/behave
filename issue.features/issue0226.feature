@issue
@unicode
Feature: UnicodeDecodeError in tracebacks (when an exception in a step implementation)

  . Exception with non-ASCII character is raised in a step implementation.
  . UnicodeDecodeError occurs with:
  .   'ascii' codec can't decode byte 0x82 in position 11: ordinal not in range(128)
  .
  . RELATED:
  .   * features/i18n.unicode_problems.feature

  @setup
  Scenario: Feature Setup
    Given a new working directory
    And a file named "features/steps/steps.py" with:
      """
      # -*- coding: UTF-8 -*-
      from behave import step
      import six
      if six.PY2:
          chr = unichr

      @step(u'a step raises an exception with non-ASCII character "{char_code:d}"')
      def step_raises_exception_with_non_ascii_text(context, char_code):
          assert 0 <= char_code <= 255, "RANGE-ERROR: char_code=%s" % char_code
          raise RuntimeError(u"FAIL:"+ chr(char_code) +";")
      """

  Scenario Outline: Syndrome with non-ASCII char <char_code> (format=<format>)
    Given a file named "features/syndrome_0226_<char_code>.feature" with:
      """
      Feature:
        Scenario:
          Given a step raises an exception with non-ASCII character "<char_code>"
      """
    When I run "behave -f <format> features/syndrome_0226_<char_code>.feature"
    Then it should fail with:
      """
      0 scenarios passed, 1 failed, 0 skipped
      0 steps passed, 1 failed, 0 skipped, 0 undefined
      """
    And the command output should contain:
      """
      RuntimeError: FAIL:<special_char>;
      """
    But the command output should not contain "UnicodeDecodeError"

    Examples:
      | format | char_code | special_char | comment! |
      | plain  |    162    |  ¢           | cent     |
      | pretty |    191    |  ¿           | question-mark on-the-head |
