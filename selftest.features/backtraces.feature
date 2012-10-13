# -- BASED-ON: cucumber/features/backtraces.feature
# PROBLEMS:
#   - Make tracebacks regressionable
#   - Skip over parts of output, like Python doctest.
Feature: Backtraces
  In order to discover errors quickly
  As a tester
  I want to see backtraces for failures.

  Background: Test Setup
    Given a new working directory
    Given a file named "features/failing_hard.feature" with:
      """
      Feature: Sample
        Scenario: Example
          Given failing
      """

  Scenario: Backtraces enabled
    Given a file named "features/steps/steps.py" with:
      """
      from behave import given

      @given(u'failing')
      def step(context):
          raise RuntimeError("failing")
      """
    When I run "behave -c features/failing_hard.feature"
    Then it should fail with:
      """
      Feature: Sample # features/failing_hard.feature:1
        Scenario: Example  # features/failing_hard.feature:2
          Given failing    # features/steps/steps.py:3
            Traceback (most recent call last):
              File "{__CWD__}/behave/model.py", line 806, in run
                match.run(runner.context)
              File "{__CWD__}/behave/model.py", line 1119, in run
                self.func(context, *args, **kwargs)
              File "{__WORKDIR__}/features/steps/steps.py", line 5, in step
                raise RuntimeError("failing")
            RuntimeError: failing
      0 features passed, 1 failed, 0 skipped
      0 scenarios passed, 1 failed, 0 skipped
      0 steps passed, 1 failed, 0 skipped, 0 undefined
      """

