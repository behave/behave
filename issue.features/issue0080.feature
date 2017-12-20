@issue
Feature: Issue #80: source file names not properly printed with python3

  . $ behave -f pretty example/example.feature
  . Scenario: run a simple test         # example/example.feature:3
  .    Given we have behave installed   # <string>:3
  .    When we implement a test         # <string>:7
  .    Then behave will test it for us! # <string>:11


  Background: Test Setup
    Given a new working directory
    And   a file named "features/steps/steps.py" with:
        """
        from behave import given, when, then

        @given(u'a step passes')
        def step(context):
            pass

        @when(u'a step passes')
        def step(context):
            pass

        @then(u'a step passes')
        def step(context):
            pass
        """
    And   a file named "features/basic.feature" with:
        """
        Feature:
          Scenario:
            Given a step passes
            When  a step passes
            Then  a step passes
        """

  Scenario: Show step locations
    When I run "behave -c -f pretty --no-timings features/basic.feature"
    Then it should pass
    And the command output should contain:
        """
        Feature:  # features/basic.feature:1
          Scenario:             # features/basic.feature:2
            Given a step passes # features/steps/steps.py:3
            When a step passes  # features/steps/steps.py:7
            Then a step passes  # features/steps/steps.py:11
        """
    And the command output should not contain "# <string>:"
