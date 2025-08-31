@use.with_python.min_version=3.8
Feature: Use nested step modules in the steps directory

  As a developer
  I want to organize my steps in subdirectories below the steps directory
  So that it feels better structured for me.

  . BEST PRACTICE: Do not use this functionality
  .  * Use step-libraries instead
  .  * Put Python packages on the Python search path (PYTHONPATH),
  .    but not in the steps directory (see below).
  .
  . SPECIFICATION:
  .   * This feature is disabled by default (reason: has caused too many problems).
  .   * You can enable it by putting "use_nested_step_modules = true" in the config-file
  .   * You can provide step-implementations as Python module in a subdirectory below the steps directory
  .
  . PROBLEMS WITH THIS APPROACH:
  .   * Some people put Python packages in the steps directory
  .   * A Python package may use relative-imports, like "from .other import foo"
  .   * Relative-imports cause exceptions if this feature is used (see below).
  .
  . NOTES:
  .   Identically named folders and modules in nested directories are all discovered.

  Background:
    Given a new working directory
    And a file named "behave.ini" with:
        """
        [behave]
        use_nested_step_modules = true
        """
    And a file named "features/steps/alice_steps.py" with:
        """
        from behave import given

        @given('I meet "{person_name:w}"')
        def step_impl(ctx, person_name: str):
            ctx.person_name = person_name

        @given('I meet "{person_name:w} at the {location:w}"')
        def step_impl(ctx, person_name: str, location: str):
            ctx.person_name = person_name
            ctx.location = location
        """
    And a file named "features/steps/nested/bob_steps.py" with:
        """
        from behave import given, when, then
        from assertpy import assert_that

        class DinnerReservation:
            def __init__(self, person_name: str):
                self.name = person_name

        @when('I invite "{person_name:w}" for dinner')
        def step_impl(ctx, person_name: str):
            ctx.person_name = person_name
            ctx.dinner_reservation = DinnerReservation(person_name)

        @then('a dinner reservation for "{person_name:w}" and me was made')
        def step_impl(ctx, person_name: str):
            assert_that(ctx.dinner_reservation.name).is_equal_to(ctx.person_name)
        """
    And a file named "features/f1.feature" with:
        """
        Feature: f1
          Scenario: S1
            Given I meet "Alice"
            When I invite "Alice" for dinner
            Then a dinner reservation for "Alice" and me was made
        """

  Rule: Steps directory contains Python package w/o relative-imports

    Scenario: Use nested step-module in package that uses no relative-imports
      Given an empty file named "features/steps/good_package/__init__.py"
        And a file named "features/steps/good_package/other.py" with:
          """
          def hello(name, greeting="Hello"):
              return "{greeting} {name}".format(greeting=greeting, name=name)
          """
        And a file named "features/steps/good_package/use_nonrelative_import.py" with:
          """
          from good_package.other import hello
          """
        When I run "behave -f pretty features/f1.feature"
        Then it should pass with:
          """
          1 feature passed, 0 failed, 0 skipped
          1 scenario passed, 0 failed, 0 skipped
          3 steps passed, 0 failed, 0 skipped
          """
        And the command output should contain:
          """
          Scenario: S1                                            # features/f1.feature:2
            Given I meet "Alice"                                  # features/steps/alice_steps.py:3
            When I invite "Alice" for dinner                      # features/steps/nested/bob_steps.py:8
            Then a dinner reservation for "Alice" and me was made # features/steps/nested/bob_steps.py:13
          """
        But the command output should not contain "Traceback"

    Scenario: Use two nested step-modules w/ same basename in two subdirectories on same level
       Given a file named "features/steps/subdir_1/nested_steps.py" with:
          """
          from behave import step

          @step('{word:w} step passes')
          def step_passes(ctx):
              pass
          """
       And a file named "features/steps/subdir_2/nested_steps.py" with:
          """
          from behave import step

          @step('{word:w} step fails')
          def step_fails(ctx):
              assert False, "XFAIL: Here"
          """
        When I run "behave -f steps features/f1.feature"
        Then it should pass with:
          """
          1 feature passed, 0 failed, 0 skipped
          1 scenario passed, 0 failed, 0 skipped
          3 steps passed, 0 failed, 0 skipped
          """
        And the command output should contain:
          """
          GIVEN STEP DEFINITIONS[4]:
            Given I meet "{person_name:w}"                      # features/steps/alice_steps.py:3
            Given I meet "{person_name:w} at the {location:w}"  # features/steps/alice_steps.py:7
            Given {word:w} step passes                          # features/steps/subdir_1/nested_steps.py:3
            Given {word:w} step fails                           # features/steps/subdir_2/nested_steps.py:3

          WHEN STEP DEFINITIONS[3]:
            When I invite "{person_name:w}" for dinner  # features/steps/nested/bob_steps.py:8
            When {word:w} step passes                   # features/steps/subdir_1/nested_steps.py:3
            When {word:w} step fails                    # features/steps/subdir_2/nested_steps.py:3

          THEN STEP DEFINITIONS[3]:
            Then a dinner reservation for "{person_name:w}" and me was made  # features/steps/nested/bob_steps.py:13
            Then {word:w} step passes                                        # features/steps/subdir_1/nested_steps.py:3
            Then {word:w} step fails                                         # features/steps/subdir_2/nested_steps.py:3

          GENERIC STEP DEFINITIONS[2]:
            * {word:w} step passes                    # features/steps/subdir_1/nested_steps.py:3
            * {word:w} step fails                     # features/steps/subdir_2/nested_steps.py:3
          """

    Scenario: Use two nested step-modules w/ same basename in two subdirectories levels (case: subdir-tree)

      Note that the second "nested_steps.py" is just inside a subdirectory tree.

      Given a file named "features/steps/subdir_1/nested_steps.py" with:
          """
          from behave import step

          @step('{word:w} step passes')
          def step_passes(ctx):
              pass
          """
       And a file named "features/steps/subdir_3/subdir_31/nested_steps.py" with:
          """
          from behave import step

          @step('{word:w} step fails')
          def step_fails(ctx):
              assert False, "XFAIL: Here"
          """
        When I run "behave -f steps features/f1.feature"
        Then it should pass with:
          """
          1 feature passed, 0 failed, 0 skipped
          1 scenario passed, 0 failed, 0 skipped
          3 steps passed, 0 failed, 0 skipped
          """
        And the command output should contain:
          """
          GIVEN STEP DEFINITIONS[4]:
            Given I meet "{person_name:w}"                      # features/steps/alice_steps.py:3
            Given I meet "{person_name:w} at the {location:w}"  # features/steps/alice_steps.py:7
            Given {word:w} step passes                          # features/steps/subdir_1/nested_steps.py:3
            Given {word:w} step fails                           # features/steps/subdir_3/subdir_31/nested_steps.py:3

          WHEN STEP DEFINITIONS[3]:
            When I invite "{person_name:w}" for dinner  # features/steps/nested/bob_steps.py:8
            When {word:w} step passes                   # features/steps/subdir_1/nested_steps.py:3
            When {word:w} step fails                    # features/steps/subdir_3/subdir_31/nested_steps.py:3

          THEN STEP DEFINITIONS[3]:
            Then a dinner reservation for "{person_name:w}" and me was made  # features/steps/nested/bob_steps.py:13
            Then {word:w} step passes                                        # features/steps/subdir_1/nested_steps.py:3
            Then {word:w} step fails                                         # features/steps/subdir_3/subdir_31/nested_steps.py:3

          GENERIC STEP DEFINITIONS[2]:
            * {word:w} step passes                    # features/steps/subdir_1/nested_steps.py:3
            * {word:w} step fails                     # features/steps/subdir_3/subdir_31/nested_steps.py:3
          """

    Scenario: Use two nested step-modules w/ same basename in two subdirectories levels (case: package)

      Note that the second "nested_steps.py" is part of a Python package.

      Given a file named "features/steps/subdir_1/nested_steps.py" with:
          """
          from behave import step

          @step('{word:w} step passes')
          def step_passes(ctx):
              pass
          """
       And an empty file named "features/steps/subdir_4/__init__.py"
       And an empty file named "features/steps/subdir_4/subdir_41/__init__.py"
       And a file named "features/steps/subdir_4/subdir_41/nested_steps.py" with:
          """
          from behave import step

          @step('{word:w} step fails')
          def step_fails(ctx):
              assert False, "XFAIL: Here"
          """
        When I run "behave -f steps features/f1.feature"
        Then it should pass with:
          """
          1 feature passed, 0 failed, 0 skipped
          1 scenario passed, 0 failed, 0 skipped
          3 steps passed, 0 failed, 0 skipped
          """
        And the command output should contain:
          """
          GIVEN STEP DEFINITIONS[4]:
            Given I meet "{person_name:w}"                      # features/steps/alice_steps.py:3
            Given I meet "{person_name:w} at the {location:w}"  # features/steps/alice_steps.py:7
            Given {word:w} step passes                          # features/steps/subdir_1/nested_steps.py:3
            Given {word:w} step fails                           # features/steps/subdir_4/subdir_41/nested_steps.py:3

          WHEN STEP DEFINITIONS[3]:
            When I invite "{person_name:w}" for dinner  # features/steps/nested/bob_steps.py:8
            When {word:w} step passes                   # features/steps/subdir_1/nested_steps.py:3
            When {word:w} step fails                    # features/steps/subdir_4/subdir_41/nested_steps.py:3

          THEN STEP DEFINITIONS[3]:
            Then a dinner reservation for "{person_name:w}" and me was made  # features/steps/nested/bob_steps.py:13
            Then {word:w} step passes                                        # features/steps/subdir_1/nested_steps.py:3
            Then {word:w} step fails                                         # features/steps/subdir_4/subdir_41/nested_steps.py:3

          GENERIC STEP DEFINITIONS[2]:
            * {word:w} step passes                    # features/steps/subdir_1/nested_steps.py:3
            * {word:w} step fails                     # features/steps/subdir_4/subdir_41/nested_steps.py:3
          """

  Rule: Steps directory contains Python package w/ relative-imports

    Note that Python packages w/ relative-imports cause problems
    if "use_nested_step_modules" is enabled.

    @use.with_python.implementation=pypy
    Scenario: Use nested step-module in package that uses relative-imports (case: pypy)
      Given an empty file named "features/steps/bad_package/__init__.py"
        And a file named "features/steps/bad_package/other.py" with:
          """
          def hello(name, greeting="Hello"):
              return "{greeting} {name}".format(greeting=greeting, name=name)
          """
        And a file named "features/steps/bad_package/use_relative_import.py" with:
          """
          from .other import hello
          """
        When I run "behave -f plain features/f1.feature"
        Then it should fail with:
          """
            File "features/steps/bad_package/use_relative_import.py", line 1, in <module>
              from .other import hello
          KeyError: '__name__'
          """
        But note that "the exception output differs in pypy"
        And the command output should contain "Traceback"

    @not.with_python.implementation=pypy
    Scenario: Use nested step-module in package that uses relative-imports (case: other)
      Given an empty file named "features/steps/bad_package/__init__.py"
        And a file named "features/steps/bad_package/other.py" with:
          """
          def hello(name, greeting="Hello"):
              return "{greeting} {name}".format(greeting=greeting, name=name)
          """
        And a file named "features/steps/bad_package/use_relative_import.py" with:
          """
          from .other import hello
          """
        When I run "behave -f plain features/f1.feature"
        Then it should fail with:
          """
            File "features/steps/bad_package/use_relative_import.py", line 1, in <module>
              from .other import hello
          KeyError: "'__name__' not in globals"
          """
        And the command output should contain "Traceback"
