@issue
@user_error
@python2.problem
Feature: Issue #506 -- Behave stops on error

    . ANALYSIS:
    .   Using exception.__cause__ = original_exception causes problems in Python2
    .   When you use the Python3 chained-exception mechanism,
    .   you should better ensure that the "original_exception.__traceback__" attribute
    .   exists. Otherwise, a new exception (missing attribute) is raised
    .   when you format the traceback,

    Scenario:
      Given a new working directory
      And a file named "features/steps/pass_steps.py" with:
        """
        from behave import step

        @step('{word:w} step passes')
        def step_passes(context, word):
            pass

        """
      And a file named "features/steps/steps.py" with:
        """
        from behave import when, then
        from behave._types import ChainedExceptionUtil
        import copy

        @when('I bad chained-exception causes my step to fail')
        def step_bad_usage_of_chained_exception(context):
            # -- BAD IMPLEMENATION:
            exception = ZeroDivisionError('integer division or modulo by zero')
            exception.__cause__ = copy.copy(exception)
            raise exception

        @when('a chained-exception causes my step to fail')
        def step_chained_exception_causes_failure(context):
            try:
                raise ZeroDivisionError("OOPS-1")
            except ZeroDivisionError as e:
                e2 = RuntimeError("OOPS-2")
                ChainedExceptionUtil.set_cause(e2, e)
                raise e2

        @then('this step must be executed')
        def step_check_step(context):
            pass
        """
      And a file named "features/syndrome.feature" with:
        """
        Feature: Failing step which can lead to stop behave

          @failing
          Scenario: Run stopping behave scenario
            When a chained-exception causes my step to fail
            Then this step must be executed
        """
      When I run "behave -f plain features/syndrome.feature"
      Then it should fail with:
        """
        0 scenarios passed, 1 failed, 0 skipped
        """
      And the command output should contain:
        """
          ZeroDivisionError: OOPS-1

        The above exception was the direct cause of the following exception:

        Traceback (most recent call last):
        """
      And the command output should contain:
        """
          File "features/steps/steps.py", line 19, in step_chained_exception_causes_failure
            raise e2
        RuntimeError: OOPS-2
        """
