"""
Tests for :mod:`behave.cucumber_expression` module.

RELATED TO:

* Step Definitions (aka: step_matcher) with CucumberExpressions
"""

from __future__ import absolute_import, print_function
from contextlib import contextmanager
from enum import Enum

import parse
import six
import pytest
# MAYBE: from assertpy import assert_that

try:
    # -- REQUIRES: Python3, Python.version >= 3.8  (probably)
    from behave.cucumber_expression import (
        ParameterType,
        ParameterTypeRegistry,
        StepMatcher4CucumberExpressions,
        TypeBuilder,
    )
    HAVE_CUCUMBER_EXPRESSIONS = True
except (ImportError, SyntaxError):
    # -- GUARD FOR: Python2 and Python3 (< 3.8)
    HAVE_CUCUMBER_EXPRESSIONS = False


# -----------------------------------------------------------------------------
# TEST CANDIDATE SUPPORT
# -----------------------------------------------------------------------------
class Color(Enum):
    red = 1
    green = 2
    blue = 3

    @classmethod
    def from_name(cls, text):
        for enum_item in iter(cls):
            if enum_item.name == text:
                return enum_item
        # -- NOT-FOUND:
        expected_names = [ei.name for ei in iter(cls)]
        message = "%r (expected: %s)" % (text, ", ".join(expected_names))
        raise ValueError(message)


COLOR_NAMES = [enum_item.name for enum_item in iter(Color)]
COLOR_UPPER_CASE_NAMES =  [name.upper() for name in COLOR_NAMES]
COLOR_EXTENDED_NAMES = COLOR_NAMES + COLOR_UPPER_CASE_NAMES


@parse.with_pattern(r"\d+")
def parse_number(text):
    return int(text)


# -----------------------------------------------------------------------------
# TEST SUPPORT
# -----------------------------------------------------------------------------
class FakeContext(object):
    def __init__(self, **kwargs):
        for name, value in kwargs.items():
            setattr(self, name, value)

    @contextmanager
    def use_with_user_mode(self):
        yield self


def step_do_nothing(ctx, *args, **kwargs):
    print("STEP CALLED WITH: args=%r, kwargs=%r" % (args, kwargs))


class StepRunner(object):
    def __init__(self, step_matcher):
        self.step_matcher = step_matcher

    @classmethod
    def with_step_matcher(cls, pattern, func=None, step_type=None,
                          parameter_types=None):
        if func is None:
            func = step_do_nothing

        step_matcher = StepMatcher4CucumberExpressions(func, pattern,
                                                       step_type=step_type,
                                                       parameter_types=parameter_types)
        return cls(step_matcher)

    def match_and_run(self, step_text):
        matched = self.step_matcher.match(step_text)
        assert matched is not None, "%r" % matched
        ctx = FakeContext()
        _result = matched.run(ctx)
        return ctx

    def assert_step_is_not_matched(self, step_text):
        matched = self.step_matcher.match(step_text)
        assert matched is None, "%r" % matched


# -----------------------------------------------------------------------------
# TEST FIXTURES
# -----------------------------------------------------------------------------
@pytest.fixture
def parameter_type_registry():
    parameter_type_registry = ParameterTypeRegistry()
    yield parameter_type_registry


# -----------------------------------------------------------------------------
# TEST SUITE -- REQUIRES: Python3, probably Python.version >= 3.8
# -----------------------------------------------------------------------------
if HAVE_CUCUMBER_EXPRESSIONS:
    @pytest.mark.skipif(six.PY2, reason="REQUIRES: Python3")
    class TestBasics(object):
        """Tests that checks basic functionality."""
        pass


    @pytest.mark.skipif(six.PY2, reason="REQUIRES: Python3")
    class TestParameterType4Int(object):
        """Using predefined :class:`ParameterType`(s) for integer numbers"""


    @pytest.mark.skipif(six.PY2, reason="REQUIRES: Python3")
    class TestParameterType4Float(object):
        """Using predefined :class:`ParameterType`(s) for float numbers"""


    @pytest.mark.skipif(six.PY2, reason="REQUIRES: Python3")
    class TestParameterType4String(object):
        """Using predefined :class:`ParameterType`(s) for string(s)"""
        pass


    @pytest.mark.skipif(six.PY2, reason="REQUIRES: Python3")
    class TestParameterType4User(object):
        """Tests using own, user-defined ParameterType(s)."""

        @pytest.mark.parametrize("color_name", COLOR_NAMES)
        def test_enum(self, color_name, parameter_type_registry):
            parameter_type_registry.define_parameter_type(
                ParameterType(
                    "color", "red|green|blue", Color,
                    transformer=Color.from_name
                )
            )

            def this_step_func(ctx, color):
                ctx.color = color

            this_step_pattern = 'I use {color} color'
            step_runner = StepRunner.with_step_matcher(this_step_pattern, this_step_func,
                                                       parameter_types=parameter_type_registry)

            step_text = this_step_pattern.format(color=color_name)
            ctx = step_runner.match_and_run(step_text)
            assert ctx.color == Color.from_name(color_name)
            assert isinstance(ctx.color, Color)

        @pytest.mark.parametrize("bad_color_name", COLOR_UPPER_CASE_NAMES)
        def test_enum_is_case_sensitive(self, bad_color_name, parameter_type_registry):
            parameter_type_registry.define_parameter_type(
                ParameterType(
                    "color", "red|green|blue", Color,
                    transformer=Color.from_name
                )
            )

            def this_step_func(ctx, color):
                ctx.color = color

            this_step_pattern = 'I use {color} color'
            step_runner = StepRunner.with_step_matcher(this_step_pattern, this_step_func,
                                                       parameter_types=parameter_type_registry)

            step_text = this_step_pattern.format(color=bad_color_name)
            step_runner.assert_step_is_not_matched(step_text)


    @pytest.mark.skipif(six.PY2, reason="REQUIRES: Python3")
    class TestWithTypeBuilder(object):
        """
        Use CucumberExpressions with :class:`TypeBuilder`.
        Reuses :class:`parse_type.TypeBuilder` for "parse-expressions".
        """

        @pytest.mark.parametrize("color_name", COLOR_NAMES)
        def test_make_enum_with_enum_class(self, color_name, parameter_type_registry):
            parse_color = TypeBuilder.make_enum(Color)
            parameter_type_registry.define_parameter_type(ParameterType(
                "color", parse_color.pattern, Color,
                transformer=parse_color
            ))

            def this_step_func(ctx, color):
                ctx.color = color

            this_step_pattern = 'I use {color} color'
            step_runner = StepRunner.with_step_matcher(this_step_pattern, this_step_func,
                                                       parameter_types=parameter_type_registry)

            step_text = this_step_pattern.format(color=color_name)
            ctx = step_runner.match_and_run(step_text)
            assert ctx.color == Color.from_name(color_name)
            assert isinstance(ctx.color, Color)

        @pytest.mark.parametrize("bad_color_name", COLOR_UPPER_CASE_NAMES)
        def test_make_enum_is_case_sensitive(self, bad_color_name, parameter_type_registry):
            parse_color = TypeBuilder.make_enum(Color)
            parameter_type_registry.define_parameter_type(ParameterType(
                "color", parse_color.pattern, type=Color,
                transformer=parse_color
            ))

            def this_step_func(ctx, color):
                ctx.color = color

            this_step_pattern = 'I use {color} color'
            step_runner = StepRunner.with_step_matcher(this_step_pattern, this_step_func,
                                                       parameter_types=parameter_type_registry)

            step_text = this_step_pattern.format(color=bad_color_name)
            step_runner.assert_step_is_not_matched(step_text)

        @pytest.mark.parametrize("state_name, state_value", [("on", True), ("off", False)])
        def test_make_enum_with_mapping(self, state_name, state_value, parameter_type_registry):
            parse_state_on = TypeBuilder.make_enum({"on": True, "off": False})
            parameter_type_registry.define_parameter_type(ParameterType(
                "state_on", parse_state_on.pattern, type=bool,
                transformer=parse_state_on
            ))

            def this_step_func(ctx, state):
                ctx.state_on = state

            this_step_pattern = 'the light is switched {state_on}'
            step_runner = StepRunner.with_step_matcher(this_step_pattern, this_step_func,
                                                       parameter_types=parameter_type_registry)

            step_text = this_step_pattern.format(state_on=state_name)
            ctx = step_runner.match_and_run(step_text)
            assert ctx.state_on == state_value
            assert isinstance(ctx.state_on, bool)

        @pytest.mark.parametrize("color_name", COLOR_NAMES)
        def test_make_choice(self, color_name, parameter_type_registry):
            parse_color_choice = TypeBuilder.make_choice(COLOR_NAMES)
            parameter_type_registry.define_parameter_type(ParameterType(
                "color_choice", parse_color_choice.pattern, type=str,
                transformer=parse_color_choice
            ))

            def this_step_func(ctx, color_name):
                ctx.color_choice = color_name

            this_step_pattern = 'I use {color_choice} color'
            step_runner = StepRunner.with_step_matcher(this_step_pattern, this_step_func,
                                                       parameter_types=parameter_type_registry)

            step_text = this_step_pattern.format(color_choice=color_name)
            ctx = step_runner.match_and_run(step_text)
            assert ctx.color_choice == color_name
            assert isinstance(ctx.color_choice, str)

        @pytest.mark.parametrize("variant_text, variant_value", [
            ("0", 0),
            ("42", 42),
            ("red", Color.red),
            ("green", Color.green),
            ("blue", Color.blue),
        ])
        def test_make_variant(self, variant_text, variant_value, parameter_type_registry):
            parse_color = TypeBuilder.make_enum(Color)
            parse_variant = TypeBuilder.make_variant([parse_number, parse_color])
            parameter_type_registry.define_parameter_type(ParameterType(
                "number_or_color", parse_variant.pattern, type=None,
                transformer=parse_variant
            ))

            def this_step_func(ctx, number_or_color):
                ctx.color = None
                ctx.number = None
                if isinstance(number_or_color, Color):
                    ctx.color = number_or_color
                elif isinstance(number_or_color, int):
                    ctx.number = number_or_color

            this_step_pattern = 'I use {number_or_color} apples'
            step_runner = StepRunner.with_step_matcher(this_step_pattern, this_step_func,
                                                       parameter_types=parameter_type_registry)

            step_text = this_step_pattern.format(number_or_color=variant_text)
            ctx = step_runner.match_and_run(step_text)
            if isinstance(variant_value, Color):
                assert ctx.color == variant_value
                assert isinstance(ctx.color, Color)
                assert ctx.number is None
            else:
                assert ctx.number == variant_value
                assert isinstance(ctx.number, int)
                assert ctx.color is None

        @pytest.mark.parametrize("numbers_text, numbers_value", [
            ("1", [1]),
            ("1, 2, 3", [1, 2, 3]),
        ])
        def test_make_many(self, numbers_text, numbers_value, parameter_type_registry):
            parse_numbers = TypeBuilder.with_many(parse_number)
            parse_numbers_pattern = r"(%s)" % parse_numbers.pattern
            parameter_type_registry.define_parameter_type(ParameterType(
                "numbers", parse_numbers_pattern, list,
                transformer=parse_numbers
            ))

            def this_step_func(ctx, numbers):
                ctx.numbers = numbers

            this_step_pattern = 'I use "{numbers}" as numbers'
            step_runner = StepRunner.with_step_matcher(this_step_pattern, this_step_func,
                                                       parameter_types=parameter_type_registry)

            step_text = this_step_pattern.format(numbers=numbers_text)
            ctx = step_runner.match_and_run(step_text)
            assert ctx.numbers == numbers_value

        @pytest.mark.parametrize("numbers_text, numbers_value", [
            ("", []),
            ("1", [1]),
            ("1, 2, 3", [1, 2, 3]),
        ])
        def test_make_many0(self, numbers_text, numbers_value, parameter_type_registry):
            parse_numbers = TypeBuilder.with_many0(parse_number)
            parse_numbers_pattern = r"(%s)" % parse_numbers.pattern
            parameter_type_registry.define_parameter_type(ParameterType(
                "numbers", parse_numbers_pattern, list,
                transformer=parse_numbers
            ))

            def this_step_func(ctx, numbers):
                ctx.numbers = numbers

            this_step_pattern = 'I use "{numbers}" as numbers'
            step_runner = StepRunner.with_step_matcher(this_step_pattern, this_step_func,
                                                       parameter_types=parameter_type_registry)

            step_text = this_step_pattern.format(numbers=numbers_text)
            ctx = step_runner.match_and_run(step_text)
            assert ctx.numbers == numbers_value
