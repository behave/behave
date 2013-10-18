@logging
@no_capture
Feature: No-logcapture mode (normal mode) shows log-records

  As a tester
  I want that sometimes that log output is not captured
  So that I can see progress even in case of success (or failures)


  @setup
  Scenario: Feature Setup
    Given a new working directory
    And a file named "features/steps/use_behave4cmd_steps.py" with:
        """
        import behave4cmd0.log.steps
        import behave4cmd0.failing_steps
        import behave4cmd0.passing_steps
        """


    Scenario: Log records are shown when scenario passes (CASE 1)

      Ensure that log-records are filtered out if log_record.level is too low.

        Given a file named "features/environment.py" with:
            """
            def before_all(context):
                import logging
                context.config.setup_logging(logging.WARN)
                # -- SAME AS:
                # logging.basicConfig()
                # logging.getLogger().setLevel(logging.WARN)
            """
        And a file named "features/logging.passing_example.feature" with:
            """
            Feature:
              Scenario: Passing
                Given I create log records with:
                    | category | level   | message |
                    | root     |  ERROR  | Hello Alice  |
                    | root     |  WARN   | Hello Bob    |
                    | root     |  INFO   | Hello Charly |
                    | root     |  DEBUG  | Hello Doro   |
                When another step passes
            """
        When I run "behave -f plain -T --no-logcapture features/logging.passing_example.feature"
        Then it should pass
        And the command output should contain the following log records:
            | category | level   | message |
            | root     |  ERROR  | Hello Alice  |
            | root     |  WARN   | Hello Bob    |
        But the command output should not contain the following log records:
            | category | level   | message      | Comment |
            | root     |  INFO   | Hello Charly | Filtered-out |
            | root     |  DEBUG  | Hello Doro   | Filtered-out |
        And note that "log_records with level below WARN are filtered out"


    @no_capture
    Scenario: Log records are shown up to first failing step (CASE 2)

      Ensure that log-records are filtered out if log_record.level is too low.

        Given a file named "features/environment.py" with:
            """
            def before_all(context):
                context.config.setup_logging()
            """
        And a file named "features/logging.failing_example.feature" with:
            """
            Feature:
              Scenario: Failing
                Given I create log records with:
                    | category | level   | message |
                    | root     |  ERROR  | Hello Alice  |
                    | root     |  WARN   | Hello Bob    |
                    | root     |  INFO   | Hello Charly |
                    | root     |  DEBUG  | Hello Doro   |
                When another step fails
                Then I create log records with:
                    | category | level   | message |
                    | root     |  ERROR  | Hello2 Zerberus |
            """
        When I run "behave -f plain -T --no-logcapture --logging-level=ERROR features/logging.failing_example.feature"
        Then it should fail with:
            """
            0 scenarios passed, 1 failed, 0 skipped
            1 step passed, 1 failed, 1 skipped, 0 undefined
            """
        And the command output should contain the following log records:
            | category | level   | message |
            | root     |  ERROR  | Hello Alice  |
        But the command output should not contain the following log records:
            | category | level   | message         | Comment |
            | root     |  WARN   | Hello Bob       | Filtered-out |
            | root     |  INFO   | Hello Charly    | Filtered-out |
            | root     |  DEBUG  | Hello Doro      | Filtered-out |
            | root     |  ERROR  | Hello2 Zerberus | Skipped      |
        And note that "log_records with level below ERROR are filtered out"
