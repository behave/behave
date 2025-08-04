"""
Test issue #1177.

.. seealso:: https://github.com/behave/behave/issues/1177
"""

# -- IMPORTS:
from __future__ import absolute_import, print_function
import sys
import parse
import pytest
from behave._stepimport import use_step_import_modules, SimpleStepContainer
from behave.parser import parse_step


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
    assert result["answer"] is True
    result = parser.parse("Light is on: false")
    assert result["answer"] is False
    result = parser.parse("Light is on: __NO_MATCH__")
    assert result is None


@pytest.mark.skipif(sys.version_info < (3, 11), reason="REQUIRES: Python >= 3.11")
def test_parse_with_bad_type_converter_pattern_raises_not_implemented_error():
    # -- HINT: re.error is only raised for Python >= 3.11
    # FAILURE-POINT: parse.Parser._match_re property -- compiles _match_re
    parser = parse.Parser("Light is on: {answer:Bool}",
                          extra_types=dict(Bool=parse_bool_bad))

    # -- PROBLEM POINT:
    with pytest.raises(NotImplementedError) as exc_info:
        _ = parser.parse("Light is on: true")

    expected = "Group names (e.g. (?P<name>) can cause failure, as they are not escaped properly:"
    assert expected in str(exc_info.value)


# -- SYNDROME: NotImplementedError is only raised for Python >= 3.11
@pytest.mark.skipif(sys.version_info < (3, 11), reason="REQUIRES: Python >= 3.11")
def test_syndrome(capsys):
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

        # -- ENSURE: No AmbiguousStepError is raised when another step is added.
        @then(u'first step and more')
        def then_second_step(ctx):
            pass

    # -- ENSURE: BAD-STEP-DEFINITION is not registered in step_registry
    step = parse_step(u'Then this step is "true"')
    assert this_step_registry.find_step_definition(step) is None

    # -- ENSURE: BAD-STEP-DEFINITION is shown in output.
    captured = capsys.readouterr()
    expected = """BAD-STEP-DEFINITION: @then('first step is "{value:Bool}"')"""
    assert expected in captured.err
    assert "RAISED EXCEPTION: NotImplementedError:Group names (e.g. (?P<name>)" in captured.err


@pytest.mark.skipif(sys.version_info < (3, 11), reason="REQUIRES: Python >= 3.11")
def test_bad_step_is_not_registered_if_regex_compile_fails(capsys):
    """
    Ensure that step-definition is not registered if parse-expression compile fails.
    """
    step_container = SimpleStepContainer()
    this_step_registry = step_container.step_registry
    with use_step_import_modules(step_container):
        from behave import then, register_type

        register_type(Bool=parse_bool_bad)

        @then(u'first step is "{value:Bool}"')
        def then_first_step(ctx, value):
            assert isinstance(value, bool), "%r" % value

    # -- ENSURE: Step-definition is not registered in step-registry.
    step = parse_step(u'Then first step is "true"')
    step_matcher = this_step_registry.find_step_definition(step)
    assert step_matcher is None


@pytest.mark.skipif(sys.version_info >= (3, 11), reason="REQUIRES: Python < 3.11")
@pytest.mark.filterwarnings("ignore:Flags not at the start of the expression.*:DeprecationWarning")
def test_bad_step_is_registered_if_regex_compile_succeeds(capsys):
    step_container = SimpleStepContainer()
    this_step_registry = step_container.step_registry
    with use_step_import_modules(step_container):
        from behave import then, register_type

        register_type(Bool=parse_bool_bad)

        @then(u'first step is "{value:Bool}"')
        def then_first_step(ctx, value):
            assert isinstance(value, bool), "%r" % value

    # -- ENSURE: Step-definition is not registered in step-registry.
    step = parse_step(u'Then first step is "true"')
    step_matcher = this_step_registry.find_step_definition(step)
    assert step_matcher is not None
