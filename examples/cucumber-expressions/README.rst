EXAMPLE: Use step-matcher for cucumber-expressions
===============================================================================

Support for a step definitions with `cucumber-expressions`_ was added to :pypi:`behave`
by providing the :mod:`behave.cucumber_expression` module.

`Cucumber-expressions`_:

* Provide a simple syntax for step-parameters (aka: placeholders) compared to regular-expressions
* Provide a simple syntax for optional or alternative (unmatched) text parts.
* Provide support for parameter types and type conversions
* Provide a number of predefined parameter types, like: ``{int}``, ``{word}``, ``{string}``, ...
* Similar to ``parse-expressions`` that are normally used in `behave`_
  (hint: ``parse-expressions`` was one of the descendants that lead to the development of `cucumber-expressions`_)


Use :func:`use_step_matcher_for_cucumber_expressions() <behave.cucumber_expression.use_step_matcher_for_cucumber_expressions()>`
in the:

* ``features/environment.py`` file: Enable this step-matcher as default
* ``features/steps/*.py`` steps-file: Enable this step-matcher before you use any steps with `cucumber-expressions`_

.. code-block:: python
    :caption: FILE: features/environment.py

    from behave.cucumber_expression import use_step_matcher_for_cucumber_expressions

    # -- HINT: Use StepMatcher4CucumberExpressions as default step-matcher.
    use_step_matcher_for_cucumber_expressions()



EXAMPLE 1:
--------------------------

You have an :class:`Enum <enum.Enum>` class that you want to use as ``parameter_type`` (placeholder)
in your steps. For example, the :class:`Color <example4me.color.Color>` enum:

.. code-block:: python
    :caption: FILE: example4me/color.py

    from enum import Enum

    class Color(Enum):
        red = 1
        green = 2
        blue = 3

        @classmethod
        def from_name(cls, text: str):
            text = text.lower()
            for enum_item in iter(cls):
                if enum_item.name == text:
                    return enum_item
            # -- OOPS:
            raise ValueError("UNEXPECTED: {}".format(text))

You provide the necessary steps with the ``parameter_type=color``:

.. code-block:: python
    :caption: FILE: features/steps/color_steps.py

    from behave import given, when, then
    from behave.cucumber_expression import (
        ParameterType,
        define_parameter_type,
        define_parameter_type_with
    )
    from example4me.color import Color

    # -- REGISTER PARAMETER TYPES:
    # OR: Use define_parameter_type_with(name="color", ...)
    define_parameter_type(ParameterType(
        name="color",
        regexp="red|green|blue",
        type=Color,
        transformer=Color.from_name
    ))

    # -- STEP DEFINITIONS: With OPTIONAL parts.
    @when('I select the "{color}" theme colo(u)r')
    def step_when_select_color_theme(ctx, color: Color):
        assert isinstance(color, Color)
        ctx.selected_color = color

    @then('the profile colo(u)r should be "{color}"')
    def step_then_profile_color_should_be(ctx, the_color: Color):
        assert isinstance(the_color, Color)
        assert ctx.selected_color == the_color

.. code-block:: gherkin
    :caption: features/cucumber_expression.feature

    Feature: Use CucumberExpressions in Step Definitions
      Scenario: User selects a color twice
        Given I am on the profile settings page
        When I select the "red" theme colour
        But  I select the "blue" theme color
        Then the profile color should be "blue"


EXAMPLE 2: Text Alternatives
-----------------------------

.. literalinclude:: features/page_steps.feature

.. code-block:: python
    :caption: features/steps/page_steps.py

    from behave import step

    # -- STEP DEFINITIONS: Use ALTERNATIVES
    @step("I am on the profile customisation/settings page")
    def step_on_profile_settings_page(ctx):
        print("STEP: Given I am on profile ... page")

.. code-block:: gherkin
    :caption: features/cucumber_expression.feature

    Feature: Use CucumberExpressions in Step Definitions
      Scenario: User selects a color twice
        Given I am on the profile settings page
        When I select the "red" theme colour
        But  I select the "blue" theme color
        Then the profile color should be "blue"


.. _`cucumber-expressions`: https://github.com/cucumber/cucumber-expressions
.. _`CucumberExpressions`: https://github.com/cucumber/cucumber-expressions
.. _`features/step_matcher.cucumber_expressions.feature`: ../../features/step_matcher.cucumber_expressions.feature
