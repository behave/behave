@sequential
@todo
Feature: Runner should support a --dry-run option

    As a tester
    I want to check if behave tests are syntactically correct
    And all step definitions exist
    Before I actually run the tests (by executing steps).

    . SPECIFICATION: Dry-run mode
    .   * Undefined steps are detected
    .   * Marks steps as "untested" or "undefined"
    .   * Marks scenarios as "untested"
    .   * Marks features as "untested"
    .   * Causes no failed scenarios, features
    .   * Causes failed test-run when undefined steps are found.

  Background: Setup
    Given a new working directory
    And a file named "features/steps/steps.py" with:
      """
      from behave import step

      @step('a step passes')
      def step_passes(context):
          pass

      @step('a step fails')
      def step_fails(context):
          assert False, "XFAIL"
      """
    And a file named "features/alice.feature" with:
      """
      Feature: Alice

          @selected
          Scenario: A1
              Given a step passes
              When a step passes
              Then a step passes

          @other_selected
          Scenario: A2
              Given a step passes
              When a step fails
              Then a step passes

          @selected
          Scenario: A3
              Given a step passes

          @selected
          Scenario: A4
              Given a step fails
      """
    And a file named "features/bob.feature" with:
      """
      Feature: Bob
          Scenario: B1
              Given a step passes
              When a step passes
              Then a step passes

          Scenario: B2
              Given a step passes
              When a step fails
              Then a step passes
      """

  Rule: Normal case
    Scenario: Dry-run one feature should mark feature/scenarios/steps as untested
        When I run "behave -f plain --dry-run features/alice.feature"
        Then it should pass with:
            """
            0 features passed, 0 failed, 0 skipped, 1 untested
            0 scenarios passed, 0 failed, 0 skipped, 4 untested
            0 steps passed, 0 failed, 0 skipped, 8 untested
            """
        And the command output should contain
            """
            Scenario: A1
            """
        And the command output should contain:
            """
            Scenario: A2
            """
        And the command output should contain:
            """
            Scenario: A3
            """
        And the command output should contain:
            """
            Scenario: A4
            """
        And note that "all scenarios of this feature are contained"

    Scenario: Dry-run one feature with tags should mark skipped scenario/steps as skipped
        When I run "behave -f plain --dry-run --tags=@selected --no-skipped features/alice.feature"
        Then it should pass with:
            """
            0 features passed, 0 failed, 0 skipped, 1 untested
            0 scenarios passed, 0 failed, 1 skipped, 3 untested
            0 steps passed, 0 failed, 3 skipped, 5 untested
            """
        And the command output should contain:
            """
            Scenario: A1
            """
        And the command output should contain:
            """
            Scenario: A3
            """
        And the command output should contain:
            """
            Scenario: A4
            """
        But the command output should not contain:
            """
            Scenario: A2
            """
        And note that "only tagged scenarios of this feature are contained (3 of 4)"

    Scenario: Dry-run two features
        When I run "behave --dry-run features/alice.feature features/bob.feature"
        Then it should pass with:
            """
            0 features passed, 0 failed, 0 skipped, 2 untested
            0 scenarios passed, 0 failed, 0 skipped, 6 untested
            0 steps passed, 0 failed, 0 skipped, 14 untested
            """

  Rule: With undefined steps
    Background:
      HINT: Inherits common background steps.

      Given a file named "features/undefined_steps.feature" with:
        """
        Feature: Undefined Steps

            @selected
            Scenario: U1
                Given a step passes
                When a step is undefined
                Then a step fails

            @other_selected
            Scenario: U2 fails
                Given a step is undefined
                When a step passes
                And  a step fails
                Then a step is undefined
        """

    @todo.needs_feature_error
    Scenario: Dry-run one feature with undefined steps
      When I run "behave --dry-run features/undefined_steps.feature"
      Then it should fail with:
          """
          0 features passed, 0 failed, 0 skipped, 1 untested
          0 scenarios passed, 0 failed, 1 error, 0 skipped, 1 untested
          0 steps passed, 0 failed, 0 skipped, 3 undefined, 4 untested
          """

    @todo.needs_feature_error
    Scenario: Dry-run two features, one with undefined steps
      When I run "behave -f plain --dry-run features/alice.feature features/undefined_steps.feature"
      Then it should fail with:
        """
        0 features passed, 0 failed, 0 skipped, 2 untested
        0 scenarios passed, 0 failed, 1 error, 0 skipped, 5 untested
        0 steps passed, 0 failed, 0 skipped, 3 undefined, 12 untested
        """
      And the command output should contain:
        """
        Feature: Alice
          Scenario: A1
            Given a step passes ... untested
            When a step passes ... untested
            Then a step passes ... untested

          Scenario: A2
            Given a step passes ... untested
            When a step fails ... untested
            Then a step passes ... untested

          Scenario: A3
            Given a step passes ... untested

          Scenario: A4
            Given a step fails ... untested

        Feature: Undefined Steps
          Scenario: U1
            Given a step passes ... untested
            When a step is undefined ... undefined

          Scenario: U2 fails
            Given a step is undefined ... undefined
            When a step passes ... untested
        """
      But the command output should contain:
        """
        Errored scenarios:
          features/undefined_steps.feature:10  U2 fails
        """


    Scenario: Dry-run two features, one with undefined steps and use tags
      When I run "behave -f plain --dry-run --tags=@selected features/alice.feature features/undefined_steps.feature"
      Then it should fail with:
        """
        0 features passed, 0 failed, 0 skipped, 2 untested
        0 scenarios passed, 0 failed, 2 skipped, 4 untested
        0 steps passed, 0 failed, 7 skipped, 1 undefined, 7 untested
        """

    Scenario: Dry-run two features, one with undefined steps and use other tags
      When I run "behave -f plain --dry-run --tags=@other_selected features/alice.feature features/undefined_steps.feature"
      Then it should fail with:
        """
        0 features passed, 0 failed, 1 error, 0 skipped, 1 untested
        0 scenarios passed, 0 failed, 1 error, 4 skipped, 1 untested
        0 steps passed, 0 failed, 8 skipped, 2 undefined, 5 untested
        """
      And the command output should contain:
        """
        Feature: Alice
          Scenario: A1

          Scenario: A2
            Given a step passes ... untested
            When a step fails ... untested
            Then a step passes ... untested

          Scenario: A3
          Scenario: A4

        Feature: Undefined Steps

          Scenario: U1

          Scenario: U2 fails
            Given a step is undefined ... undefined
            When a step passes ... untested
        """
      But the command output should contain:
        """
        Errored scenarios:
          features/undefined_steps.feature:10  U2 fails
        """

  Rule: Pending steps are not detected in dry-run mode
    Background:
      HINT: Inherits common background steps.

      Given a file named "features/pending_steps.feature" with:
        """
        Feature: Pending Steps

            @selected
            Scenario: P1
                Given a step passes
                When a step is pending
                Then a step fails

            @other_selected
            Scenario: P2 fails
                Given a step is pending
                When a step passes
                And  a step fails
                Then a step is pending
        """
      And a file named "features/steps/pending_steps.py" with:
        """
        from behave import step
        from behave.exception import StepNotImplementedError

        @step(u'a step is pending')
        def step_is_pending(context):
            raise StepNotImplementedError("OOPS")
        """


    @todo.needs_feature_error
    Scenario: Dry-run one feature with pending steps
      When I run "behave -f plain --dry-run features/pending_steps.feature"
      Then it should pass with:
        """
        0 features passed, 0 failed, 0 skipped, 1 untested
        0 scenarios passed, 0 failed, 0 skipped, 2 untested
        0 steps passed, 0 failed, 0 skipped, 7 untested
        """
      And the command output should contain:
        """
        Feature: Pending Steps
          Scenario: P1
            Given a step passes ... untested
            When a step is pending ... untested
            Then a step fails ... untested

          Scenario: P2 fails
            Given a step is pending ... untested
            When a step passes ... untested
            And a step fails ... untested
            Then a step is pending ... untested
        """
      But note that "pending steps are not detected in dry-run mode"


    @todo.needs_feature_error
    Scenario: Dry-run two features, one with pending steps
      When I run "behave -f plain --dry-run features/alice.feature features/pending_steps.feature"
      Then it should pass with:
        """
        0 features passed, 0 failed, 0 skipped, 2 untested
        0 scenarios passed, 0 failed, 0 skipped, 6 untested
        0 steps passed, 0 failed, 0 skipped, 15 untested
        """
      And the command output should contain:
        """
        Feature: Alice
          Scenario: A1
            Given a step passes ... untested
            When a step passes ... untested
            Then a step passes ... untested

          Scenario: A2
            Given a step passes ... untested
            When a step fails ... untested
            Then a step passes ... untested

          Scenario: A3
            Given a step passes ... untested

          Scenario: A4
            Given a step fails ... untested

        Feature: Pending Steps
          Scenario: P1
            Given a step passes ... untested
            When a step is pending ... untested
            Then a step fails ... untested

          Scenario: P2 fails
            Given a step is pending ... untested
            When a step passes ... untested
            And a step fails ... untested
            Then a step is pending ... untested
        """
      But note that "pending steps are not detected in dry-run mode"


    Scenario: Dry-run two features, one with pending steps and use tags
      When I run "behave -f plain --dry-run --tags=@selected features/alice.feature features/pending_steps.feature"
      Then it should pass with:
        """
        0 features passed, 0 failed, 0 skipped, 2 untested
        0 scenarios passed, 0 failed, 2 skipped, 4 untested
        0 steps passed, 0 failed, 7 skipped, 8 untested
        """
      And the command output should contain:
        """
        Feature: Alice

          Scenario: A1
            Given a step passes ... untested
            When a step passes ... untested
            Then a step passes ... untested

          Scenario: A2

          Scenario: A3
            Given a step passes ... untested

          Scenario: A4
            Given a step fails ... untested

        Feature: Pending Steps

          Scenario: P1
            Given a step passes ... untested
            When a step is pending ... untested
            Then a step fails ... untested

          Scenario: P2 fails
        """
      But note that "pending steps are not detected in dry-run mode"


    Scenario: Dry-run two features, one with pending steps and use other tags
      When I run "behave -f plain --dry-run --tags=@other_selected features/alice.feature features/pending_steps.feature"
      Then it should pass with:
        """
        0 features passed, 0 failed, 0 skipped, 2 untested
        0 scenarios passed, 0 failed, 4 skipped, 2 untested
        0 steps passed, 0 failed, 8 skipped, 7 untested
        """
      And the command output should contain:
        """
        Feature: Alice
          Scenario: A1

          Scenario: A2
            Given a step passes ... untested
            When a step fails ... untested
            Then a step passes ... untested

          Scenario: A3
          Scenario: A4

        Feature: Pending Steps
          Scenario: P1

          Scenario: P2 fails
            Given a step is pending ... untested
            When a step passes ... untested
            And a step fails ... untested
            Then a step is pending ... untested
        """
      But note that "pending steps are not detected in dry-run mode"
