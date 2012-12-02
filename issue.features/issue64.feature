@issue
Feature: Issue #64 Exit status not set to 1 even there are failures in certain cases

  The behave exit status not always returns 1 when failure(s) occur.
  The problem was associated with the Feature.run() logic implementation.

  This problem was first discovered while verifying issue #52 (see comments).
  See also similar test when tags select a subset of scenarios.

  RELATED ISSUES:
    * issue #52

  Background: Test Setup
    Given a new working directory
    Given a file named "features/steps/steps.py" with:
      """
      from behave import given

      @given(u'passing')
      def step(context):
          pass

      @given(u'failing')
      def step(context):
          assert False, "failing"
      """

  Scenario: Failing in First Scenario
    Given a file named "features/issue64_case1.feature" with:
      """
      Feature: Failing in First Scenario
        Scenario:
          Given failing

        Scenario:
          Given passing
      """
    When I run "behave --format=plain features/issue64_case1.feature"
    Then it should fail with:
      """
      0 features passed, 1 failed, 0 skipped
      1 scenario passed, 1 failed, 0 skipped
      """

  Scenario: Failing in Middle Scenario
    Given a file named "features/issue64_case2.feature" with:
      """
      Feature: Failing in Middle Scenario
        Scenario:
          Given passing
        Scenario:
          Given failing
        Scenario:
          Given passing
      """
    When I run "behave --format=plain features/issue64_case2.feature"
    Then it should fail with:
      """
      0 features passed, 1 failed, 0 skipped
      2 scenarios passed, 1 failed, 0 skipped
      """

  Scenario: Failing in Last Scenario
    Given a file named "features/issue64_case3.feature" with:
      """
      Feature: Failing in Last Scenario
        Scenario:
          Given passing
        Scenario:
          Given passing
        Scenario:
          Given failing
      """
    When I run "behave --format=plain features/issue64_case3.feature"
    Then it should fail with:
      """
      0 features passed, 1 failed, 0 skipped
      2 scenarios passed, 1 failed, 0 skipped
      """

  Scenario: Failing in First and Last Scenario
    Given a file named "features/issue64_case4.feature" with:
      """
      Feature: Failing in First and Last Scenario
        Scenario:
          Given failing
        Scenario:
          Given passing
        Scenario:
          Given failing
      """
    When I run "behave --format=plain features/issue64_case4.feature"
    Then it should fail with:
      """
      0 features passed, 1 failed, 0 skipped
      1 scenario passed, 2 failed, 0 skipped
      """
