Feature: Undefined Step

  . TERMINOLOGY:
  .  * An undefined step is a step without matching step implementation.
  .
  . SPECIFICATION:
  .  * An undefined step should be reported after the run.
  .  * An undefined step should cause its scenario to fail.
  .  * If an undefined step is detected the remaining scenario steps are skipped.
  .  * All undefined steps in a scenario should be reported (issue #42).
  .  * Undefined steps should be detected even after a step fails in a scenario.
  .  * Each undefined step should be reported only once.
  .  * If a scenario is disabled (by tag expression, etc.),
  .    the undefined step discovery should not occur.
  .    This allows to prepare scenarios that are not intended to run (yet).
  .  * Option --dry-run should discover undefined steps, too.
  .
  . RELATED TO:
  .  * issue #42  Multiple undefined steps in same scenario are detected.


    @setup
    Scenario: Feature Setup
      Given a new working directory
      And a file named "features/steps/passing_steps.py" with:
        """
        from behave import step

        @step('a step passes')
        def step_passes(context):
            pass

        @step('a step fails')
        def step_fails(context):
            assert False, "XFAIL"
        """
      And a file named "features/undefined_last_step.feature" with:
        """
        Feature:
          Scenario:
            Given a step passes
            When an undefined step is used
        """

    Scenario: An undefined step should be reported
      When I run "behave -f plain -T features/undefined_last_step.feature"
      Then it should fail
      And the command output should contain:
        """
        Feature:
           Scenario:
             Given a step passes ... passed
              When an undefined step is used ... undefined
        """
      And the command output should contain:
        """
        You can implement step definitions for undefined steps with these snippets:

        @when(u'an undefined step is used')
        def step_impl(context):
            raise NotImplementedError(u'STEP: When an undefined step is used')
        """
      And an undefined-step snippet should exist for "When an undefined step is used"


    Scenario: An undefined step should cause its scenario to fail
      When I run "behave -f plain features/undefined_last_step.feature"
      Then it should fail with:
        """
        0 features passed, 1 failed, 0 skipped
        0 scenarios passed, 1 failed, 0 skipped
        1 step passed, 0 failed, 0 skipped, 1 undefined
        """


    Scenario: Additional scenario steps after an undefined step are skipped
      Given a file named "features/undefined_step_and_more.feature" with:
        """
        Feature:
          Scenario:
            Given a step passes
            When an undefined step is used
            Then a step passes
            And  a step fails
        """
      When I run "behave -f plain -T features/undefined_step_and_more.feature"
      Then it should fail with:
        """
        0 features passed, 1 failed, 0 skipped
        0 scenarios passed, 1 failed, 0 skipped
        1 step passed, 0 failed, 2 skipped, 1 undefined
        """
      And the command output should contain:
        """
        Feature:
           Scenario:
             Given a step passes ... passed
              When an undefined step is used ... undefined
        """


    Scenario: Two undefined steps in same scenario should be detected
      Given a file named "features/two_undefined_steps1.feature" with:
        """
        Feature:
          Scenario:
            Given a step passes
            When an undefined step is used
            And  a step fails
            Then another undefined step is used
        """
      When I run "behave -f plain -T features/two_undefined_steps1.feature"
      Then it should fail with:
        """
        0 features passed, 1 failed, 0 skipped
        0 scenarios passed, 1 failed, 0 skipped
        1 step passed, 0 failed, 1 skipped, 2 undefined
        """
      And the command output should contain:
        """
        Feature:
           Scenario:
             Given a step passes ... passed
              When an undefined step is used ... undefined
        """
      And undefined-step snippets should exist for:
        | Step |
        | When an undefined step is used |
        | Then another undefined step is used |
      But the command output should not contain:
        """
        And a step fails ... skipped
        Then another undefined step is used ... undefined
        """


    Scenario: Two undefined steps in different scenarios
      Given a file named "features/two_undefined_steps2.feature" with:
        """
        Feature:
          Scenario:
            Given a step passes
            When an undefined step is used

          Scenario:
            Given another undefined step is used
            When a step passes
        """
      When I run "behave -f plain -T features/two_undefined_steps2.feature"
      Then it should fail with:
        """
        0 features passed, 1 failed, 0 skipped
        0 scenarios passed, 2 failed, 0 skipped
        1 step passed, 0 failed, 1 skipped, 2 undefined
        """
      And the command output should contain:
        """
        Feature:
           Scenario:
             Given a step passes ... passed
              When an undefined step is used ... undefined

           Scenario:
             Given another undefined step is used ... undefined
        """
      And undefined-step snippets should exist for:
        | Step |
        | When an undefined step is used |
        | Given another undefined step is used |


    Scenario: Undefined step in Scenario Outline
      Given a file named "features/undefined_step_in_scenario_outline.feature" with:
        """
        Feature:
          Scenario Outline:
            Given a step <outcome1>
            When an undefined step is used
            Then a step <outcome2>

          Examples:
            | outcome1 | outcome2 |
            |  passes  | passes   |
            |  passes  | fails    |
            |  fails   | passes   |
            |  fails   | fails    |
        """
      When I run "behave -f plain -T features/undefined_step_in_scenario_outline.feature"
      Then it should fail with:
        """
        0 features passed, 1 failed, 0 skipped
        0 scenarios passed, 4 failed, 0 skipped
        2 steps passed, 2 failed, 4 skipped, 4 undefined
        """
      And an undefined-step snippet should exist for "When an undefined step is used"
      And the command output should contain:
        """
        Feature:
           Scenario Outline:  -- @1.1
             Given a step passes ... passed
              When an undefined step is used ... undefined

           Scenario Outline:  -- @1.2
             Given a step passes ... passed
              When an undefined step is used ... undefined

           Scenario Outline:  -- @1.3
             Given a step fails ... failed
             Assertion Failed: XFAIL

           Scenario Outline:  -- @1.4
             Given a step fails ... failed
             Assertion Failed: XFAIL
        """


    Scenario: Two undefined step in Scenario Outline
      Given a file named "features/two_undefined_step_in_scenario_outline.feature" with:
        """
        Feature:
          Scenario Outline:
            Given a step <outcome1>
            When an undefined step is used
            Then a step <outcome2>
            And another undefined step is used

          Examples:
            | outcome1 | outcome2 |
            |  passes  | passes   |
            |  passes  | fails    |
            |  fails   | passes   |
            |  fails   | fails    |
        """
      When I run "behave -f plain features/two_undefined_step_in_scenario_outline.feature"
      Then it should fail with:
        """
        0 features passed, 1 failed, 0 skipped
        0 scenarios passed, 4 failed, 0 skipped
        2 steps passed, 2 failed, 4 skipped, 8 undefined
        """
      And undefined-step snippets should exist for:
        | Step |
        | When an undefined step is used |
        | Then another undefined step is used |


    Scenario: Undefined steps are detected if scenario is selected via tag
      Given a file named "features/undefined_steps_with_tagged_scenario.feature" with:
        """
        Feature:

          @selected
          Scenario: S1
            Given a step passes
            And an undefined step Alice
            When a step fails
            Then an undefined step Bob

          @selected
          Scenario: S2
            Given a step passes
            When an undefined step Charly

          @not_selected
          Scenario: S3
            Given an undefined step Delta
            Then a step fails
        """
      When I run "behave -f plain --tags=@selected features/undefined_steps_with_tagged_scenario.feature"
      Then it should fail with:
        """
        0 features passed, 1 failed, 0 skipped
        0 scenarios passed, 2 failed, 1 skipped
        2 steps passed, 0 failed, 3 skipped, 3 undefined
        """
      And undefined-step snippets should exist for:
        | Step |
        | Given an undefined step Alice      |
        | Then an undefined step Bob    |
        | When an undefined step Charly |
      But undefined-step snippets should not exist for:
        | Step |
        | Given a step passes |
        | Given an undefined step Delta |
        | When a step fails |
        | Then a step fails |


    Scenario: Undefined steps are detected if --dry-run option is used
      When I run "behave -f plain --dry-run features/undefined_steps_with_tagged_scenario.feature"
      Then it should fail with:
        """
        0 features passed, 0 failed, 0 skipped, 1 untested
        0 scenarios passed, 0 failed, 0 skipped, 3 untested
        0 steps passed, 0 failed, 0 skipped, 4 undefined, 4 untested
        """
      And undefined-step snippets should exist for:
        | Step |
        | Given an undefined step Alice      |
        | Then an undefined step Bob    |
        | When an undefined step Charly |
        | Given an undefined step Delta |
      But undefined-step snippets should not exist for:
        | Step |
        | Given a step passes |
        | When a step fails |
        | Then a step fails |
