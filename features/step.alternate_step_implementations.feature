Feature: Alternate step implementations

  As I tester and test writer
  I want to run the same feature with different step implementations in different environments
  So I can run quick checks in a development environment and detailed checks in a testlab.

    | Example directory layout:
    |
    |   .../features/
    |       +-- example.feature
    |       +-- steps/
    |       |   +-- example.py
    |       +-- environment.py
    |       +-- testlab_steps/
    |       |   +-- example.py
    |       +-- testlab_environment.py

  Scenario: Use steps from a directory other than "steps/"
    Given a new working directory
      And a file named "features/example_use_different_steps.feature" with:
          """
          Feature:
            Scenario:
              When I do something
          """
      And a file named "features/alternate_environment.py" with:
          """
          def before_feature(context, feature):
              context.alternate_environment_is_in_use = True
          """
      And a file named "features/alternate_steps/example_steps.py" with:
          """
          from behave import step

          @step('I do something')
          def step_do_something(context):
              assert context.alternate_environment_is_in_use, \
                     "Expected alternate_environment.py to be used"
          """
     When I run "behave -f plain --steps-prefix alternate_ features/example_use_different_steps.feature"
     Then it should pass with:
          """
          1 feature passed, 0 failed, 0 skipped
          1 scenario passed, 0 failed, 0 skipped
          1 step passed, 0 failed, 0 skipped, 0 undefined
          """
