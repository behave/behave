Feature: Execute Steps within a Step Function (Nested Steps)

    As a tester
    I want to reuse existing steps and call several ones within another step
    So that I can comply with the the DRY principle.

  Scenario: Execute a number of simple steps (GOOD CASE)
    Given a new working directory
    And   a file named "features/steps/steps.py" with:
      """
      from behave import given, when, then

      @given(u'I go to the supermarket')
      def step_given_I_go_to_the_supermarket(context):
          context.shopping_cart = {}

      @when(u'I buy {amount:n} {item:w}')
      def step_when_I_buy(context, amount, item):
          assert amount >= 0
          if not context.shopping_cart.has_key(item):
              context.shopping_cart[item] = 0
          context.shopping_cart[item] += amount

      # -- HERE: Is the interesting functionality.
      @when(u'I buy the usual things')
      def step_when_I_buy_the_usual_things(context):
          context.execute_steps(u'''
              When I buy 2 apples
              And  I buy 3 bananas
          ''')

      @then(u'I have {amount:n} {item:w}')
      def step_then_I_have(context, amount, item):
          actual = context.shopping_cart.get(item, 0)
          assert amount == actual
      """
    And   a file named "features/use_nested_steps.feature" with:
      """
      Feature:
        Scenario:
          Given I go to the supermarket
          When  I buy the usual things
          Then  I have 2 apples
          And   I have 3 bananas
      """
    When I run "behave -f plain features/use_nested_steps.feature"
    Then it should pass with:
      """
      1 feature passed, 0 failed, 0 skipped
      1 scenario passed, 0 failed, 0 skipped
      4 steps passed, 0 failed, 0 skipped, 0 undefined
      """

  @not_implemented
  Scenario: A Nested Step Fails with Assert

  @not_implemented
  Scenario: A Nested Step Fails with Exception

