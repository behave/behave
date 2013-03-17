@issue
@change_request
Feature: Issue #116: SummaryReporter shows failed scenarios list

  Scenario: Test Setup
    Given a new working directory
    And   a file named "features/steps/passing_failing_steps.py" with:
        """
        from behave import step

        @step(u'a step passes')
        def step_passes(context):
            pass

        @step(u'a step fails')
        def step_fails(context):
            assert False, "FAILS"
        """
    And   a file named "features/e1.feature" with:
        """
        Feature: E1

          Scenario: E1.1
            Given a step passes

          @xfail
          Scenario: E1.2 (XFAIL)
            Given a step fails

          Scenario: E1.3
            Given a step passes
        """
    And   a file named "features/e2.feature" with:
        """
        @example2
        Feature: E2

          @xfail
          Scenario: E2.1 (XFAIL)
            Given a step fails

          Scenario: E2.2
            Given a step passes
        """

  Scenario: Summary shows list of failed scenarios when at least one fails
    When I run "behave -f plain features/"
    Then it should fail
    And the command output should contain:
        """
        Failing scenarios:
          features/e1.feature:7  E1.2 (XFAIL)
          features/e2.feature:5  E2.1 (XFAIL)

        0 features passed, 2 failed, 0 skipped
        3 scenarios passed, 2 failed, 0 skipped
        3 steps passed, 2 failed, 0 skipped, 0 undefined
        """

  Scenario: Summary hides list of failed scenarios when all scenarios pass
    When I run "behave -f plain --tags=~@xfail features/"
    Then it should pass with:
        """
        2 features passed, 0 failed, 0 skipped
        3 scenarios passed, 0 failed, 2 skipped
        3 steps passed, 0 failed, 2 skipped, 0 undefined
        """
    But the command output should not contain:
        """
        Failing scenarios:
        """
