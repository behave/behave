Feature: Execute class-based steps with inheritance (Nested Steps)

    As a tester
    I want to reuse existing steps as class methods
    So that I can comply with the the DRY principle.

  Background:
    Given a new working directory
    And   a file named "features/steps/base_steps.py" with:
    """
    from behave.step_registry import local_step_registry

    Base = local_step_registry()
    class SomeSteps(Base):
        @Base.given(u'I go to the supermarket')
        def step_given_I_go_to_the_supermarket(self):
            self.context.shopping_cart = {}

        @Base.when(u'I buy {amount:n} {item:w}')
        def step_when_I_buy(self, amount, item):
            assert amount >= 0
            if not item in self.context.shopping_cart:
                self.context.shopping_cart[item] = 0
            self.context.shopping_cart[item] += amount

        @Base.when(u'I buy the usual things')
        def step_when_I_buy_the_usual_things(self):
            self.step_when_I_buy(2, 'apples')
            self.step_when_I_buy(3, 'bananas')

        @Base.then(u'I have {amount:n} {item:w}')
        def step_then_I_have(self, amount, item):
            actual = self.context.shopping_cart.get(item, 0)
            assert amount == actual
    """

  Scenario: Simply execute some class-based definitions
    Given   a file named "features/steps/steps.py" with:
      """
      from base_steps import SomeSteps
      SomeSteps().register()
      """
    And   a file named "features/use_class_steps.feature" with:
      """
      Feature:
        Scenario:
          Given I go to the supermarket
          When  I buy the usual things
          Then  I have 2 apples
          And   I have 3 bananas
      """
    When I run "behave -f plain features/use_class_steps.feature"
    Then it should pass with:
      """
      1 feature passed, 0 failed, 0 skipped
      1 scenario passed, 0 failed, 0 skipped
      4 steps passed, 0 failed, 0 skipped, 0 undefined
      """

  Scenario: Extend a set of class-based steps
    Given a file named "features/steps/steps.py" with:
    """
    from base_steps import SomeSteps

    class ExtendedSteps(SomeSteps):
        usual_things = {
            'apples': 1,
            'bananas': 1
        }
        def step_when_I_buy_the_usual_things(self):
            for item, quantity in self.usual_things.items():
                self.step_when_I_buy(quantity, item)

    ExtendedSteps().register()

    """
    And   a file named "features/use_class_steps.feature" with:
      """
      Feature:
        Scenario:
          Given I go to the supermarket
          When  I buy the usual things
          Then  I have 1 apples
          And   I have 1 bananas
      """
    When I run "behave -f plain features/use_class_steps.feature"
    Then it should pass with:
      """
      1 feature passed, 0 failed, 0 skipped
      1 scenario passed, 0 failed, 0 skipped
      4 steps passed, 0 failed, 0 skipped, 0 undefined
      """

  Scenario: Make additional steps in a subclass (with custom matcher)
    Given a file named "features/steps/steps.py" with:
    """
    from base_steps import SomeSteps
    from behave.matchers import RegexMatcher
    class ExtendedSteps(SomeSteps):
        usual_things = {
            'apples': 2,
            'bananas': 4
        }
        def step_when_I_buy_the_usual_things(self):
            for item, quantity in self.usual_things.items():
                self.step_when_I_buy(quantity, item)

        @SomeSteps.when(u'I (double|halve) my item quantities', matcher=RegexMatcher)
        def multiply_quantity(self, by_amount):
            cart = self.context.shopping_cart
            if by_amount == 'double':
                multiple = 2
            else:
                multiple = 0.5
            for item in cart:
                current_quantity = cart[item]
                cart[item] *= multiple

    ExtendedSteps().register()
    """
    And   a file named "features/use_class_steps.feature" with:
      """
      Feature:
        Scenario:
          Given I go to the supermarket
          When  I buy the usual things
          Then  I have 2 apples
          And   I have 4 bananas
          When  I double my item quantities
          Then  I have 4 apples
          And   I have 8 bananas
          When  I halve my item quantities
          Then  I have 2 apples
          And   I have 4 bananas
      """
    When I run "behave -f plain features/use_class_steps.feature"
    Then it should pass with:
      """
      1 feature passed, 0 failed, 0 skipped
      1 scenario passed, 0 failed, 0 skipped
      10 steps passed, 0 failed, 0 skipped, 0 undefined
      """
