@issue
Feature: Issue #67: JSON formatter cannot serialize tables.

  The JSON formatter cannot handle tables (currently):

    * Table as setup/intermediate/result table in steps of scenario
    * Examples tables in a ScenarioOutline

  A JSON exception occurs when such a feature file should be processed.


  Scenario: Scenario with Tables
    Given a new working directory
    And   a file named "features/steps/steps1.py" with:
      """
      from behave import given, when, then

      @given(u'I add the following employees')
      def step(context):
          pass  # -- SKIP: Table processing here.

      @when(u'I select department "{department}"')
      def step(context, department):
          context.department = department

      @then(u'I get the following employees')
      def step(context):
          pass  # -- SKIP: Table processing here.
      """
    And  a file named "features/issue67_case1.feature" with:
      """
      Feature: Scenario with Tables
        Scenario:
         Given I add the following employees:
            | name      | department  |
            | Alice     | Wonderland  |
            | Bob       | Moonwalk    |
          When I select department "Wonderland"
          Then I get the following employees:
            | name      | department  |
            | Alice     | Wonderland  |
      """
    When I run "behave -f json features/issue67_case1.feature"
    Then it should pass with:
      """
      1 scenario passed, 0 failed, 0 skipped
      3 steps passed, 0 failed, 0 skipped, 0 undefined
      """
    But the command output should not contain:
      """
      TypeError: <Row [u'Alice', u'Wonderland']> is not JSON serializable
      """

  Scenario: ScenarioOutline with Examples Table
    Given a file named "features/steps/steps2.py" with:
      """
      from behave import given, when, then

      @given(u'a step with "{name}"')
      def step(context, name):
          context.name = name

      @when(u'a step with "{name}" occurs')
      def step(context, name):
          assert context.name == name

      @then(u'a step with "{name}" is reached')
      def step(context, name):
          assert context.name == name
      """
    And a file named "features/issue67_case2.feature" with:
      """
      Feature: ScenarioOutline with Examples Table
        Scenario Outline:
          Given a step with "<name>"
          When  a step with "<name>" occurs
          Then  a step with "<name>" is reached

        Examples:
            |name |
            |Alice|
            |Bob  |
      """
    When I run "behave -f json features/issue67_case2.feature"
    Then it should pass with:
      """
      2 scenarios passed, 0 failed, 0 skipped
      6 steps passed, 0 failed, 0 skipped, 0 undefined
      """

