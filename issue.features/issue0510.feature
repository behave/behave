@issue
@junit
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
  . [XML-charsets] The normative reference is XML 1.0 (Fifth Edition),
  .     section 2.2, https://www.w3.org/TR/REC-xml/#charsets
  .
  .  Within a CDATA section, only the CDEnd string is recognized as markup,
  .  so that left angle brackets and ampersands may occur in their literal form;
  .  they need not (and cannot) be escaped using " &lt; " and " &amp; ".
  .  CDATA sections cannot nest.
  .
  .  CDSect	 ::=   	CDStart CData CDEnd
  .  CDStart ::=   	'<![CDATA['
  .  CData	 ::=   	(Char* - (Char* ']]>' Char*))
  .  CDEnd	 ::=   	']]>'
  .
  . [CDATA Sections] https://www.w3.org/TR/REC-xml/#sec-cdata-sect
  .


  @use.with_xmllint=yes
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

  @use.with_xmllint=yes
  Scenario:
    Given a new working directory
    And a file named "features/steps/cdata_end.py" with:
      """
      # -*- coding: UTF-8 -*-
      from __future__ import print_function
      from behave import step
      import logging

      @step(u'we print ]]>')
      def step_cdata_end(context):
          print(u"]]>")

      @step(u'we log ]]>')
      def step_log_cdata_end(context):
          logging.warning(u"]]>")
      """
    And a file named "features/cdata_end.feature" with:
      """
      Feature: A CDATA end
        Scenario: Print and log CDATA end
          When we print ]]>
          And we log ]]>
      """
    When I run "behave --junit features/cdata_end.feature"
    Then it should pass with:
      """
      1 scenario passed, 0 failed, 0 skipped
      """
    When I run "xmllint reports/TESTS-cdata_end.xml"
    Then it should pass
    And the command output should not contain "parser error"
    And the command output should not contain:
      """
      reports/TESTS-cdata_end.xml:6: parser error : Sequence ']]>' not allowed in content
      """
    And note that "xmllint reports additional correlated errors"
