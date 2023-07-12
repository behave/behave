@issue
Feature: Issue #1120 -- Logging ignoring level set in setup_logging

  . DESCRIPTION OF SYNDROME (OBSERVED BEHAVIOR):
  .  * I setup logging-level in "before_all()" hook w/ context.config.setup_logging()
  .  * I use logging in "after_scenario()" hook
  .  * Even levels below "logging.WARNING" are shown

  Background: Setup
    Given a new working directory
    And a file named "features/steps/use_step_library.py" with:
      """
      import behave4cmd0.passing_steps
      import behave4cmd0.failing_steps
      """
    And a file named "features/simple.feature" with:
      """
      Feature: F1
        Scenario: S1
          Given a step passes
          When another step passes
      """

  Scenario: Check Syndrome
    Given a file named "features/environment.py" with:
      """
      from __future__ import absolute_import, print_function
      import logging
      from behave.log_capture import capture

      def before_all(context):
          context.config.setup_logging(logging.WARNING)

      @capture
      def after_scenario(context, scenario):
          logging.debug("THIS_LOG_MESSAGE::debug")
          logging.info("THIS_LOG_MESSAGE::info")
          logging.warning("THIS_LOG_MESSAGE::warning")
          logging.error("THIS_LOG_MESSAGE::error")
          logging.critical("THIS_LOG_MESSAGE::critical")
      """
    When I run "behave features/simple.feature"
    Then it should pass with:
      """
      1 feature passed, 0 failed, 0 skipped
      """
    And the command output should contain "THIS_LOG_MESSAGE::critical"
    And the command output should contain "THIS_LOG_MESSAGE::error"
    And the command output should contain "THIS_LOG_MESSAGE::warning"
    But the command output should not contain "THIS_LOG_MESSAGE::debug"
    And the command output should not contain "THIS_LOG_MESSAGE::info"


  Scenario: Workaround for Syndrome (works without fix)
    Given a file named "features/environment.py" with:
      """
      from __future__ import absolute_import, print_function
      import logging
      from behave.log_capture import capture

      def before_all(context):
          # -- HINT: Use behave.config.logging_level from config-file
          context.config.setup_logging()

      @capture
      def after_scenario(context, scenario):
          logging.debug("THIS_LOG_MESSAGE::debug")
          logging.info("THIS_LOG_MESSAGE::info")
          logging.warning("THIS_LOG_MESSAGE::warning")
          logging.error("THIS_LOG_MESSAGE::error")
          logging.critical("THIS_LOG_MESSAGE::critical")
      """
    And a file named "behave.ini" with:
      """
      [behave]
      logging_level = WARNING
      """
    When I run "behave features/simple.feature"
    Then it should pass with:
      """
      1 feature passed, 0 failed, 0 skipped
      """
    And the command output should contain "THIS_LOG_MESSAGE::critical"
    And the command output should contain "THIS_LOG_MESSAGE::error"
    And the command output should contain "THIS_LOG_MESSAGE::warning"
    But the command output should not contain "THIS_LOG_MESSAGE::debug"
    And the command output should not contain "THIS_LOG_MESSAGE::info"
