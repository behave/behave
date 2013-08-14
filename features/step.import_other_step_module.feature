Feature: Ensure that a step module can import another step module

  As a test writer
  I want to import step definitions from another module in a step module
  So that I can reuse other steps and call them directly.

  | When a step module imports another step module
  | this should not cause AmbiguousStep errors
  | due to duplicated registration of the same step functions.
  |
  | NOTES:
  |   * In general you should avoid this case (provided as example here).
  |   * Use "context.execute_steps(...)" to avoid importing other step modules
  |   * Use step-libraries; this will in general use sane imports of other step modules


  Scenario: Step module that imports another step module
    Given a new working directory
    And a file named "features/steps/alice1_steps.py" with:
      """
      from behave import given

      @given(u'I call Alice')
      def step_call_alice(context):
          pass
      """
    And   a file named "features/steps/bob1_steps.py" with:
      """
      from behave import given
      from alice1_steps import step_call_alice

      @given(u'I call Bob')
      def step_call_bob(context):
          pass

      @given(u'I call Bob and Alice')
      def step_call_bob_and_alice(context):
          step_call_bob(context)
          step_call_alice(context)
      """
    And a file named "features/example.import_step_module.feature" with:
      """
      Feature:
        Scenario:
          Given I call Bob and Alice
      """
    When I run "behave -f plain --no-timings features/example.import_step_module.feature"
    Then it should pass with:
        """
        1 scenario passed, 0 failed, 0 skipped
        1 step passed, 0 failed, 0 skipped, 0 undefined
        """
    And the command output should contain:
        """
        Feature:
            Scenario:
              Given I call Bob and Alice ... passed
        """


  Scenario: Step module that imports another step module (cross-wise)
    Given a new working directory
    And a file named "features/steps/alice2_steps.py" with:
      """
      from behave import given
      import bob2_steps     # -- BAD: Import other step module, cross-wise.

      @given(u'I call Alice')
      def step_call_alice(context):
          pass
      """
    And   a file named "features/steps/bob2_steps.py" with:
      """
      from behave import given
      import alice2_steps     # -- BAD: Import other step module, cross-wise.

      @given(u'I call Bob')
      def step_call_bob(context):
          pass
      """
    And a file named "features/example.cross_imported_step_modules.feature" with:
      """
      Feature:
        Scenario:
          Given I call Alice
          And   I call Bob
      """
    When I run "behave -f plain --no-timings features/example.cross_imported_step_modules.feature"
    Then it should pass with:
        """
        1 feature passed, 0 failed, 0 skipped
        1 scenario passed, 0 failed, 0 skipped
        2 steps passed, 0 failed, 0 skipped, 0 undefined
        """
    And the command output should contain:
        """
        Feature:
            Scenario:
              Given I call Alice ... passed
              And I call Bob ... passed
        """


