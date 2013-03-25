@issue
Feature: Issue #143: Logging starts with a StreamHandler way too early

    | This verifies that some imported library or other item has not made a
    | call to logging too soon, which would add a StreamHandler.

  Scenario:
    Given a file named "features/steps/steps.py" with:
        """
        import logging
        from behave import given, when, then, step

        @step('I log debug {num} times')
        def log_output(context, num):
            for i in xrange(int(num)):
                logging.debug('Some debug logging')
        """
    And a file named "features/issue0143_example.feature" with:
        """
        Feature: Logging should not be output unless there is a failure

            Scenario: A passing test
                Given I log debug 100 times
        """
    When I run "behave -f plain features/issue0143_example.feature"
    Then it should pass
    And the command output should not contain:
        """
        DEBUG:root:Some debug logging
        """

