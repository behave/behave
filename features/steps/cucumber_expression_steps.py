"""
Provides some steps for testing step-definitions with `CucumberExpressions`_.

.. _CucumberExpressions: https://github.com/cucumber/cucumber-expressions
"""

from pytest import approx
from decimal import Decimal
from behave import given, when, then

try:
    # -- REQUIRES: Python3, Python.version >= 3.8
    from behave.cucumber_expression import use_step_matcher_for_cucumber_expressions
    HAVE_CUCUMBER_EXPRESSIONS = True
except (ImportError, SyntaxError):
    HAVE_CUCUMBER_EXPRESSIONS = False


# -----------------------------------------------------------------------------
# CONSTANTS
# -----------------------------------------------------------------------------
BYTE_MAX_VALUE = 255
BYTE_MIN_VALUE = -256

SHORT_MAX_VALUE = int(2**16/2) - 1
SHORT_MIN_VALUE = -SHORT_MAX_VALUE - 1

INT_MAX_VALUE = int(2**32/2) - 1
INT_MIN_VALUE = -INT_MAX_VALUE - 1

LONG_MAX_VALUE = int(2**64/2) - 1
LONG_MIN_VALUE = -LONG_MAX_VALUE - 1


FLOAT_ACCURACY = 0.00001


# -----------------------------------------------------------------------------
# SETUP:
# -----------------------------------------------------------------------------
if HAVE_CUCUMBER_EXPRESSIONS:
    use_step_matcher_for_cucumber_expressions()


# -----------------------------------------------------------------------------
# PARAMETER TYPES
# -----------------------------------------------------------------------------


# -----------------------------------------------------------------------------
# STEP DEFINITIONS: For integer numbers
# -----------------------------------------------------------------------------
if HAVE_CUCUMBER_EXPRESSIONS:
    @given('I provide a/an "{int}" value as int')
    @when('I provide a/an "{int}" value as int')
    def step_provide_value_as_int(ctx, value):
        assert type(value) is int
        assert value >= INT_MIN_VALUE
        assert value <= INT_MAX_VALUE
        ctx.value = value


    @given('I provide a/an "{short}" value as short')
    @when('I provide a/an "{short}" value as short')
    def step_provide_value_as_short(ctx, value):
        assert type(value) is int
        assert value >= SHORT_MIN_VALUE
        assert value <= SHORT_MAX_VALUE
        ctx.value = value


    @given('I provide a/an "{long}" value as long')
    @when('I provide a/an "{long}" value as long')
    def step_provide_value_as_long(ctx, value):
        assert type(value) is int
        assert value >= LONG_MIN_VALUE
        assert value <= LONG_MAX_VALUE
        ctx.value = value


    @given('I provide a/an "{biginteger}" value as biginteger')
    @when('I provide a/an "{biginteger}" value as biginteger')
    def step_provide_value_as_biginteger(ctx, value):
        assert type(value) is int
        ctx.value = value


    @given('I provide a/an "{byte}" value as byte')
    @when('I provide a/an "{byte}" value as byte')
    def step_provide_value_as_byte(ctx, value):
        assert type(value) is int
        assert value >= BYTE_MIN_VALUE
        assert value <= BYTE_MAX_VALUE
        ctx.value = value


    # -- THEN STEPS:
    @then('the stored value equals "{int}" as int')
    def step_then_stored_value_equals_as_int(ctx, expected):
        assert type(expected) is int
        assert ctx.value == expected


    @then('the stored value equals "{short}" as short')
    def step_then_stored_value_equals_as_short(ctx, expected):
        assert type(expected) is int
        assert ctx.value == expected


    @then('the stored value equals "{long}" as long')
    def step_then_stored_value_equals_as_long(ctx, expected):
        assert type(expected) is int
        assert ctx.value == expected


    @then('the stored value equals "{biginteger}" as biginteger')
    def step_then_stored_value_equals_as_biginteger(ctx, expected):
        assert type(expected) is int
        assert ctx.value == expected


# -----------------------------------------------------------------------------
# STEP DEFINITIONS: For float numbers
# -----------------------------------------------------------------------------
if HAVE_CUCUMBER_EXPRESSIONS:
    @given('I provide a/an "{float}" value as float')
    @when('I provide a/an "{float}" value as float')
    def step_provide_value_as_float(ctx, value):
        assert type(value) is float
        ctx.value = value


    @given('I provide a/an "{double}" value as double')
    @when('I provide a/an "{double}" value as double')
    def step_provide_value_as_double(ctx, value):
        assert type(value) is float
        ctx.value = value


    @given('I provide a/an "{bigdecimal}" value as bigdecimal')
    @when('I provide a/an "{bigdecimal}" value as bigdecimal')
    def step_provide_value_as_bigdecimal(ctx, value):
        assert type(value) is Decimal
        ctx.value = value


    @then('the stored value equals "{float}" as float')
    def step_then_stored_value_equals_as_float(ctx, expected):
        assert type(expected) is float
        # ctx.value might be a bigdecimal, so we convert it to float for comparison
        assert float(ctx.value) == approx(expected, abs=FLOAT_ACCURACY)


    @then('the stored value equals "{double}" as double')
    def step_then_stored_value_equals_as_double(ctx, expected):
        assert type(expected) is float
        assert ctx.value == approx(expected, abs=FLOAT_ACCURACY)


    @then('the stored value equals "{bigdecimal}" as bigdecimal')
    def step_then_stored_value_equals_as_bigdecimal(ctx, expected):
        assert type(expected) is Decimal
        assert ctx.value == approx(expected, abs=Decimal(str(FLOAT_ACCURACY)))


# -----------------------------------------------------------------------------
# STEP DEFINITIONS: For string-like parameter types
# -----------------------------------------------------------------------------
if HAVE_CUCUMBER_EXPRESSIONS:
    @given('I provide a/an "{word}" value as word')
    @when('I provide a/an "{word}" value as word')
    def step_provide_value_as_word(ctx, value):
        assert type(value) is str
        ctx.value = value


    @given('I provide a/an {string} value as string')
    @when('I provide a/an {string} value as string')
    def step_provide_value_as_string(ctx, value):
        assert type(value) is str
        ctx.value = value


    @then('the stored value equals "{word}" as word')
    def step_then_stored_value_equals_as_word(ctx, expected):
        assert type(expected) is str
        assert ctx.value == expected


    @then('the stored value equals {string} as string')
    def step_then_stored_value_equals_as_string(ctx, expected):
        assert type(expected) is str
        assert ctx.value == expected


# -----------------------------------------------------------------------------
# STEP DEFINITIONS: For match anything parameter types
# -----------------------------------------------------------------------------
if HAVE_CUCUMBER_EXPRESSIONS:
    @given('I provide a/an "{}" value as any')
    @when('I provide a/an "{}" value as any')
    def step_provide_value_as_any(ctx, value):
        assert type(value) is str
        ctx.value = value


    @then('the stored value equals "{}" as any')
    def step_then_stored_value_equals_as_any(ctx, expected):
        assert type(expected) is str
        assert ctx.value == expected
