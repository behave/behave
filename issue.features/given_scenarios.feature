@feature_request
@issue
Feature: Issue #XXX: Back reference features as givens

  In some cases features and scenarios naturally build on each other,
  e.g. logging in as an admin is one scenario, creating a user
  involves logging in as an admin and then doing something
  else. Creating a business object involves creating an admin and
  creating a user and so on.

  In order to DRY out the Gherkin for this and avoid steps which
  duplicate the steps in a seperate place, allow users to write Given
  steps which reference a previous scenario and executes those steps

  Background:
    Given a new working directory
    And a file named "features/steps/steps.py" with:
        """
        from behave import step

        @step('step {count}')
        def a_step(context, count):
            print ('step %s' % count)
        """
        
    And a file named "features/given_scenario.feature" with
        """
        Feature:
          
          Scenario: Scenario 1
            Given step 1
            When step 2
            Then step 3

          Scenario: Scenario 2
            Given Scenario 1
            Then step 4
        """

  
  Scenario: Refer to previous scenario
    When I run "behave -c -f plain --no-capture features/given_scenario.feature"
    Then it should pass with
    """
    Scenario: Scenario 1
      step 1
          Given step 1 ... passed
      step 2
          When step 2 ... passed
      step 3
          Then step 3 ... passed
    Scenario: Scenario 2
      step 1
      step 2
      step 3
          Given Scenario 1 ... passed
      step 4
          Then step 4 ... passed
    """
