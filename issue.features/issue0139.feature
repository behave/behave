@issue
@not_reproducible
Feature: Issue #139: Wrong steps seem to be executed when using --wip

  | RELATED-TO: issue #35
  | behave --format=plain --tags @one" seems to execute right scenario w/ wrong steps
  |
  | If you have a feature file with two scenarios where the second is tagged
  | with @wip, running behave -w will output step names from the first scenario.
  | It does seem to run the correct code for the steps.


  Scenario:
    Given a new working directory
    And a file named "features/steps/steps.py" with:
        """
        from behave import given, when, then, step

        @step('a step passes')
        def step_passes(context):
            pass

        @step('a step fails')
        def step_fails(context):
            assert False, "XFAIL"

        @when('I run a test step')
        def step_impl(context):
            pass

        @when('I run some other test step')
        def step_impl(context):
            pass

        @then('I should not see a failure here')
        def step_impl(context):
            pass
        """
    And a file named "features/issue0139_example.feature" with:
        """
        Feature: Bug in wip/behave -w

            Scenario: This is strange
                Given a step passes
                When a step passes
                Then a step fails

            @wip
            Scenario: Demonstrate bug
                When I run a test step
                And I run some other test step
                Then I should not see a failure here
        """
    When I run "behave -w -f plain -T features/issue0139_example.feature"
    Then it should pass
    And the command output should contain:
        """
        Feature: Bug in wip/behave -w
          Scenario: This is strange
          Scenario: Demonstrate bug
            When I run a test step ... passed
            And I run some other test step ... passed
            Then I should not see a failure here ... passed
        """



