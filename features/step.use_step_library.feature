Feature: Use a step library

    As a tester
    I want to use steps from one or more step libraries
    To simplify the reuse of problem domain specific steps in multiple projects.


  Scenario: Use a simple step library
    Given a new working directory
    And an empty file named "step_library1/__init__.py"
    And a file named "step_library1/alice_steps.py" with:
      """
      from behave import step

      @step('I meet Alice')
      def step_meet_alice(context):
          pass
      """
    And a file named "step_library1/bob_steps.py" with:
      """
      from behave import step

      @step('I meet Bob')
      def step_meet_bob(context):
          pass
      """
    And a file named "features/steps/use_step_library.py" with:
      """
      from step_library1 import alice_steps, bob_steps
      """
    And a file named "features/example_use_step_library.feature" with:
      """
      Feature:
        Scenario:
          Given I meet Alice
          And   I meet Bob
      """
    When I run "behave -f plain features/example_use_step_library.feature"
    Then it should pass with:
        """
        1 feature passed, 0 failed, 0 skipped
        1 scenario passed, 0 failed, 0 skipped
        2 steps passed, 0 failed, 0 skipped, 0 undefined
        """
