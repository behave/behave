.. _id.appendix.cucumber_expressions:

==============================================================================
Cucumber-Expressions
==============================================================================

.. index:: cucumber-expressions, cucumber expressions, regexp

:github:`Cucumber-expressions <cucumber/cucumber-expressions>`:

* Similar idea like :ref:`parse expressions <id.appendix.parse_expressions>`
* Provide a compact, readable placeholder syntax for step-parameters in step definitions
* Support pre-defined parameter types with type conversion
* Support to define own parameter types
* Much easier to use compared to :ref:`regular expressions <id.appendix.regular_expressions>`

.. code-block::
    :caption: EXAMPLES: Step definitions with cucumber-expression

    I have {int} cucumbers in my belly
    I have {float} cucumbers in my belly
    I have a {color} ball


Example
---------

.. code-block:: python
    :caption: FILE: features/environment.py

    from behave.cucumber_expression import use_step_matcher_for_cucumber_expressions

    # -- DEFINE: cucumber-expressions as default step-matcher.
    use_step_matcher_for_cucumber_expressions()


.. code-block:: python
    :caption: FILE: features/steps/example_steps_with_cucumber_expression.py

    from behave import when
    from behave.cucumber_expression import use_step_matcher_for_cucumber_expressions

    # -- REQUIRED: If multiple step-matcher variants are used.
    use_step_matcher_for_cucumber_expressions()

    # -- MATCHES STEPS:
    #   When I eat 1 apple
    #   When I eat 10 apples
    @when('I eat {int} apple(s)')
    def step_when_eat_apples(ctx, number: int):
        assert isinstance(number, int)
        assert number >= 0
        ctx.apples_count = number


Predefined Parameter Types
-------------------------------

================= =========== ==============================================================================================
ParameterType     Type        Description
================= =========== ==============================================================================================
``{int}``         ``int``      Matches an 32-bit integer number (``int``) sand converts to it, like: ``42``
``{float}``       ``float``    Matches ``float`` (as 32-bit float), like: ``3.6``, ``.8``, ``-9.2``
``{word}``        ``string``   Matches one word without whitespace, like: ``banana`` (not: ``banana split``).
``{string}``      ``string``   Matches double-/single-quoted strings, for example ``"banana split"`` (not: ``banana split``).
``{}``            ``string``   Matches anything, like ``re_pattern = ".*"``
``{bigdecimal}``  ``Decimal``  Matches ``float``, but converts to ``BigDecimal`` if platform supports it.
``{double}``      ``float``    Matches ``float``, but converts to 64-bit float number if platform supports it.
``{biginteger}``  ``int``      Matches ``int``, but converts to "BigInteger" if platform supports it.
``{byte}``        ``int``      Matches ``int``, but converts to 8-bit signed integer if platform supports it.
``{short}``       ``int``      Matches ``int``, but converts to 16-bit signed integer if platform supports it.
``{long}``        ``int``      Matches ``int``, but converts to 64-bit signed integer if platform supports it.
================= =========== ==============================================================================================

Use Optional Text
------------------------------------------------------------------------------

Sometimes, it is useful to match optional text (example: singular/plural).

.. code-block::
    :caption: EXAMPLE: Use optional word part

    I have {int} cucumber(s) in my belly

    # -- MATCHES:
    I have 1 cucumber in my belly
    I have 42 cucumbers in my belly


Use Alternative Words
------------------------------------------------------------------------------

Sometimes, it is useful to match two word alternatives.


.. code-block::
    :caption: EXAMPLE: Use word alternatives

    I have {int} cucumber(s) in my belly/stomach

    # -- MATCHES:
    I have 1 cucumber in my belly
    I have 42 cucumbers in my stomach



Escaping for Parenthesis/Braces
------------------------------------------------------------------------------

.. code-block::
    :caption: EXAMPLE: Use ESCAPING

    I have {int} \{what} cucumber(s) in my belly \(amazing!)

    # -- MATCHES:
    I have 1 {what} cucumber in my belly (amazing!)
    I have 42 {what} cucumbers in my belly (amazing!)


User-Defined Types
------------------------------------------------------------------------------

**EXAMPLE 1:** Number

.. code-block:: python
    :caption: FILE: features/steps/example1_number_steps.py

    from behave import when
    from behave.cucumber_expression import (
        define_parameter_type_with,
        use_step_matcher_for_cucumber_expressions
    )
    import parse

    # -- TYPE-CONVERTER (aka: parse-function)
    # HINT: Proof-of-concept (BETTER USE: {int})
    @parse.with_pattern(r"\d+")
    def parse_number(text):
        return int(text)

    # -- DEFINE PARAMETER-TYPE:
    # HINT: Each parameter type can be defined only once.
    define_parameter_type_with(
        name="number",
        regexp=parse_number.pattern,
        type=int,
        transformer=parse_number
    )

    use_step_matcher_for_cucumber_expressions()

    # -- MATCHES STEPS:
    #   When I eat 1 apple
    #   When I eat 10 apples
    @when('I eat {number} apple(s)')
    def step_when_eat_apples(ctx, the_number: int):
        assert isinstance(the_number, int)
        assert the_number >= 0
        ctx.apples_count = the_number

**EXAMPLE 2:** Parameter Type for ``Color`` enum

.. code-block:: python
    :caption: FILE: example4me/color.py

    from enum import Enum

    class Color(Enum):
        red = 1
        green = 2
        blue = 3


.. code-block:: python
    :caption: FILE: features/steps/example2_color_steps.py

    from behave import when
    from behave.cucumber_expression import (
        TypeBuilder,    # -- BASED ON: parse_type.TypeBuilder
        define_parameter_type_with,
        use_step_matcher_for_cucumber_expressions
    )
    from example4me.color import Color

    # -- TYPE-CONVERTER(s):
    parse_color = TypeBuilder.make_enum(Color)

    # -- DEFINE PARAMETER-TYPE:
    define_parameter_type_with(
        name="color",
        regexp=parse_color.pattern,
        type=Color,
        transformer=parse_color
    )

    use_step_matcher_for_cucumber_expressions()

    # -- MATCHES STEPS:
    # When I use the red color
    # When I use the blue color
    @when('I use the {color} color')
    def step_when_use_color(ctx, the_color: Color):
        assert isinstance(the_color, Color)
        ctx.selected_color = the_color

**EXAMPLE 3:** Using more than one Parameter Type in a Step Definition

* Ordering of parameters in step-function must match the ordering in the step definition text

.. code-block:: python
    :caption: FILE: features/steps/example3_colored_fruit_steps.py

    from behave import when
    from behave.cucumber_expression import (
        TypeBuilder,    # -- BASED ON: parse_type.TypeBuilder
        define_parameter_type_with,
        use_step_matcher_for_cucumber_expressions
    )
    from example4me.color import Color

    # -- TYPE-CONVERTER(s):
    SUPPORTED_FRUITS = ["apple", "banana", "pear"]
    parse_color = TypeBuilder.make_enum(Color)
    parse_fruit = TypeBuilder.make_choice(SUPPORTED_FRUITS)

    # -- DEFINE PARAMETER-TYPE:
    # HINT: Each parameter type can be defined only once.
    define_parameter_type_with(
        name="color",
        regexp=parse_color.pattern,
        type=Color,
        transformer=parse_color
    )
    define_parameter_type_with(
        name="fruit",
        regexp=parse_fruit.pattern,
        type=str,
        transformer=parse_fruit
    )

    use_step_matcher_for_cucumber_expressions()

    # -- MATCHES STEPS:
    # When I eat the red apple
    # When I eat the green banana
    # When I eat the blue pear
    @when('I eat the {color} {fruit}')
    def step_when_eat_fruit(ctx, the_color: Color, the_fruit: str):
        assert isinstance(the_color, Color)
        assert isinstance(the_fruit, str)
        ctx.selected_fruit_combination = (the_color, the_fruit)

.. seealso:: **Cucumber-Expressions:**

    * Repository: :github:`cucumber/cucumber-expressions`
    * :this_repo:`features/step_matcher.cucumber_expressions.feature`
    * :github:`parse_type <jenisys/parse_type>`: ``TypeBuilder`` functionality and more.

.. include:: _common_extlinks.rst

.. hidden:

    SIMILAR: :ref:`parse-expressions`

    * `parse`_: https://github.com/r1chardj0n3s/parse
    * `parse_type`_: https://github.com/jenisys/parse_type


