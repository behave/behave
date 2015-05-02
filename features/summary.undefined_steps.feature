Feature: Summary with Undefined Steps

  . SPECIFICATION:
  .  * An undefined step should be counted as "undefined" step.
  .  * An undefined step should cause its scenario to fail.
  .  * If an undefined step is detected the remaining scenario steps are skipped.
  .
  . RELATED TO:
  .  * issue #42  Multiple undefined steps in same scenario are detected.


    @setup
    Scenario: Test Setup
      Given a new working directory
      And a file named "features/steps/passing_steps.py" with:
        """
        from behave import step

        @step('a step passes')
        def step_passes(context):
            pass
        """

    Scenario: Undefined step as first step in a scenario
      Given a file named "features/summary_undefined_first_step.feature" with:
        """
        Feature:
          Scenario:
            Given an undefined step is used
            When a step passes
            Then a step passes
        """
      When I run "behave -f plain features/summary_undefined_first_step.feature"
      Then it should fail with:
        """
        0 features passed, 1 failed, 0 skipped
        0 scenarios passed, 1 failed, 0 skipped
        0 steps passed, 0 failed, 2 skipped, 1 undefined
        """

    Scenario: Undefined step as last step in a scenario
      Given a file named "features/summary_undefined_last_step.feature" with:
        """
        Feature:
          Scenario:
            Given a step passes
            When an undefined step is used
        """
      When I run "behave -f plain features/summary_undefined_last_step.feature"
      Then it should fail with:
        """
        0 features passed, 1 failed, 0 skipped
        0 scenarios passed, 1 failed, 0 skipped
        1 step passed, 0 failed, 0 skipped, 1 undefined
        """


    Scenario: Undefined step as middle step in a scenario
      Given a file named "features/summary_undefined_middle_step.feature" with:
        """
        Feature:
          Scenario:
            Given a step passes
            When an undefined step is used
            Then a step passes
            And  a step passes
        """
      When I run "behave -f plain features/summary_undefined_middle_step.feature"
      Then it should fail with:
        """
        0 features passed, 1 failed, 0 skipped
        0 scenarios passed, 1 failed, 0 skipped
        1 step passed, 0 failed, 2 skipped, 1 undefined
        """

    Scenario: Two undefined steps in same scenario, all are detected (skipped)
      Given a file named "features/summary_undefined_step2.feature" with:
        """
        Feature:
          Scenario:
            Given a step passes
            When an undefined step is used
            Then a step passes
            And  another undefined step is used
        """
      When I run "behave -f plain features/summary_undefined_step2.feature"
      Then it should fail with:
        """
        0 features passed, 1 failed, 0 skipped
        0 scenarios passed, 1 failed, 0 skipped
        1 step passed, 0 failed, 1 skipped, 2 undefined
        """


    Scenario: Two undefined steps in different scenarios
      Given a file named "features/summary_undefined_step_and_another.feature" with:
        """
        Feature:
          Scenario:
            Given a step passes
            When an undefined step is used
            Then a step passes

          Scenario:
            Given an undefined step is used
            When a step passes
        """
      When I run "behave -f plain features/summary_undefined_step_and_another.feature"
      Then it should fail with:
        """
        0 features passed, 1 failed, 0 skipped
        0 scenarios passed, 2 failed, 0 skipped
        1 step passed, 0 failed, 2 skipped, 2 undefined
        """
