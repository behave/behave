@issue
@unicode
Feature: Issue #453 -- Unicode output problem when Exception is raised in step

  . Either Exception text (as summary) or traceback python line shows
  . special characters incorrectly.
  .
  . Result (of failed step):
  .     File "features/steps/steps.py", line 8, in foo
  .        raise Exception(u"Ð¿Ð¾ Ñ�Ñ�Ñ�Ñ�ÐºÐ¸") <-- This is not
  .   Exception: по русски <-- This is OK


    Scenario:
      Given a new working directory
      And a file named "features/steps/problematic_steps.py" with:
        """
        # -*- coding: UTF-8 -*-
        from behave import step

        @step(u'an exception with special chars is raised')
        def step_exception_raised(context):
            raise Exception(u"по русски")
        """
      And a file named "features/syndrome.feature" with:
        """
        Feature:
          Scenario:
            Given an exception with special chars is raised
        """
      When I run "behave -f plain features/syndrome.feature"
      Then it should fail with:
        """
        Scenario:
          Given an exception with special chars is raised ... failed
        """
      And the command output should contain:
        """
          File "features/steps/problematic_steps.py", line 6, in step_exception_raised
            raise Exception(u"по русски")
        Exception: по русски
        """
