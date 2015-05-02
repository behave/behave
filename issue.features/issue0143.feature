@issue
Feature: Issue #143: Logging starts with a StreamHandler way too early

  . This verifies that some imported library or other item has not made a
  . call to logging too soon, which would add a StreamHandler.


  @setup
  Scenario: Feature Setup
    Given a new working directory
    And a file named "features/steps/steps.py" with:
        """
        import logging
        from behave import given, when, then, step

        @step('I create {count:n} log records')
        def step_create_log_records(context, count):
            for i in range(count):
                logging.debug('Some debug logging')
        """
    And a file named "features/issue0143_example.feature" with:
        """
        Feature: Logging should not be output unless there is a failure

            Scenario: A passing test
                Given I create 4 log records
        """

  Scenario: Ensure that no log-ouput occurs with enabled log-capture
    Given an empty file named "features/environment.py"
    When I run "behave -f plain --logcapture features/issue0143_example.feature"
    Then it should pass
    And the command output should not contain:
        """
        DEBUG:root:Some debug logging
        """


  Scenario: Ensure that log-ouput occurs with disabled log-capture
    Given a file named "features/environment.py" with:
        """
        import logging

        def before_all(context):
            # -- basicConfig() will not set level if setup is already done.
            logging.basicConfig()
            logging.getLogger().setLevel(logging.DEBUG)
        """
    When I run "behave -f plain --no-logcapture features/issue0143_example.feature"
    Then it should pass
    And the command output should contain:
        """
        DEBUG:root:Some debug logging
        """
