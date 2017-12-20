@issue
@unicode
Feature: Issue #424 -- Unicode output problem when fails in nested steps

    . HINTS:
    .   * Python step file should have encoding line (# -*- coding: ... -*-)
    .   * Assert failure message should use unicode-string instead of byte-string

    Scenario:
      Given a new working directory
      And a file named "features/steps/pass_steps.py" with:
        """
        from behave import step

        @step('{word:w} step passes')
        def step_passes(context, word):
            pass
        """
      And a file named "features/steps/steps.py" with:
        """
        # -*- coding: UTF-8 -*-
        # NOTE: Python2 requires encoding to decode special chars correctly.
        from behave import step

        @step('I press the big red button')
        def step_press_red_button(context):
            assert False, u"Ungültiger Wert"  # HINT: Special chars require Unicode.

        @step('I call the nested step with the "red button"')
        def step_press_red_button(context):
            context.execute_steps(u'When I press the big red button')
        """
      And a file named "behave.ini" with:
          """
          [behave]
          show_timings = false
          """
      And a file named "features/alice.feature" with:
        """
        Feature:

          Scenario: Use step directly
            When I press the big red button

          Scenario: Use nested step
            Given another step passes
            When I call the nested step with the "red button"
        """
      When I run "behave -f plain features/alice.feature"
      Then it should fail with:
        """
        0 scenarios passed, 2 failed, 0 skipped
        1 step passed, 2 failed, 0 skipped, 0 undefined
        """
      And the command output should contain:
        """
        Scenario: Use step directly
          When I press the big red button ... failed
        Assertion Failed: Ungültiger Wert

        Scenario: Use nested step
          Given another step passes ... passed
          When I call the nested step with the "red button" ... failed
        Assertion Failed: FAILED SUB-STEP: When I press the big red button
        Substep info: Assertion Failed: Ungültiger Wert
        """
