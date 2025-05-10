Feature: Multiline Step Definitions with backslash

  As I tester and test writer
  I want to be able to split steps definitions across multiple lines, using a backslash
  So that I can avoid writing long lines


  # Given
  Scenario: Multiline one step definition Given
    Given a new working directory
    And a file named "features/steps/alice_steps.py" with:
      """
      from behave import given

      @given(u'I call Alice and Bob')
      def step(context):
          pass
      """
    And a file named "features/multiline_one_step_given.feature" with:
      """
      Feature:
        Scenario: Multiline Step Given
          Given I call Alice \
                and Bob
      """
    When I run "behave -f plain features/multiline_one_step_given.feature"
    Then it should pass

  Scenario: Multiline two step definition Given
    Given a new working directory
    And a file named "features/steps/alice_steps.py" with:
      """
      from behave import given

      @given(u'I call Alice and Bob')
      def step(context):
          pass
      """
    And a file named "features/multiline_two_step_given.feature" with:
      """
      Feature:
        Scenario: Multiline Step Given
          Given I call \
                Alice \
                and Bob
      """
    When I run "behave -f plain features/multiline_two_step_given.feature"
    Then it should pass

  Scenario: Multiline three step definition Given
    Given a new working directory
    And a file named "features/steps/alice_steps.py" with:
      """
      from behave import given

      @given(u'I call Alice and Bob')
      def step(context):
          pass
      """
    And a file named "features/multiline_three_step_given.feature" with:
      """
      Feature:
        Scenario: Multiline Step Given
          Given \
                I call \
                Alice \
                and Bob
      """
    When I run "behave -f plain features/multiline_three_step_given.feature"
    Then it should pass

  Scenario: Multiline padded step definition Given
    Given a new working directory
    And a file named "features/steps/alice_steps.py" with:
      """
      from behave import given

      @given(u'I call Alice and Bob')
      def step(context):
          pass
      """
    And a file named "features/multiline_padded_step_given.feature" with:
      """
      Feature:
        Scenario: Multiline Step Given
          Given \
                I call \  
                Alice \	
                and Bob
      """
    When I run "behave -f plain features/multiline_padded_step_given.feature"
    Then it should pass

  # When
  Scenario: Multiline one step definition When
    Given a new working directory
    And a file named "features/steps/alice_steps.py" with:
      """
      from behave import given, when

      @given(u'I call Alice and Bob')
      def step_given(context):
          pass

      @when(u'their phone rings')
      def step_when(context):
          pass
      """
    And a file named "features/multiline_one_step_when.feature" with:
      """
      Feature:
        Scenario: Multiline Step When
          Given I call Alice and Bob
          When their phone \
               rings
      """
    When I run "behave -f plain features/multiline_one_step_when.feature"
    Then it should pass

  Scenario: Multiline two step definition When
    Given a new working directory
    And a file named "features/steps/alice_steps.py" with:
      """
      from behave import given, when

      @given(u'I call Alice and Bob')
      def step_given(context):
          pass

      @when(u'their phone rings')
      def step_when(context):
          pass
      """
    And a file named "features/multiline_two_step_when.feature" with:
      """
      Feature:
        Scenario: Multiline Step When
          Given I call Alice and Bob
          When their \
               phone \
               rings
      """
    When I run "behave -f plain features/multiline_two_step_when.feature"
    Then it should pass

  Scenario: Multiline three step definition When
    Given a new working directory
    And a file named "features/steps/alice_steps.py" with:
      """
      from behave import given, when

      @given(u'I call Alice and Bob')
      def step_given(context):
          pass

      @when(u'their phone rings')
      def step_when(context):
          pass
      """
    And a file named "features/multiline_three_step_when.feature" with:
      """
      Feature:
        Scenario: Multiline Step When
          Given I call Alice and Bob
          When \
               their \
               phone \
               rings
      """
    When I run "behave -f plain features/multiline_three_step_when.feature"
    Then it should pass

  # Then
  Scenario: Multiline one step definition Then
    Given a new working directory
    And a file named "features/steps/alice_steps.py" with:
      """
      from behave import given, then

      @given(u'I call Alice and Bob')
      def step_given(context):
          pass

      @then(u'their phone rings')
      def step_then(context):
          pass
      """
    And a file named "features/multiline_one_step_then.feature" with:
      """
      Feature:
        Scenario: Multiline Step Then
          Given I call Alice and Bob
          Then their phone \
               rings
      """
    When I run "behave -f plain features/multiline_one_step_then.feature"
    Then it should pass

  Scenario: Multiline two step definition Then
    Given a new working directory
    And a file named "features/steps/alice_steps.py" with:
      """
      from behave import given, then

      @given(u'I call Alice and Bob')
      def step_given(context):
          pass

      @then(u'their phone rings')
      def step_then(context):
          pass
      """
    And a file named "features/multiline_two_step_then.feature" with:
      """
      Feature:
        Scenario: Multiline Step Then
          Given I call Alice and Bob
          Then their \
               phone \
               rings
      """
    When I run "behave -f plain features/multiline_two_step_then.feature"
    Then it should pass

  Scenario: Multiline three step definition Then
    Given a new working directory
    And a file named "features/steps/alice_steps.py" with:
      """
      from behave import given, then

      @given(u'I call Alice and Bob')
      def step_given(context):
          pass

      @then(u'their phone rings')
      def step_then(context):
          pass
      """
    And a file named "features/multiline_three_step_then.feature" with:
      """
      Feature:
        Scenario: Multiline Step Then
          Given I call Alice and Bob
          Then \
               their \
               phone \
               rings
      """
    When I run "behave -f plain features/multiline_three_step_then.feature"
    Then it should pass

  # And
  Scenario: Multiline one step definition And
    Given a new working directory
    And a file named "features/steps/alice_steps.py" with:
      """
      from behave import given

      @given(u'I call Alice and Bob')
      def step_given(context):
          pass

      @given(u'their phone rings')
      def step_given(context):
          pass
      """
    And a file named "features/multiline_one_step_and.feature" with:
      """
      Feature:
        Scenario: Multiline Step And
          Given I call Alice and Bob
          And their phone \
               rings
      """
    When I run "behave -f plain features/multiline_one_step_and.feature"
    Then it should pass

  Scenario: Multiline two step definition And
    Given a new working directory
    And a file named "features/steps/alice_steps.py" with:
      """
      from behave import given

      @given(u'I call Alice and Bob')
      def step_given(context):
          pass

      @given(u'their phone rings')
      def step_given(context):
          pass
      """
    And a file named "features/multiline_two_step_and.feature" with:
      """
      Feature:
        Scenario: Multiline Step And
          Given I call Alice and Bob
          And their \
               phone \
               rings
      """
    When I run "behave -f plain features/multiline_two_step_and.feature"
    Then it should pass

  Scenario: Multiline three step definition And
    Given a new working directory
    And a file named "features/steps/alice_steps.py" with:
      """
      from behave import given

      @given(u'I call Alice and Bob')
      def step_given(context):
          pass

      @given(u'their phone rings')
      def step_given(context):
          pass
      """
    And a file named "features/multiline_three_step_and.feature" with:
      """
      Feature:
        Scenario: Multiline Step And
          Given I call Alice and Bob
          And \
               their \
               phone \
               rings
      """
    When I run "behave -f plain features/multiline_three_step_and.feature"
    Then it should pass

  # Feature
  Scenario: Multiline invalid step definition Feature
    Given a new working directory
    And a file named "features/steps/alice_steps.py" with:
      """
      from behave import given

      @given(u'I call Alice and Bob')
      def step_given(context):
          pass
      """
    And a file named "features/multiline_invalid_feature.feature" with:
      """
      Feature: \
        Scenario: Multiline Feature
        Given I call Alice and Bob
      """
    When I run "behave -f plain features/multiline_invalid_feature.feature"
    Then it should fail with:
      """
      Backslash escape invalid in state
      """

  # Scenario
  Scenario: Multiline invalid step definition Scenario
    Given a new working directory
    And a file named "features/steps/alice_steps.py" with:
      """
      from behave import given

      @given(u'I call Alice and Bob')
      def step_given(context):
          pass
      """
    And a file named "features/multiline_invalid_scenario.feature" with:
      """
      Feature:
        Scenario: \
          Multiline Scenario
        Given I call Alice and Bob
      """
    When I run "behave -f plain features/multiline_invalid_scenario.feature"
    Then it should fail with:
      """
      Backslash escape invalid in state
      """
