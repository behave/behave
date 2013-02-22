Feature: Duplicated Step Definitions

  As I behave user
  I want to know when step definitions are duplicated

  Background: Test Setup
    Given a new working directory

  Scenario: Duplicated Step in same File
    Given a file named "features/duplicated_step.feature" with:
      """
      Feature: Duplicated Step Definition
        Scenario: Duplicated Step
          Given I call Alice
      """
    And   a file named "features/steps/step1.py" with:
      """
      from behave import given, when, then

      @given(u'I call Alice')
      def step(context):
          pass

      @given(u'I call Alice')
      def step(context):
          pass
      """
    When I run "behave -c -q features/duplicated_step.feature"
    Then it should fail
    And the command output should contain:
        """
        behave.step_registry.AmbiguousStep: "I call Alice" has already been defined
        """

  Scenario: Duplicated Step Definition in another File
    Given a file named "features/duplicated_step.feature" with:
      """
      Feature: Duplicated Step Definition
        Scenario: Duplicated Step
          Given I call Alice
      """
    And   a file named "features/steps/step1.py" with:
      """
      from behave import given, when, then

      @given(u'I call Alice')
      def step(context):
          pass
      """
    And   a file named "features/steps/step2.py" with:
      """
      from behave import given, when, then

      @given(u'I call Alice')
      def step(context):
          pass
      """
    When I run "behave -c -q features/duplicated_step.feature"
    Then it should fail
    And the command output should contain:
        """
        behave.step_registry.AmbiguousStep: "I call Alice" has already been defined
        """
    And the command output should contain:
        """
          File "{__WORKDIR__}/features/steps/step1.py", line 3, in <module>
          @given(u'I call Alice')
        """
