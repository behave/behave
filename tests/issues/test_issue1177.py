"""
Test issue #1177.

.. seealso:: https://github.com/behave/behave/issues/1177
"""
# -- IMPORTS:
from __future__ import absolute_import, print_function

import sys

from behave._stepimport import use_step_import_modules, SimpleStepContainer
import parse
import pytest


@parse.with_pattern(r"true|false")
def parse_bool_good(text):
    return text == "true"


@parse.with_pattern(r"(?P<status>(?i)true|(?i)false)", regex_group_count=1)
def parse_bool_bad(text):
    return text == "true"


@pytest.mark.parametrize("parse_bool", [parse_bool_good])  # DISABLED:, parse_bool_bad])
def test_parse_expr(parse_bool):
    parser = parse.Parser("Light is on: {answer:Bool}",
                          extra_types=dict(Bool=parse_bool))
    result = parser.parse("Light is on: true")
    assert result["answer"] == True
    result = parser.parse("Light is on: false")
    assert result["answer"] == False
    result = parser.parse("Light is on: __NO_MATCH__")
    assert result is None


# -- SYNDROME: NotImplementedError is only raised for Python >= 3.11
@pytest.mark.skipif(sys.version_info < (3, 11),
                    reason="Python >= 3.11: NotImplementedError is raised")
def test_syndrome():
    """
    Ensure that no AmbiguousStepError is raised
    when another step is added after the one with the BAD TYPE-CONVERTER PATTERN.
    """
    step_container = SimpleStepContainer()
    this_step_registry = step_container.step_registry
    with use_step_import_modules(step_container):
        from behave import then, register_type

        register_type(Bool=parse_bool_bad)

        @then(u'first step is "{value:Bool}"')
        def then_first_step(ctx, value):
            assert isinstance(value, bool), "%r" % value

        with pytest.raises(NotImplementedError) as excinfo1:
            # -- CASE: Another step is added
            # EXPECTED: No AmbiguousStepError is raised.
            @then(u'first step and more')
            def then_second_step(ctx, value):
                assert isinstance(value, bool), "%r" % value

    # -- CASE: Manually add step to step-registry
    # EXPECTED: No AmbiguousStepError is raised.
    with pytest.raises(NotImplementedError) as excinfo2:
        step_text = u'first step and other'
        def then_third_step(ctx, value): pass
        this_step_registry.add_step_definition("then", step_text, then_third_step)

    assert "Group names (e.g. (?P<name>) can cause failure" in str(excinfo1.value)
    assert "Group names (e.g. (?P<name>) can cause failure" in str(excinfo2.value)


@pytest.mark.skipif(sys.version_info >= (3, 11),
                    reason="Python < 3.11 -- NotImpplementedError is not raised")
def test_syndrome_for_py310_and_older():
    """
    Ensure that no AmbiguousStepError is raised
    when another step is added after the one with the BAD TYPE-CONVERTER PATTERN.
    """
    step_container = SimpleStepContainer()
    this_step_registry = step_container.step_registry
    with use_step_import_modules(step_container):
        from behave import then, register_type

        register_type(Bool=parse_bool_bad)

        @then(u'first step is "{value:Bool}"')
        def then_first_step(ctx, value):
            assert isinstance(value, bool), "%r" % value

        # -- CASE: Another step is added
        # EXPECTED: No AmbiguousStepError is raised.
        @then(u'first step and mpre')
        def then_second_step(ctx, value):
            assert isinstance(value, bool), "%r" % value

    # -- CASE: Manually add step to step-registry
    # EXPECTED: No AmbiguousStepError is raised.
    step_text = u'first step and other'
    def then_third_step(ctx, value): pass
    this_step_registry.add_step_definition("then", step_text, then_third_step)
