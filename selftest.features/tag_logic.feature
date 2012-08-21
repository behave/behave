# -- BASED-ON: cucumber/features/execute_with_tag_filter.feature
Feature: Tag logic

  In order to conveniently run subsets of features
  As a Cuker
  I want to select features using logical AND/OR of tags

  Scenario: Test Setup
    Given a new working directory
    And a file named "features/steps/steps.py" with:
        """
        from behave import given

        @given(u'passing')
        def step(context):
            pass
        """
    And   a file named "features/tagulicious.feature" with:
      """
      Feature: Sample

        @one @three
        Scenario: Example
          Given passing

        @one
        Scenario: Another Example
          Given passing

        @three
        Scenario: Yet another Example
          Given passing

        @ignore
        Scenario: And yet another Example
          Given passing
      """

  Scenario: ANDing tags
    When I run "behave -c -f plain -t @one -t @three features/tagulicious.feature"
    Then it should pass with:
      """
      1 feature passed, 0 failed, 0 skipped
      1 scenario passed, 0 failed, 3 skipped
      1 step passed, 0 failed, 3 skipped, 0 undefined
      """
    And the command output should contain:
      """
      Feature: Sample
         Scenario: Example
             Given passing ... passed
         Scenario: Another Example
         Scenario: Yet another Example
         Scenario: And yet another Example
      """

  Scenario: ORing tags
    When I run "behave -c -f plain -t @one,@three features/tagulicious.feature"
    Then it should pass with:
        """
        1 feature passed, 0 failed, 0 skipped
        3 scenarios passed, 0 failed, 1 skipped
        3 steps passed, 0 failed, 1 skipped, 0 undefined
        """
    And the command output should contain:
        """
        Feature: Sample
           Scenario: Example
               Given passing ... passed
           Scenario: Another Example
               Given passing ... passed
           Scenario: Yet another Example
               Given passing ... passed
           Scenario: And yet another Example
        """
