@issue
Feature: Issue #84: behave.runner behave does not reliably detected failed test runs

    | Behave does currently not reliably detected failed test runs and
    | therefore returns not sys.exit(1) at end of main().
    |
    | 1. behave.runner:Runner.run_with_paths() returns failed==True
    |    if last feature was successful and test runner does not stop
    |    after first failing feature.
    |
    | 2. Issue #64: Same problem in behave.model.Feature.run() with scenarios

  Scenario: Test Setup
    Given a new working directory
    And   a file named "features/passing.feature" with:
        """
        Feature: Passing
          Scenario:
            Given a step passes
            When  a step passes
            Then  a step passes
        """
    And   a file named "features/failing.feature" with:
        """
        Feature: Failing
          Scenario:
            Given a step fails
            When  a step fails
            Then  a step fails
        """
    And   a file named "features/steps/steps.py" with:
        """
        from behave import step

        @step(u'a step passes')
        def step_passes(context):
            pass

        @step(u'a step fails')
        def step_fails(context):
            assert False, "step: a step fails"
        """

  Scenario: First feature fails, second feature passes
    When I run "behave -f plain features/failing.feature features/passing.feature"
    Then it should fail with:
        """
        1 feature passed, 1 failed, 0 skipped
        1 scenario passed, 1 failed, 0 skipped
        3 steps passed, 1 failed, 2 skipped, 0 undefined
        """

  Scenario: First feature passes, second feature fails
    When I run "behave -f plain features/passing.feature features/failing.feature"
    Then it should fail with:
        """
        1 feature passed, 1 failed, 0 skipped
        1 scenario passed, 1 failed, 0 skipped
        3 steps passed, 1 failed, 2 skipped, 0 undefined
        """

  Scenario: First feature passes, second fails, last passes
    When I run "behave -f plain features/passing.feature features/failing.feature features/passing.feature"
    Then it should fail with:
        """
        2 features passed, 1 failed, 0 skipped
        2 scenarios passed, 1 failed, 0 skipped
        6 steps passed, 1 failed, 2 skipped, 0 undefined
        """
