Feature: Show missing Step Definitions

  As I behave user
  I want to know which step definitions are missing

  Background: Test Setup
    Given a new working directory
    And   a file named "features/steps/steps.py" with:
      """
      from behave import given, when, then

      @given(u'I do something')
      def step(context):
          pass

      @when(u'I do something')
      def step(context):
          pass
      """

  Scenario: One Missing Step
    Given a file named "features/missing_step.feature" with:
      """
      Feature: Missing Step Definition
        Scenario: Missing Given Step
          Given I do something
          And   I use an unknown step

        Scenario: Missing When Step
          Given I do something
          When  I use an unknown step

        Scenario: Missing Then Step
          Given I do something
          When  I do something
          Then  I use an unknown step
      """
    When I run "behave -c -f plain features/missing_step.feature"
    Then it should fail with:
        """
        You can implement step definitions for undefined steps with these snippets:
        @given(u'I use an unknown step')
        def step(context):
            assert False
        @when(u'I use an unknown step')
        def step(context):
            assert False
        @then(u'I use an unknown step')
        def step(context):
            assert False
        """

  Scenario: Several Missing Steps
    Given a file named "features/missing_step2.feature" with:
      """
      Feature: Missing Step Definition
        BEHAVIOUR: Only first undefined step in a scenario is shown.
        Scenario: Missing Given Step
          Given I use an unknown step
          When  I use an unknown step
      """
    When I run "behave -c -f plain features/missing_step2.feature"
    Then it should fail
    And the command output should contain:
        """
        You can implement step definitions for undefined steps with these snippets:
        @given(u'I use an unknown step')
        def step(context):
            assert False
        """
    But the command output should not contain:
        """
        @when(u'I use an unknown step')
        def step(context):
            assert False
        """

  Scenario: Several Missing Steps2
    Given a file named "features/missing_step3.feature" with:
      """
      Feature: Missing Step Definition2
        BEHAVIOUR: Only first undefined step in a scenario is shown.
        Scenario: Missing Given Step
          Given I do something
          When  I use an unknown step
          Then  I use an unknown step
      """
    When I run "behave -c -f plain features/missing_step3.feature"
    Then it should fail
    And the command output should contain:
        """
        You can implement step definitions for undefined steps with these snippets:
        @when(u'I use an unknown step')
        def step(context):
            assert False
        """
    But the command output should not contain:
        """
        @then(u'I use an unknown step')
        def step(context):
            assert False
        """
