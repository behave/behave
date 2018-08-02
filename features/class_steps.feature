Feature: Execute Steps within a Step Function (Nested Steps)

    As a tester
    I want to reuse existing steps as class methods
    And I want to extend those class methods with subclasses
    So that I can comply with the the DRY principle.

  Scenario: Execute a number of simple steps (GOOD CASE)
    Given a new working directory
    And   a file named "features/steps/steps.py" with:
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


      class ExtendedSteps(SomeSteps):
          usual_things = {
              'apples': 2,
              'bananas': 3
          }
          def step_when_I_buy_the_usual_things(self):
              for item, quantity in self.usual_things.items():
                  self.step_when_I_buy(quantity, item)

      class MoreExtendedSteps(ExtendedSteps):
          usual_things = {
              'apples': 1,
              'bananas': 1
          }

      MoreExtendedSteps().register()

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

