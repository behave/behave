Feature: Setup logging_level

  As a tester
  I want to configure the logging_level for --logcapture mode
  So that I see only the important log-records when a scenario fails.

  As a tester
  I want to configure the logging_level for --nologcapture mode
  So that I see only the important log-records up to this level.

  | SPECIFICATION:
  |  * logging_level can be defined on command-line
  |  * logging_level can be defined in behave configuration file
  |  * logging_level should be applied in before_all() hook in --nologcapture mode


  @setup
  Scenario: Feature Setup
    Given a new working directory
    And a file named "features/steps/use_behave4cmd_steps.py" with:
        """
        import behave4cmd0.log.steps
        import behave4cmd0.failing_steps
        import behave4cmd0.passing_steps
        """
    And a file named "features/environment.py" with:
        """
        def before_all(context):
            context.config.setup_logging()
        """
    And  a file named "features/example.log_with_failure.feature" with:
        """
        Feature:
          Scenario: S1
            Given I create log records with:
                | category | level   | message |
                | root     |  ERROR  | Hello1 log-error-record |
                | root     |  WARN   | Hello1 log-warn-record  |
                | root     |  INFO   | Hello1 log-info-record  |
                | root     |  DEBUG  | Hello1 log-debug-record |
            When a step fails
        """
    And  a file named "features/example.log_with_pass.feature" with:
        """
        Feature:
          Scenario: S2
            Given I create log records with:
                | category | level   | message |
                | root     |  ERROR  | Hello2 log-error-record |
                | root     |  WARN   | Hello2 log-warn-record  |
                | root     |  INFO   | Hello2 log-info-record  |
                | root     |  DEBUG  | Hello2 log-debug-record |
            When a step passes
        """

  @capture
  Scenario: Logcapture mode: Use logging_level on command-line

    Also ensure that command-line option can override configuration file info.

    Given a file named "behave.ini" with:
        """
        [behave]
        logging_level = INFO
        """
    When I run "behave -f plain -T --logging-level=WARN features/"
    Then it should fail with:
        """
        1 scenario passed, 1 failed, 0 skipped
        3 steps passed, 1 failed, 0 skipped, 0 undefined
        """
    And the command output should contain:
        """
        Captured logging:
        ERROR:root:Hello1 log-error-record
        WARNING:root:Hello1 log-warn-record
        """
    But the command output should not contain the following log records:
        | category | level   | message                 | Comment |
        | root     |  INFO   | Hello1 log-info-record  | Log-level too low |
        | root     |  DEBUG  | Hello1 log-debug-record | Log-level too low |
        | root     |  ERROR  | Hello2 log-error-record | Scenario passes, capture log is suppressed |
        | root     |  WARN   | Hello2 log-warn-record  | Scenario passes, capture log is suppressed |
        | root     |  INFO   | Hello2 log-info-record  | Scenario passes, capture log is suppressed |
        | root     |  DEBUG  | Hello2 log-debug-record | Scenario passes, capture log is suppressed |


  @capture
  Scenario: Logcapture mode: Use logging_level in configuration file
    Given a file named "behave.ini" with:
        """
        [behave]
        logging_level = ERROR
        """
    When I run "behave -f plain -T features/"
    Then it should fail with:
        """
        1 scenario passed, 1 failed, 0 skipped
        3 steps passed, 1 failed, 0 skipped, 0 undefined
        """
    And the command output should contain:
        """
        Captured logging:
        ERROR:root:Hello1 log-error-record
        """
    But the command output should not contain the following log records:
        | category | level   | message                 | Comment |
        | root     |  WARN   | Hello1 log-warn-record  | Log-level too low |
        | root     |  INFO   | Hello1 log-info-record  | Log-level too low |
        | root     |  DEBUG  | Hello1 log-debug-record | Log-level too low |
        | root     |  ERROR  | Hello2 log-error-record | Scenario passes |
        | root     |  WARN   | Hello2 log-warn-record  | Scenario passes |
        | root     |  INFO   | Hello2 log-info-record  | Scenario passes |
        | root     |  DEBUG  | Hello2 log-debug-record | Scenario passes |


  @no_capture
  Scenario: Normal mode: Use logging_level on command-line
    Given a file named "behave.ini" with:
        """
        [behave]
        logging_level = INFO
        """
    When I run "behave -f plain -T --logging-level=WARN --no-logcapture features/"
    Then it should fail with:
        """
        1 scenario passed, 1 failed, 0 skipped
        3 steps passed, 1 failed, 0 skipped, 0 undefined
        """
    And the command output should contain the following log records:
        | category | level   | message |
        | root     |  ERROR  | Hello1 log-error-record |
        | root     |  WARN   | Hello1 log-warn-record  |
        | root     |  ERROR  | Hello2 log-error-record |
        | root     |  WARN   | Hello2 log-warn-record  |
    But the command output should not contain the following log records:
        | category | level   | message                 | Comment |
        | root     |  INFO   | Hello1 log-info-record  | Log-level too low |
        | root     |  DEBUG  | Hello1 log-debug-record | Same reason |
        | root     |  INFO   | Hello2 log-info-record  | Same reason |
        | root     |  DEBUG  | Hello2 log-debug-record | Same reason |

  @no_capture
  Scenario: Normal mode: Use logging_level in configuration file
    Given a file named "behave.ini" with:
        """
        [behave]
        log_capture = false
        logging_level = ERROR
        """
      When I run "behave -f plain -T features/"
      Then it should fail with:
        """
        1 scenario passed, 1 failed, 0 skipped
        3 steps passed, 1 failed, 0 skipped, 0 undefined
        """
    And the command output should contain the following log records:
        | category | level   | message |
        | root     |  ERROR  | Hello1 log-error-record |
        | root     |  ERROR  | Hello2 log-error-record |
    But the command output should not contain the following log records:
        | category | level   | message                 | Comment |
        | root     |  WARN   | Hello1 log-warn-record  | Log-level too low |
        | root     |  INFO   | Hello1 log-info-record  | Same reason |
        | root     |  DEBUG  | Hello1 log-debug-record | Same reason |
        | root     |  WARN   | Hello2 log-warn-record  | Same reason |
        | root     |  INFO   | Hello2 log-info-record  | Same reason |
        | root     |  DEBUG  | Hello2 log-debug-record | Same reason |
