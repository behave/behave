@issue
@unicode
Feature: Issue #449 -- Unicode output problem when fails with Russion text

  . Either Exception text (as summary) or traceback python line shows
  . special characters correctly.

  Scenario:
    Given a new working directory
    And a file named "features/steps/problematic_steps.py" with:
      """
      # -*- coding: UTF-8 -*-
      # NOTE: Python2 requires encoding to decode special chars correctly.
      from behave import step
      from hamcrest.core import assert_that, equal_to

      @step("Russian text")
      def step_russian_text(stop):
          assert_that(False, equal_to(True), u"Всё очень плохо") # cyrillic
      """
    And a file named "behave.ini" with:
        """
        [behave]
        show_timings = false
        """
    And a file named "features/syndrome.feature" with:
      """
      Feature:
        Scenario:
          Given Russian text
      """
    When I run "behave -f plain features/syndrome.feature"
    Then it should fail with:
      """
      Scenario:
        Given Russian text ... failed
      Assertion Failed: Всё очень плохо
      """
    But the command output should not contain:
      """
      Assertion Failed: 'ascii' codec can't encode characters in position
      """
