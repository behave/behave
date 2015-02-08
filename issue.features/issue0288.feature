@issue
@only.with_python2=true
Feature: Issue #288 -- print() needed in "environment.py" file or steps
  
  . QUICKFIX: Apply to your code base
  .   pip install modernize
  .   python-modernize --fix=libmodernize.fixes.fix_print my_directory/          # Shows only changes
  .   python-modernize --fix=libmodernize.fixes.fix_print --write my_directory/  # Applies changes
  .
  . NOTE: Currently, the feature describes the implemented behaviour of behave.

    Background: Feature Setup
        Given a new working directory
        And a file named "features/steps/steps.py" with:
            """
            from __future__ import unicode_literals
            from behave import step

            @step('{word:w} step passes')
            def step_passes(context, word):
                pass
            """
        And a file named "features/e1.feature" with:
            """
            Feature:
                Scenario: Alice
                    Given a step passes
                    Then another step passes

                Scenario: Bob
                    Given some step passes
            """


    Scenario: Environment File Example
        Given a file named "features/environment.py" with:
            """
            def before_all(context):
                print "HELLO @before_all"
            """
        When I run "behave -f plain features"
        Then it should fail with:
            """
            File "features/environment.py", line 2
                  print "HELLO @before_all"
                                          ^
              SyntaxError: invalid syntax
            """

    Scenario: Module imported from environment file is unaffected
        Given a file named "features/environment.py" with:
            """
            from __future__ import absolute_import, print_function
            from foo import hello

            def before_all(context):
                hello("@before_all")
            """
        And a file named "foo.py" with:
            """
            def hello(text):
                print "HELLO "+ text
            """
        When I run "behave -f plain features"
        Then it should pass with:
            """
            2 scenarios passed, 0 failed, 0 skipped
            3 steps passed, 0 failed, 0 skipped, 0 undefined
            """

    Scenario: Steps Example
        Given a file named "features/steps/print_steps.py" with:
            """
            from __future__ import unicode_literals
            from behave import step

            @step('I print "{text}"')
            def step_print(context, text):
                print "HELLO STEP "+ text
            """
        When I run "behave -f plain features"
        Then it should fail with:
            """
            File "features/steps/print_steps.py", line 6
                print "HELLO STEP "+ text
                                  ^
            SyntaxError: invalid syntax
            """

    Scenario: Step imports other module with print statement
        Given a file named "features/steps/print_steps2.py" with:
            """
            from __future__ import unicode_literals
            from behave import step
            from bar import hello

            @step('I print "{text}"')
            def step_print(context, text):
                hello(text)
            """
        And a file named "bar.py" with:
            """
            def hello(text):
                print "HELLO "+ text
            """
        And a file named "features/e2.feature" with:
            """
            Feature:
                Scenario: Charly
                    Given I print "Lorem ipsum"
            """
        When I run "behave -f plain --no-capture features/e2.feature"
        Then it should pass with:
            """
            1 scenario passed, 0 failed, 0 skipped
            1 step passed, 0 failed, 0 skipped, 0 undefined
            """
        And the command output should contain:
            """
            HELLO Lorem ipsum
            """
