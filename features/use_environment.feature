Feature: Use Alternate Environment Setup

  As I tester and test writer
  I want to run the same step implementations against different environments
  So I can verify UAT, Staging and Production using the same tests.

  . CONCEPT: TEST ENVIRONMENT
  .   A test environment allows you to use different environment setups
  .   so that urls and other inputs can be set for each environment.
  .
  .   Examples for test environments are:
  .     * development (using local urls and data)
  .     * production
  .     * UAT
  .     * Staging
  .     * ...
  .
  .
  . EXAMPLE DIRECTORY LAYOUT (with default environment and environment=staging):
  .
  .   features/
  .       +-- steps/                # -- Step implementations for all environments..
  .       |   +-- foo_steps.py
  .       +-- *.feature
  .       +-- environment.py          # -- Environment for default environment.
  .       +-- staging_environment.py  # -- Environment for environment=staging.


  @setup
  Scenario: Feature Setup
    Given a new working directory
      And a file named "features/example1.feature" with:
        """
        Feature:
          Scenario:
            Given I do something in a staging environment
        """
      And a file named "features/environment.py" with:
        """
        def before_all(context):
            context.use_staging_environment = False
        """
      And a file named "features/steps/foo_steps.py" with:
        """
        from behave import step

        @step('I do something in a staging environment')
        def step_do_something(context):
            if context.config.environment == 'staging':
                assert context.use_staging_environment
            else:
                assert not context.use_staging_environment
        """
      And I remove the environment variable "BEHAVE_ENVIRONMENT"

  Scenario: Use environment=staging
    Given a file named "features/staging_environment.py" with:
        """
        def before_all(context):
            context.use_staging_environment = True
        """

    When I run "behave -c --environment=staging features/example1.feature"
    Then it should pass with:
        """
        1 feature passed, 0 failed, 0 skipped
        1 scenario passed, 0 failed, 0 skipped
        1 step passed, 0 failed, 0 skipped, 0 undefined
        """
    And the command output should contain:
        """
        Scenario:                                       # features/example1.feature:2
          Given I do something in a staging environment # features/steps/foo_steps.py:3
        """

  Scenario: Use default environment
    Given I remove the environment variable "BEHAVE_ENVIRONMENT"
     When I run "behave -c features/example1.feature"
     Then it should pass with:
        """
        1 feature passed, 0 failed, 0 skipped
        1 scenario passed, 0 failed, 0 skipped
        1 step passed, 0 failed, 0 skipped, 0 undefined
        """
    And the command output should contain:
        """
        Scenario:                                       # features/example1.feature:2
          Given I do something in a staging environment # features/steps/foo_steps.py:3
        """

  Scenario: Use the BEHAVE_ENVIRONMENT environment variable to define the staging environment
    Given I set the environment variable "BEHAVE_ENVIRONMENT" to "staging"
    When I run "behave -c features/example1.feature"
    Then it should pass with:
        """
        1 feature passed, 0 failed, 0 skipped
        1 scenario passed, 0 failed, 0 skipped
        1 step passed, 0 failed, 0 skipped, 0 undefined
        """
    And the command output should contain:
        """
        Scenario:                                       # features/example1.feature:2
          Given I do something in a staging environment # features/steps/foo_steps.py:3
        """
    But note that "I should better remove it again (TEARDOWN PHASE)"
    And I remove the environment variable "BEHAVE_ENVIRONMENT"


  Scenario: Using an unknown environment
    When I run "behave -c --environment=unknown features/example1.feature"
    Then it should fail with:
        """
        ConfigError: No environemnt file "unknown_environment.py"
        """
