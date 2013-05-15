# -- BASED-ON: cucumber/features/nested_steps.feature
# PROBLEM: stdout capture is shown only when a step fails.
Feature: Nested Steps


  Background:
    Given a new working directory
    And a file named "features/steps/step_turtle.py" with:
        """
        from __future__ import print_function
        from behave import given
        import sys

        @given(u'a turtle')
        def step(context):
            print("turtle!")
            sys.stdout.write("TURTLE!")
        """
    And   a file named "features/f.feature" with:
      """
      Feature: Call Nested Steps
        Scenario: Example
          Given two turtles
      """

  Scenario: Use #steps to call several steps at once
    Given a file named "features/steps/steps.py" with:
        """#!python
        from __future__ import print_function
        from behave import given

        @given(u'two turtles')
        def step(context):
            context.execute_steps(u'''
                Given a turtle
                And   a turtle
            ''')
        """
    When I run "behave -c -f plain"
    Then it should pass with:
      """
      1 feature passed, 0 failed, 0 skipped
      1 scenario passed, 0 failed, 0 skipped
      1 step passed, 0 failed, 0 skipped, 0 undefined
      """