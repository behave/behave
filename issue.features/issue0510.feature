@issue
@junit
@wip
Feature: Issue #510 -- JUnit XML output is not well-formed (in some cases)

  . Special control characters in JUnit stdout/stderr sections
  . are directly written to CDATA XML sections.
  .
  . According to the XML charset specification only the following unicode
  . codepoints (characters) are allowed in a CDATA section:
  .
  .   Char ::=  #x9 | #xA | #xD | [#x20-#xD7FF] | [#xE000-#xFFFD] | [#x10000-#x10FFFF]
  .   /* any Unicode character, excluding the surrogate blocks, FFFE, and FFFF. */
  .
  . [XML-charsets] "The normative reference is XML 1.0 (Fifth Edition),
  .     section 2.2, https://www.w3.org/TR/REC-xml/#charsets


  @use.with_xmllint=yes
  @xfail
  Scenario:
    Given a new working directory
    And a file named "features/steps/special_char_steps.py" with:
      """
      # -*- coding: UTF-8 -*-
      from __future__ import print_function
      from behave import step

      @step(u'we print ^D')
      def step_print_special_char_control_d(context):
          print(u"\004")
      """
    And a file named "features/special_char.feature" with:
      """
      Feature: An illegal char
        Scenario: Control-D
          When we print ^D
      """
    When I run "behave --junit features/special_char.feature"
    Then it should pass with:
      """
      1 scenario passed, 0 failed, 0 skipped
      """
    When I run "xmllint reports/TESTS-special_char.xml"
    Then it should pass
    And the command output should not contain "parser error"
    And the command output should not contain:
      """
      reports/TESTS-special_char.xml:12: parser error : PCDATA invalid Char value 4
      """
    And note that "xmllint reports additional correlated errors"
