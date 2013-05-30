@wip
@issue_122
@xfail
Feature: Duplicated Step Definitions

  As I behave user
  I want to know when step definitions are duplicated

  # -- FAILS with pypy ?!?!
  @xfail
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
    And the command output should contain:
        """
        File "{__WORKDIR__}/features/steps/alice_steps.py", line 7, in <module>
        @given(u'I call Alice')
        """

  # -- FAILS on linux w/ cpython2.7 ?!?!
  @xfail
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
      import bob1_steps     # -- ENFORCE: Step registration order.

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
    And the command output should contain:
        """
        File "{__WORKDIR__}/features/steps/bob2_steps.py", line 4, in <module>
        @given(u'I call Bob')
        """
