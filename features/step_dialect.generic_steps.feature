Feature: Step dialect for generic steps

  As a test/story writer
  I want to have a possibility to use generic steps
  So that I can execute a sequence of steps without BDD keywords (Given/When/Then)

  | SPECIFICATION: Generic step
  |   * Prefix each step with a '*' (asterisk/star) character to mark it as step
  |   * Provide step-functions/step definition with "@step" decorator


  @setup
  Scenario: Feature Setup
    Given a new working directory
    And a file named "features/steps/steps.py" with:
        """
        from behave import step

        @step('{word:w} step passes')
        def step_passes(context, word):
            pass

        @step('{word:w} step passes with "{param}"')
        def step_passes_with_param(context, word, param):
            pass

        @step('a multi-line text step with')
        def step_with_multiline_text(context):
            assert context.text is not None, "REQUIRE: multi-line text"

        @step('a step fails with "{param}"')
        def step_fails_with_param(context, param=None):
            assert False, "XFAIL-STEP: %s" % param

        @step('a step fails')
        def step_fails(context):
            assert False, "XFAIL-STEP"

        @step('a table step with')
        def step_with_table(context):
            assert context.table, "REQUIRES: table"
            context.table.require_columns(["name", "age"])
        """


  Scenario: Simple step-by-step example

      * a step passes
      * another step passes


  Scenario: Simple step-by-step example 2
    Given a file named "features/generic_steps.feature" with:
        """
        Feature:
          Scenario:
            * a step passes
            * another step passes
            * a step passes with "Alice"
            * another step passes with "Bob"
        """
    When I run "behave -f plain -T features/generic_steps.feature"
    Then it should pass with:
        """
        1 scenario passed, 0 failed, 0 skipped
        4 steps passed, 0 failed, 0 skipped
        """
    And the command output should contain:
        """
        Feature:
          Scenario:
            * a step passes ... passed
            * another step passes ... passed
            * a step passes with "Alice" ... passed
            * another step passes with "Bob" ... passed
        """

  Scenario: Simple step-by-step example with failing steps
    Given a file named "features/generic_steps.failing.feature" with:
        """
        Feature:
          Scenario:
            * a step passes
            * a step fails with "Alice"
            * a step fails with "Bob"
            * another step passes
        """
    When I run "behave -f plain -T features/generic_steps.failing.feature"
    Then it should fail with:
        """
        0 scenarios passed, 1 failed, 0 skipped
        1 step passed, 1 failed, 2 skipped
        """
    And the command output should contain:
        """
        Feature:
          Scenario:
            * a step passes ... passed
            * a step fails with "Alice" ... failed
        """


  Scenario: Simple step-by-step example with scenario description

    CASE: Ensure that first step is discovered after last description line.

      Given a file named "features/generic_steps.with_description.feature" with:
        '''
        Feature:
          Scenario:

            First scenario description line.
            Second scenario description line.

              * a step passes
              * another step passes
        '''
      When I run "behave -f plain -T features/generic_steps.with_description.feature"
      Then it should pass with:
        """
        1 scenario passed, 0 failed, 0 skipped
        2 steps passed, 0 failed, 0 skipped
        """


  Scenario: Simple step-by-step example with multi-line text
    Given a file named "features/generic_steps.with_text.feature" with:
      '''
      Feature:
        Scenario:
          * a step passes
          * a multi-line text step with:
              """
              First line of multi-line text.
              Second-line of multi-line text.
              """
          * another step passes with "Charly"
      '''
    When I run "behave -f plain -T features/generic_steps.with_text.feature"
    Then it should pass with:
      """
      1 scenario passed, 0 failed, 0 skipped
      3 steps passed, 0 failed, 0 skipped
      """
    And the command output should contain:
      '''
      Feature:

        Scenario:
          * a step passes ... passed
          * a multi-line text step with ... passed
            """
            First line of multi-line text.
            Second-line of multi-line text.
            """
          * another step passes with "Charly" ... passed
      '''

  Scenario: Simple step-by-step example with table
    Given a file named "features/generic_steps.with_table.feature" with:
      '''
      Feature:
        Scenario:
          * a step passes
          * a table step with:
              | name  | age |
              | Alice | 10  |
              | Bob   | 12  |
          * another step passes with "Dodo"
      '''
    When I run "behave -f plain -T features/generic_steps.with_table.feature"
    Then it should pass with:
      """
      1 scenario passed, 0 failed, 0 skipped
      3 steps passed, 0 failed, 0 skipped
      """
    And the command output should contain:
      '''
      Feature:
        Scenario:
          * a step passes ... passed
          * a table step with ... passed
              | name  | age |
              | Alice | 10  |
              | Bob   | 12  |
          * another step passes with "Dodo" ... passed
      '''


