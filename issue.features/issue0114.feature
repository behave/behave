@issue
@change_request
Feature: Issue #114: Avoid unnecessary blank lines w/ --no-skipped option

    . Unnessary blank lines appear when you use (for each skipped feature):
    .
    .    behave -f progress --tags=@one --no-skipped ...

  @setup
  Scenario: Feature Setup
    Given a new working directory
    And   a file named "features/steps/passing_steps.py" with:
        """
        from behave import step

        @step(u'a step passes')
        def step_passes(context):
            pass
        """
    And   a file named "features/e1.feature" with:
        """
        @example
        Feature: E1
          Scenario: S1.1
            Given a step passes
        """
    And   a file named "features/e2.feature" with:
        """
        @exclude
        Feature: E2
          Scenario: S2.1
            Given a step passes
        """
    And   a file named "features/e3.feature" with:
        """
        @example
        Feature: E3
          Scenario: S3.1
            Given a step passes
        """

  Scenario: Run Features with tags and --show-skipped option
    When I run "behave -f progress --tags=@example"
    Then it should pass with:
        """
        2 features passed, 0 failed, 1 skipped
        2 scenarios passed, 0 failed, 1 skipped
        2 steps passed, 0 failed, 1 skipped, 0 undefined
        """
    And the command output should contain:
        """
        features/e1.feature  .
        features/e2.feature  S
        features/e3.feature  .
        """

  Scenario: Run Features with tag and --no-skipped option (CASE 1)
    When I run "behave -f progress --tags=@example --no-skipped"
    Then it should pass with:
        """
        2 features passed, 0 failed, 1 skipped
        2 scenarios passed, 0 failed, 1 skipped
        2 steps passed, 0 failed, 1 skipped, 0 undefined
        """
    And the command output should contain exactly:
        """
        features/e1.feature  .
        features/e3.feature  .
        """
    But the command output should not contain exactly:
        """
        features/e1.feature  .

        features/e3.feature  .
        """

  Scenario: Run Features with other tag and --no-skipped option (CASE 2)
    When I run "behave -f progress --tags=@exclude --no-skipped"
    Then it should pass with:
        """
        1 feature passed, 0 failed, 2 skipped
        1 scenario passed, 0 failed, 2 skipped
        1 step passed, 0 failed, 2 skipped, 0 undefined
        """
    And the command output should contain exactly:
        """
        features/e2.feature  .
        """

  Scenario: Run Features with tag, --no-skipped and plain formatter (CASE 3)
    When I run "behave -f plain --tags=@example --no-skipped -T"
    Then it should pass with:
        """
        2 features passed, 0 failed, 1 skipped
        2 scenarios passed, 0 failed, 1 skipped
        2 steps passed, 0 failed, 1 skipped, 0 undefined
        """
    And the command output should contain exactly:
        """
        Feature: E1

          Scenario: S1.1
            Given a step passes ... passed

        Feature: E3

        """
    But the command output should not contain exactly:
        """
        Feature: E1

          Scenario: S1.1
            Given a step passes ... passed


        Feature: E3

        """
