Feature: Use logging_filter with logcapture

  PRECONDITION: capture_log mode is enabled (config.capture_log = true).

  As a tester
  In log-capture mode
  I want to include/exclude log-records from some logging categories
  So that the output is not cluttered with unneeded information in case of failures.

    Background:
      Given I define the log record schema:
          | category | level | message         |
          | root     | ERROR | __LOG_MESSAGE__ |

    @setup
    Scenario: Feature Setup
      Given a new working directory
      And a file named "features/steps/use_behave4cmd_steps.py" with:
          """
          import behave4cmd0.log_steps
          import behave4cmd0.failing_steps
          import behave4cmd0.passing_steps
          """
      And a file named "features/logging.failing.feature" with:
          """
          Feature:
            Scenario: Failing
              Given I create log records with:
                  | category | level   | message |
                  | root     |  ERROR  | __LOG_MESSAGE__ |
                  | foo      |  ERROR  | __LOG_MESSAGE__ |
                  | foo.bar  |  ERROR  | __LOG_MESSAGE__ |
                  | bar      |  ERROR  | __LOG_MESSAGE__ |
              When another step fails
          """
      And a file named "behave.ini" with:
          """
          [behave]
          default_format = pretty
          capture_log = true
          logging_level = WARN
          logging_clear_handlers = true
          """


    Scenario: Include only a logging category
      When I run "behave --capture-log --logging-filter=foo features/logging.failing.feature"
      Then it should fail with:
          """
          0 scenarios passed, 1 failed, 0 skipped
          1 step passed, 1 failed, 0 skipped
          """
      And the command output should contain log records from categories:
          | category |
          | foo      |
      But the command output should not contain log records from categories:
          | category | Comment |
          | root     | Not included: filtered-out |
          | foo.bar  | Not included: filtered-out |
          | bar      | Not included: filtered-out |


    Scenario: Include only a logging sub-category
      When I run "behave --logging-filter=foo.bar features/logging.failing.feature"
      Then it should fail
      And the command output should contain log records from categories:
          | category | Comment  |
          | foo.bar  | Included |
      But the command output should not contain log records from categories:
          | category | Comment |
          | root     | Not included: filtered-out |
          | foo      | Not included: filtered-out |
          | bar      | Not included: filtered-out |


    Scenario: Exclude a logging category
      When I run "behave --logging-filter=-foo features/logging.failing.feature"
      Then it should fail
      And the command output should contain log records from categories:
          | category | Comment |
          | root     | Not excluded: foo |
          | foo.bar  | Not excluded: foo |
          | bar      | Not excluded: foo |
      But the command output should not contain log records from categories:
          | category | Comment |
          | foo      | Excluded |


    Scenario: Include several logging categories
      When I run "behave --logging-filter=foo,bar features/logging.failing.feature"
      Then it should fail
      And the command output should contain log records from categories:
          | category | Comment |
          | foo      | Included: foo |
          | bar      | Included: bar |
      But the command output should not contain log records from categories:
          | category | Comment |
          | root     | Not included: filtered-out  |
          | foo.bar  | Not included (sub-category) |


    Scenario: Include/exclude several logging categories
      When I run "behave --logging-filter=foo.bar,-bar features/logging.failing.feature"
      Then it should fail
      And the command output should contain log records from categories:
          | category | Comment |
          | root     | Not excluded: bar |
          | foo      | Not excluded: bar |
          | foo.bar  | Included  |
      But the command output should not contain log records from categories:
          | category | Comment |
          | bar      | Excluded: filtered-out |


    Scenario: Include/exclude several logging categories with configfile
      Given a file named "behave.ini" with:
          """
          [behave]
          capture_log = true
          logging_level = WARN
          logging_filter = foo.bar,-bar
          logging_clear_handlers = true
          """
      When I run "behave features/logging.failing.feature"
      Then it should fail
      And the command output should contain log records from categories:
          | category | Comment |
          | root     | Not excluded: bar |
          | foo      | Not excluded: bar |
          | foo.bar  | Included  |
      But the command output should not contain log records from categories:
          | category | Comment |
          | bar      | Excluded: filtered-out |
