"""
Provides some steps for testing step-definitions with `CucumberExpressions`_.

.. _CucumberExpressions: https://github.com/cucumber/cucumber-expressions
"""

from __future__ import absolute_import, print_function
from decimal import Decimal
from behave import given, when, then
from assertpy import assert_that

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
        assert_that(value).is_instance_of(int)
        assert_that(value).is_greater_than_or_equal_to(INT_MIN_VALUE)
        assert_that(value).is_less_than_or_equal_to(INT_MAX_VALUE)
        ctx.value = value


    @given('I provide a/an "{short}" value as short')
    @when('I provide a/an "{short}" value as short')
    def step_provide_value_as_short(ctx, value):
        assert_that(value).is_instance_of(int)
        assert_that(value).is_greater_than_or_equal_to(SHORT_MIN_VALUE)
        assert_that(value).is_less_than_or_equal_to(SHORT_MAX_VALUE)
        ctx.value = value


    @given('I provide a/an "{long}" value as long')
    @when('I provide a/an "{long}" value as long')
    def step_provide_value_as_long(ctx, value):
        assert_that(value).is_instance_of(int)
        assert_that(value).is_greater_than_or_equal_to(LONG_MIN_VALUE)
        assert_that(value).is_less_than_or_equal_to(LONG_MAX_VALUE)
        ctx.value = value


    @given('I provide a/an "{biginteger}" value as biginteger')
    @when('I provide a/an "{biginteger}" value as biginteger')
    def step_provide_value_as_biginteger(ctx, value):
        assert_that(value).is_instance_of(int)
        ctx.value = value


    @given('I provide a/an "{byte}" value as byte')
    @when('I provide a/an "{byte}" value as byte')
    def step_provide_value_as_byte(ctx, value):
        assert_that(value).is_instance_of(int)
        assert_that(value).is_greater_than_or_equal_to(BYTE_MIN_VALUE)
        assert_that(value).is_less_than_or_equal_to(BYTE_MAX_VALUE)
        ctx.value = value


    # -- THEN STEPS:
    @then('the stored value equals "{int}" as int')
    def step_then_stored_value_equals_as_int(ctx, expected):
        assert_that(expected).is_instance_of(int)
        assert_that(ctx.value).is_equal_to(expected)


    @then('the stored value equals "{short}" as short')
    def step_then_stored_value_equals_as_short(ctx, expected):
        assert_that(expected).is_instance_of(int)
        assert_that(ctx.value).is_equal_to(expected)


    @then('the stored value equals "{long}" as long')
    def step_then_stored_value_equals_as_long(ctx, expected):
        assert_that(expected).is_instance_of(int)
        assert_that(ctx.value).is_equal_to(expected)


    @then('the stored value equals "{biginteger}" as biginteger')
    def step_then_stored_value_equals_as_biginteger(ctx, expected):
        assert_that(expected).is_instance_of(int)
        assert_that(ctx.value).is_equal_to(expected)


# -----------------------------------------------------------------------------
# STEP DEFINITIONS: For float numbers
# -----------------------------------------------------------------------------
if HAVE_CUCUMBER_EXPRESSIONS:
    @given('I provide a/an "{float}" value as float')
    @when('I provide a/an "{float}" value as float')
    def step_provide_value_as_float(ctx, value):
        assert_that(value).is_instance_of(float)
        ctx.value = value


    @given('I provide a/an "{double}" value as double')
    @when('I provide a/an "{double}" value as double')
    def step_provide_value_as_double(ctx, value):
        assert_that(value).is_instance_of(float)
        ctx.value = value


    @given('I provide a/an "{bigdecimal}" value as bigdecimal')
    @when('I provide a/an "{bigdecimal}" value as bigdecimal')
    def step_provide_value_as_bigdecimal(ctx, value):
        assert_that(value).is_instance_of(Decimal)
        ctx.value = value


    @then('the stored value equals "{float}" as float')
    def step_then_stored_value_equals_as_float(ctx, expected):
        assert_that(expected).is_instance_of(float)
        assert_that(ctx.value).is_close_to(expected, FLOAT_ACCURACY)


    @then('the stored value equals "{double}" as double')
    def step_then_stored_value_equals_as_double(ctx, expected):
        assert_that(expected).is_instance_of(float)
        assert_that(ctx.value).is_close_to(expected, FLOAT_ACCURACY)


    @then('the stored value equals "{bigdecimal}" as bigdecimal')
    def step_then_stored_value_equals_as_bigdecimal(ctx, expected):
        assert_that(expected).is_instance_of(Decimal)
        assert_that(ctx.value).is_close_to(expected, FLOAT_ACCURACY)


# -----------------------------------------------------------------------------
# STEP DEFINITIONS: For string-like parameter types
# -----------------------------------------------------------------------------
if HAVE_CUCUMBER_EXPRESSIONS:
    @given('I provide a/an "{word}" value as word')
    @when('I provide a/an "{word}" value as word')
    def step_provide_value_as_word(ctx, value):
        assert assert_that(value).is_instance_of(str)
        ctx.value = value


    @given('I provide a/an {string} value as string')
    @when('I provide a/an {string} value as string')
    def step_provide_value_as_string(ctx, value):
        assert assert_that(value).is_instance_of(str)
        ctx.value = value


    @then('the stored value equals "{word}" as word')
    def step_then_stored_value_equals_as_word(ctx, expected):
        assert assert_that(expected).is_instance_of(str)
        assert_that(ctx.value).is_equal_to(expected)


    @then('the stored value equals {string} as string')
    def step_then_stored_value_equals_as_string(ctx, expected):
        assert assert_that(expected).is_instance_of(str)
        assert_that(ctx.value).is_equal_to(expected)


# -----------------------------------------------------------------------------
# STEP DEFINITIONS: For match anything parameter types
# -----------------------------------------------------------------------------
if HAVE_CUCUMBER_EXPRESSIONS:
    @given('I provide a/an "{}" value as any')
    @when('I provide a/an "{}" value as any')
    def step_provide_value_as_any(ctx, value):
        assert assert_that(value).is_instance_of(str)
        ctx.value = value


    @then('the stored value equals "{}" as any')
    def step_then_stored_value_equals_as_any(ctx, expected):
        assert assert_that(expected).is_instance_of(str)
        assert_that(ctx.value).is_equal_to(expected)
