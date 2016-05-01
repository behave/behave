@issue
Feature: Issue #288 -- Use print function instead print statement in environment/steps files

  . Loaded files have future flags of importing module "behave.runner".
  . This should be removed.
  .
  . AFFECTED FILES:
  .   * features/environment.py
  .   * features/steps/*.py
  .
  . AFFECTED FUTURE FLAGS:
  .   * print_function
  .   * absolute_import
  .   * ...

  @setup
  Scenario: Feature Setup
    Given a new working directory
    And a file named "features/steps/reuse_steps.py" with:
        """
        from behave4cmd0 import passing_steps
        """
    And a file named "features/passing.feature" with:
        """
        Feature:
          Scenario:
            Given a step passes
        """

  @preferred
  Scenario: Use print function with future-statement in steps/environment (PY2, PY3)
    Given a file named "features/steps/my_steps.py" with:
        """
        from __future__ import print_function
        print("Hello step")
        """
    And a file named "features/environment.py" with:
        """
        from __future__ import print_function
        print("Hello environment")
        """
    When I run "behave -f plain features/passing.feature"
    Then it should pass with:
        """
        1 scenario passed, 0 failed, 0 skipped
        1 step passed, 0 failed, 0 skipped, 0 undefined
        """
    And the command output should not contain:
        """
        Traceback (most recent call last):
        """

  @use.with_python2=true
  Scenario: Use python2 print keyword in steps/environment
    Given a file named "features/steps/my_steps.py" with:
        """
        print "Hello step"
        """
    And a file named "features/environment.py" with:
        """
        print "Hello step"
        """
    When I run "behave -f plain features/passing.feature"
    Then it should pass with:
        """
        1 scenario passed, 0 failed, 0 skipped
        1 step passed, 0 failed, 0 skipped, 0 undefined
        """
    And the command output should not contain "SyntaxError"
    And the command output should not contain:
        """
        Traceback (most recent call last):
        """

  @use.with_python3=true
  Scenario: Use print function without future-statement in steps/environment (PY3)
    Given a file named "features/steps/my_steps.py" with:
        """
        print("Hello step")
        """
    And a file named "features/environment.py" with:
        """
        print("Hello environment")
        """
    When I run "behave -f plain features/passing.feature"
    Then it should pass with:
        """
        1 scenario passed, 0 failed, 0 skipped
        1 step passed, 0 failed, 0 skipped, 0 undefined
        """
    And the command output should not contain:
        """
        Traceback (most recent call last):
        """

