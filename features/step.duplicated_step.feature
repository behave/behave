Feature: Duplicated Step Definitions

  As I tester and test writer
  I want to know when step definitions are duplicated
  So that I can fix these problems.


  Scenario: Duplicated Step in same File
    Given a new working directory
    And a file named "features/steps/alice_steps.py" with:
      """
      from behave import given, when, then

      @given(u'I call Alice')
      def step(context):
          pass

      @given(u'I call Alice')
      def step(context):
          pass
      """
    And a file named "features/duplicated_step_alice.feature" with:
      """
      Feature:
        Scenario: Duplicated Step
          Given I call Alice
      """
    When I run "behave -f plain features/duplicated_step_alice.feature"
    Then it should fail
    And the command output should contain:
        """
        AmbiguousStep: @given('I call Alice') has already been defined in
        existing step @given('I call Alice') at features/steps/alice_steps.py:3
        """
    # -- DISABLED: Python 3.8 traceback line numbers differ w/ decorators (+1).
    # And the command output should contain:
    #    """
    #    File "features/steps/alice_steps.py", line 7, in <module>
    #    """


  Scenario: Duplicated Step Definition in another File
    Given a new working directory
    And a file named "features/steps/bob1_steps.py" with:
      """
      from behave import given

      @given('I call Bob')
      def step_call_bob1(context):
          pass
      """
    And   a file named "features/steps/bob2_steps.py" with:
      """
      from behave import given

      @given('I call Bob')
      def step_call_bob2(context):
          pass
      """
    And a file named "features/duplicated_step_bob.feature" with:
      """
      Feature:
        Scenario: Duplicated Step
          Given I call Bob
      """
    When I run "behave -f plain features/duplicated_step_bob.feature"
    Then it should fail
    And the command output should contain:
        """
        AmbiguousStep: @given('I call Bob') has already been defined in
        existing step @given('I call Bob') at features/steps/bob1_steps.py:3
        """
    # -- DISABLED: Python 3.8 traceback line numbers differ w/ decorators (+1).
    # And the command output should contain:
    #    """
    #    File "features/steps/bob2_steps.py", line 3, in <module>
    #    """


  Scenario: Duplicated Same Step Definition via import from another File

    VERIFY THAT: Duplicated step-detection works.
    Duplicated step-registration occurred through a twice imported step-module:
    First registration may occurs by step-loading the step-module,
    second registration due to import of first step-module.

    The step registry detects that the same step-function should be registered
    another time and ignores it (step is already registered).

    Given a new working directory
    And a file named "features/steps/charly1_steps.py" with:
      """
      from behave import given

      @given('I call Charly')
      def step_call_charly1(context):
          pass
      """
    And   a file named "features/steps/charly2_steps.py" with:
      """
      import charly1_steps
      """
    And a file named "features/duplicated_step_via_import.feature" with:
      """
      Feature:
        Scenario: Duplicated same step via import
          Given I call Charly
      """
    When I run "behave -f plain features/duplicated_step_via_import.feature"
    Then it should pass
    And the command output should not contain:
        """
        AmbiguousStep: @given('I call Charly') has already been defined in
        existing step @given('I call Charly') at features/steps/charly1_steps.py:3
        """
