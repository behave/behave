@issue
Feature: Issue #35 Plain Formatter shows wrong steps when tag-selection is used

  Background: Test Setup
    Given a new working directory
    And a file named "features/steps/steps.py" with:
      """
      from behave import given, when, then

      @given(u'the ninja has a third level black-belt')
      def step(context):
          pass

      @when(u'attacked by {opponent}')
      def step(context, opponent):
          pass

      @then(u'the ninja should {reaction}')
      def step(context, reaction):
          pass
      """
    And a file named "features/issue35_1.feature" with:
      """
      Feature: Using Tags with Features and Scenarios

        @one
        Scenario: Weaker opponent
            Given the ninja has a third level black-belt
            When attacked by a samurai
            Then the ninja should engage the opponent

        @two
        Scenario: Stronger opponent
            Given the ninja has a third level black-belt
            When attacked by Chuck Norris
            Then the ninja should run for his life
      """

  Scenario: Select First Scenario with Tag
    When I run "behave --no-timings -f plain --tags=@one features/issue35_1.feature"
    Then it should pass with:
      """
      1 feature passed, 0 failed, 0 skipped
      1 scenario passed, 0 failed, 1 skipped
      3 steps passed, 0 failed, 3 skipped, 0 undefined
      """
    And the command output should contain:
      """
      Feature: Using Tags with Features and Scenarios
         Scenario: Weaker opponent
             Given the ninja has a third level black-belt ... passed
              When attacked by a samurai ... passed
              Then the ninja should engage the opponent ... passed
         Scenario: Stronger opponent
      """

  Scenario: Select Second Scenario with Tag
    When I run "behave --no-timings -f plain --tags=@two features/issue35_1.feature"
    Then it should pass with:
      """
      1 feature passed, 0 failed, 0 skipped
      1 scenario passed, 0 failed, 1 skipped
      3 steps passed, 0 failed, 3 skipped, 0 undefined
      """
    And the command output should contain:
      """
      Feature: Using Tags with Features and Scenarios
         Scenario: Weaker opponent
         Scenario: Stronger opponent
             Given the ninja has a third level black-belt ... passed
              When attacked by Chuck Norris ... passed
              Then the ninja should run for his life ... passed
      """

