Feature: Use Alternate Step Implementations for Each Test Stage

  As I tester and test writer
  I want to run the same feature with other step implementations during different testing stages
  So I can run quick checks in a development environment and detailed checks in a testlab.

  . CONCEPT: TEST STAGE
  .   A test stage allows you to use different step/environment implementations
  .   compared to other test stage or the default, unnamed test stage.
  .
  .   Examples for test stages are:
  .     * develop (using the development environment with more diagnostics)
  .     * product (using the product database, ...)
  .     * systemtest
  .     * systemint (system integration)
  .     * ...
  .
  .   NOTE:
  .   Test stages can be used to adapt to different test environments
  .   while using these test stages.
  .
  .
  . EXAMPLE DIRECTORY LAYOUT (with default stage and stage=testlab):
  .
  .   features/
  .       +-- steps/                # -- Step implementations for default stage.
  .       |   +-- foo_steps.py
  .       +-- testlab_steps/        # -- Step implementations for stage=testlab.
  .       |   +-- foo_steps.py
  .       +-- *.feature
  .       +-- environment.py          # -- Environment for default stage.
  .       +-- testlab_environment.py  # -- Environment for stage=testlab.


  @setup
  Scenario: Feature Setup
    Given a new working directory
      And a file named "features/example1.feature" with:
        """
        Feature:
          Scenario:
            Given I do something in a test stage
        """
      And a file named "features/environment.py" with:
        """
        def before_all(context):
            context.use_develop_environment = False
        """
      And a file named "features/steps/foo_steps.py" with:
        """
        from behave import step

        @step('I do something in a test stage')
        def step_do_something(context):
            assert not context.config.stage
            assert not context.use_develop_environment
        """
      And I remove the environment variable "BEHAVE_STAGE"

  Scenario: Use stage=develop
    Given a file named "features/develop_environment.py" with:
        """
        def before_all(context):
            context.use_develop_environment = True
        """
    And a file named "features/develop_steps/foo_steps.py" with:
        """
        from behave import step

        @step('I do something in a test stage')
        def step_do_something(context):
            assert context.config.stage == "develop"
            assert context.use_develop_environment
        """
    When I run "behave -c --stage=develop features/example1.feature"
    Then it should pass with:
        """
        1 feature passed, 0 failed, 0 skipped
        1 scenario passed, 0 failed, 0 skipped
        1 step passed, 0 failed, 0 skipped, 0 undefined
        """
    And the command output should contain:
        """
        Scenario:                              # features/example1.feature:2
          Given I do something in a test stage # features/develop_steps/foo_steps.py:3
        """

  Scenario: Use default stage
    Given I remove the environment variable "BEHAVE_STAGE"
     When I run "behave -c features/example1.feature"
     Then it should pass with:
        """
        1 feature passed, 0 failed, 0 skipped
        1 scenario passed, 0 failed, 0 skipped
        1 step passed, 0 failed, 0 skipped, 0 undefined
        """
    And the command output should contain:
        """
        Scenario:                              # features/example1.feature:2
          Given I do something in a test stage # features/steps/foo_steps.py:3
        """

  Scenario: Use the BEHAVE_STAGE environment variable to define the test stage
    Given I set the environment variable "BEHAVE_STAGE" to "develop"
    When I run "behave -c features/example1.feature"
    Then it should pass with:
        """
        1 feature passed, 0 failed, 0 skipped
        1 scenario passed, 0 failed, 0 skipped
        1 step passed, 0 failed, 0 skipped, 0 undefined
        """
    And the command output should contain:
        """
        Scenario:                              # features/example1.feature:2
          Given I do something in a test stage # features/develop_steps/foo_steps.py:3
        """
    But note that "I should better remove it again (TEARDOWN PHASE)"
    And I remove the environment variable "BEHAVE_STAGE"


  Scenario: Using an unknown stage
    When I run "behave -c --stage=unknown features/example1.feature"
    Then it should fail with:
        """
        ConfigError: No unknown_steps directory
        """
