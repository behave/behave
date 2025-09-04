"""
Provide some "parameter-types" (type-converters) for step parameters
that can be used in ``parse-expressions`` (step_matcher: "parse"/"cfparse").

EXAMPLE 1::

    # -- FILE: features/steps/example_steps1.py
    from behave import given, register_type
    from behave.parameter_type import parse_number

    register_type(Number=parse_number)

    # -- EXAMPLE: "Given I buy 2 apples"
    @given('I buy {amount:Number} apples'):
    def step_given_buy_apples(ctx, amount: int):
        pass

EXAMPLE 2::

    # -- FILE: features/steps/example_steps2.py
    from behave import given, register_type
    from behave.parameter_type import parse_number
    from parse_type import TypeBuilder

    FRUITS = [
        "apple",  "banana",  "orange",   # -- SINGULAR
        "apples", "bananas", "oranges",  # -- PLURAL
    ]
    parse_fruits = TypeBuilder.make_choice(FRUITS)

    register_type(Fruit=parse_fruit)
    register_type(Number=parse_number)

    # -- EXAMPLE: "Given I sell 1 apple", "Given I sell 2 bananas", ...
    @given('I sell {amount:Number} {fruit:Fruit}'):
    def step_given_sell_fruits(ctx, amount: int, fruit: str):
        pass
"""

from __future__ import absolute_import, print_function
from collections import namedtuple
import os
import parse
from behave import register_type
from .python_feature import PYTHON_VERSION

if PYTHON_VERSION < (3, 6):
    # -- NEEDED-FOR: Path should be similar to Python3 implementation.
    from pathlib2 import Path
else:
    # -- SINCE: Python 3.4 -- But some minor changes in Python 3.5, too.
    from pathlib import Path


# -----------------------------------------------------------------------------
# VALUE OBJECT CLASSES
# -----------------------------------------------------------------------------
EnvironmentVar = namedtuple("EnvironmentVar", ["name", "value"])


# -----------------------------------------------------------------------------
# TYPE CONVERTERS
# -----------------------------------------------------------------------------
@parse.with_pattern(r"\d+")
def parse_number(text):
    """
    Type converter that matches an integer number and converts to an "int".

    :param text:  Text to use.
    :return: Converted number (as int).
    :raises: ValueError, if number conversion fails
    """
    return int(text)

@parse.with_pattern(r"\w+")
def parse_word(text):
    """
    Type converter that matches text without whitespace characters as one word.

    :param text:  Text to use.
    :return: Text (as string).
    """
    return text

@parse.with_pattern(r"[a-zA-Z_]([a-zA-Z0-9_\.])+", regex_group_count=1)
def parse_dotted_word(text):
    """
    Type converter that matches one dotted word, like:

    * "one"
    * "one.two"
    * "one.two.three"

    :param text:  Text to use.
    :return: Text (as string).
    """
    return text

@parse.with_pattern(r".*")
def parse_any_text(text):
    """
    Type converter that matches ANY text (even: EMPTY_STRING).

    EXAMPLE:

    .. code-block:: python

        # -- FILE: features/steps/example_steps.py
        from behave import step, register_type
        from behave.step_parameter import parse_any_text

        register_type(AnyText=parse_any_text)

        @step('a parameter with "{param:AnyText}"')
        def step_use_parameter(context, param):
            pass

    .. code-block:: gherkin

        # -- FILE: features/example_any_text.feature
        ...
        Given a parameter with ""
        Given a parameter with "one"
        Given a parameter with "one two three"
    """
    return text


@parse.with_pattern(r'[^"]*')
def parse_unquoted_text(text):
    """
    Type converter that matches UNQUOTED text (using: double-quotes).

    EXAMPLE:

    .. code-block:: python

        # -- FILE: features/steps/example_steps.py
        from behave import step, register_type
        from behave.step_parameter import parse_unquoted_text

        register_type(Unquoted=parse_unquoted_text)

        @step('some parameter with "{param:Unquoted}"')
        def step_some_parameter(context, param):
            pass
    """
    return text


@parse.with_pattern(r'[^"]*')
def parse_path(text):
    """
    Type converter that matches UNQUOTED text (using: double-quotes)
    abd return a Path object.

    EXAMPLE:

    .. code-block:: python

        # -- FILE: features/steps/example_steps.py
        from pathlib import Path
        from behave import step, register_type
        from behave.parameter_type import parse_path

        register_type(Path=parse_path)

        @step('some file name "{filename:Path}" exists')
        def step_some_file_exists(context, filename):
            assert isinstance(filename, Path)
            assert filename.exists()
    """
    return Path(text.strip())


@parse.with_pattern(r'[^"]*')
def parse_path_as_text(text):
    return text.strip()


@parse.with_pattern(r"\$\w+")  # -- ONLY FOR: $WORD
def parse_environment_var(text, default=None):
    """
    Matches the name of a process environment-variable, like "$HOME".
    The name and value of this environment-variable is returned
    as value-object.

    If the environment-variable is undefined, its value is None.

    :param:  Text to parse/convert (as string).
    :returns: EnvironmentVar object with name and value.

    EXAMPLE:

    .. code-block:: gherkin

        # -- FILE: features/example_environment_var.feature
        ...
        Given I use "$TOP_DIR" as current directory
    """
    if not text.startswith("$"):
        raise ValueError("REQUIRE START-WITH $: '{}'".format(text))

    env_name = text[1:]
    env_value = os.environ.get(env_name, default)
    return EnvironmentVar(env_name, env_value)


# -----------------------------------------------------------------------------
# TYPE REGISTRY:
# -----------------------------------------------------------------------------
TYPE_REGISTRY = dict(
    AnyText=parse_any_text,
    Number=parse_number,
    Path=parse_path,
    Unquoted=parse_unquoted_text,
    EnvironmentVar=parse_environment_var,
    Word=parse_word,
    Dotted=parse_dotted_word,
)


def register_all_types():
    register_type(**TYPE_REGISTRY)


# -----------------------------------------------------------------------------
# MODULE INIT:
# -----------------------------------------------------------------------------
AUTO_REGISTER_TYPE_CONVERTERS = False
if AUTO_REGISTER_TYPE_CONVERTERS:
    register_all_types()
