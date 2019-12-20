@issue
@already_fixed
Feature: Issue #148: Substeps do not fail

  FIXED-BY: issue #117 context.execute_steps() should support table and multi-line text.
  RELATED-TO: issue #96

  @setup
  Scenario: Setup
    Given a new working directory
    And a file named "features/steps/passing_steps.py" with:
        """
        @step('a step passes')
        def step_passes(context):
            pass

        @step('a step fails')
        def step_fails(context):
            assert False, "XFAIL"
        """
    And a file named "features/issue0148_example.feature" with:
        """
        Feature: Sub steps

          @xfail
          Scenario: Failing test without substeps
            Given a step passes
            When a step fails
            Then a step passes

          @xfail
          Scenario: Failing test with substeps
            Given a step passes
            When I do something with stupid substeps
            Then a step passes
        """

  Scenario: Missing Step Keywords in Substeps
    Given a file named "features/steps/substeps.py" with:
        """
        @When('I do something with stupid substeps')
        def step(context):
            context.execute_steps(u'''
                I do something stupid
                there is a second stupid step
            ''')  # Given/When/Then keywords are missing in substeps above.
        """
    When I run "behave -f plain -T features/issue0148_example.feature"
    Then it should fail with:
        """
        0 features passed, 1 failed, 0 skipped
        0 scenarios passed, 2 failed, 0 skipped
        2 steps passed, 2 failed, 2 skipped, 0 undefined
        """
    And the command output should contain:
        """
          Scenario: Failing test without substeps
            Given a step passes ... passed
            When a step fails ... failed
        """
    And the command output should contain:
        """
          Scenario: Failing test with substeps
            Given a step passes ... passed
            When I do something with stupid substeps ... failed
        """
    And the command output should contain:
        """
        ParserError: Failed to parse <string>:
        Parser failure in state=steps at line 2: "I do something stupid"
        """


  Scenario: Use Step Keywords in Substeps
    Given a file named "features/steps/substeps.py" with:
        """
        @when('I do something with stupid substeps')
        def step(context):
            context.execute_steps(u'''
                When a step fails
                Then a step fails
            ''')
        """
    When I run "behave -f plain -T features/issue0148_example.feature"
    Then it should fail with:
        """
        0 features passed, 1 failed, 0 skipped
        0 scenarios passed, 2 failed, 0 skipped
        2 steps passed, 2 failed, 2 skipped, 0 undefined
        """
    And the command output should contain:
        """
          Scenario: Failing test with substeps
            Given a step passes ... passed
            When I do something with stupid substeps ... failed
            Assertion Failed: FAILED SUB-STEP: When a step fails
            Substep info: Assertion Failed: XFAIL
        """
    But the command output should not contain:
        """

        ParserError: Failed to parse <string>
        """


