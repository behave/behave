Feature: Define custom settings to be used by step definitions

  As a tester
  I want to pass custom settings from outside behave to the step definitions
  So I can control resource usage and management of steps without changing code

  Background:
    Given a new working directory
      And a file named "features/file.feature" with:
          """
          Feature:
            Scenario:
              When a file is created as a result of a step
              Then it is cleaned up after the scenario unless told otherwise
          """
      And a file named "features/steps/file.py" with:
          """
          from behave import when, then

          @when("a file is created as a result of a step")
          def step_a_file_is_created_as_a_result_of_a_step(context):
              pass

          @then("it is cleaned up after the scenario unless told otherwise")
          def step_it_is_cleaned_up_after_the_scenario_unless_told_otherwise(context):
              keep_artifacts = getattr(context.config.userdata, "keep_artifacts", "no")

              assert "yes" == keep_artifacts, \
                     "Expected the custom option to be available in the context"
          """

    Scenario: Passing custom settings through the command line
      When I run "behave -f plain --define keep_artifacts=yes"
      Then it should pass with:
           """
           1 feature passed, 0 failed, 0 skipped
           1 scenario passed, 0 failed, 0 skipped
           2 steps passed, 0 failed, 0 skipped, 0 undefined
           """
