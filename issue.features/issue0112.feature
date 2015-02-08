@issue
@change_request
Feature: Issue #112: Improvement to AmbiguousStep error

    . AmbiguousStep could be more useful if it also showed the existing string
    . with which the new one is clashing. This is particularly useful
    . if using step parameters.


  Background:
    Given a new working directory
    And   a file named "features/syndrome112.feature" with:
        """
        Feature:
          Scenario:
            Given I buy 10 oranges
        """

  Scenario: Good step ordering -- From specific to generic regular expression
    Given a file named "features/steps/good_steps.py" with:
        """
        from behave import given, when, then

        # -- ORDERING-IMPORTANT: From more specific steps to less specific.
        @given(u'I buy {number:n} {items:w}')
        def step_given_I_buy2(context, number, items):
            pass

        # -- OTHERWISE: Generic step matches all other patterns.
        @given(u'I buy {amount} {product}')
        def step_given_I_buy(context, amount, product):
            pass
        """
    When I run "behave -c features/syndrome112.feature"
    Then it should pass with:
        """
        1 feature passed, 0 failed, 0 skipped
        1 scenario passed, 0 failed, 0 skipped
        1 step passed, 0 failed, 0 skipped, 0 undefined
        """


  Scenario: Bad step ordering causes AmbiguousStep
    Given a file named "features/steps/bad_steps.py" with:
        """
        from behave import given, when, then

        # -- ORDERING-VIOLATED: Generic step comes first.
        @given(u'I buy {amount} {product}')
        def step_given_I_buy(context, amount, product):
            pass

        # -- AMBIGUOUS-STEP: Will occur here.
        @given(u'I buy {number:n} {items:w}')
        def step_given_I_buy2(context, number, items):
            pass
        """
    When I run "behave -c features/syndrome112.feature"
    Then it should fail
    And the command output should contain:
        """
        AmbiguousStep: @given('I buy {number:n} {items:w}') has already been defined in
          existing step @given('I buy {amount} {product}') at features/steps/bad_steps.py:4
        """
