@issue
Feature: Issue #181: Escape apostrophes in undefined steps snippets

  . I have noticed that, for the following line in my features file:
  .
  .   Then I'm redirected to http://www.example.com
  .
  . Behave outputs the following:
  .
  .   @then(u'I'm redirected to http://www.example.com')
  .   def step_impl(context):
  .       assert False


  Scenario:
    Given a new working directory
    And an empty file named "features/steps/steps.py"
    And a file named "features/issue181_example.feature" with
        """
        Feature:
          Scenario:
            Given I'm using an "undefined step"
        """
    When I run "behave -f plain features/issue181_example.feature"
    Then it should fail with:
        """
        0 steps passed, 0 failed, 0 skipped, 1 undefined
        """
    And the command output should contain:
        """
        You can implement step definitions for undefined steps with these snippets:

        @given(u'I\'m using an "undefined step"')
        def step_impl(context):
            raise NotImplementedError(u'STEP: Given I\'m using an "undefined step"')
        """
