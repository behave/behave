# -*- coding: UTF-8 -*-
# ruff: noqa: E501
"""
Unit tests for :mod:`behave.parameter_type` module.
"""

from __future__ import absolute_import, print_function
from contextlib import contextmanager
import os
from behave.parameter_type import  (
    EnvironmentVar,
    parse_number,
    parse_any_text,
    parse_unquoted_text,
    parse_environment_var,
)
from parse import Parser
import pytest


# -----------------------------------------------------------------------------
# TEST SUPPORT
# -----------------------------------------------------------------------------
@contextmanager
def os_environ():
    try:
        initial_environ = os.environ.copy()
        yield os.environ
    finally:
        # -- RESTORE:
        os.environ = initial_environ


# -----------------------------------------------------------------------------
# TEST SUITE
# -----------------------------------------------------------------------------
class TestParseNumber(object):
    TYPE_REGISTRY = dict(Number=parse_number)
    PATTERN = "Number: {number:Number}"
    TEXT_TEMPLATE = "Number: {}"

    @classmethod
    def assert_match_with_parse_number_and_converts_to_int(cls, text, expected):
        parser = Parser(cls.PATTERN, extra_types=cls.TYPE_REGISTRY)
        result = parser.parse(cls.TEXT_TEMPLATE.format(text))
        number = result["number"]
        assert number == expected
        assert isinstance(number, int)

    @classmethod
    def assert_mismatch_with_parse_number(cls, text):
        parser = Parser(cls.PATTERN, extra_types=cls.TYPE_REGISTRY)
        result = parser.parse(cls.TEXT_TEMPLATE.format(text))
        assert result is None

    @pytest.mark.parametrize("text, expected", [
        ("0", 0),
        ("12", 12),
        ("321", 321),
    ])
    def test_parse_number__matches_positive_number_and_zero(self, text, expected):
        self.assert_match_with_parse_number_and_converts_to_int(text, expected)

    @pytest.mark.parametrize("text", ["-1", "-12"])
    def test_parse_number__mismatches_negavtive_number(self, text):
        self.assert_mismatch_with_parse_number(text)


class TestParseAnyText(object):
    TYPE_REGISTRY = dict(AnyText=parse_any_text)
    PATTERN = 'AnyText: "{some:AnyText}"'
    TEXT_TEMPLATE = 'AnyText: "{}"'

    @classmethod
    def assert_match_with_parse_any_and_converts_to_string(cls, text, expected):
        parser = Parser(cls.PATTERN, extra_types=cls.TYPE_REGISTRY)
        result = parser.parse(cls.TEXT_TEMPLATE.format(text))
        actual_value = result["some"]
        assert actual_value == expected
        assert isinstance(actual_value, str)

    @classmethod
    def assert_mismatch_with_parse_any(cls, text):
        parser = Parser(cls.PATTERN, extra_types=cls.TYPE_REGISTRY)
        result = parser.parse(cls.TEXT_TEMPLATE.format(text))
        assert result is None

    @pytest.mark.parametrize("text", ["Alice", "B_O_B", "charly-123"])
    def test_parse_any_text__matches_word(self, text):
        expected = text
        self.assert_match_with_parse_any_and_converts_to_string(text, expected)

    @pytest.mark.parametrize("text", ["Alice, Bob", "Alice and Bob"])
    def test_parse_any_text__matches_many_words(self, text):
        expected = text
        self.assert_match_with_parse_any_and_converts_to_string(text, expected)

    def test_parse_any_text__matches_empty_string(self):
        text = ""
        expected = text
        self.assert_match_with_parse_any_and_converts_to_string(text, expected)

    @pytest.mark.parametrize("text", [" ", "  ", "\t", "\n"])
    def test_parse_any_text__matches_whitespace(self, text):
        expected = text
        self.assert_match_with_parse_any_and_converts_to_string(text, expected)


class TestParseUnquotedText(object):
    TYPE_REGISTRY = dict(Unquoted=parse_unquoted_text)
    PATTERN = 'Unquoted: "{some:Unquoted}"'
    TEXT_TEMPLATE = 'Unquoted: "{}"'

    @classmethod
    def assert_match_with_parse_unquoted_and_converts_to_string(cls, text, expected):
        parser = Parser(cls.PATTERN, extra_types=cls.TYPE_REGISTRY)
        result = parser.parse(cls.TEXT_TEMPLATE.format(text))
        actual_value = result["some"]
        assert actual_value == expected
        assert isinstance(actual_value, str)

    @classmethod
    def assert_mismatch_with_parse_unquoted(cls, text):
        parser = Parser(cls.PATTERN, extra_types=cls.TYPE_REGISTRY)
        result = parser.parse(cls.TEXT_TEMPLATE.format(text))
        assert result is None

    @pytest.mark.parametrize("text", ["Alice", "B_O_B", "charly-123"])
    def test_parse_unquoted_text__matches_word(self, text):
        expected = text
        self.assert_match_with_parse_unquoted_and_converts_to_string(text, expected)

    @pytest.mark.parametrize("text", ["Alice, Bob", "Alice and Bob"])
    def test_parse_unquoted_text__matches_many_words(self, text):
        expected = text
        self.assert_match_with_parse_unquoted_and_converts_to_string(text, expected)

    def test_parse_unquoted_text__matches_empty_string(self):
        text = ""
        expected = text
        self.assert_match_with_parse_unquoted_and_converts_to_string(text, expected)

    @pytest.mark.parametrize("text", [" ", "  ", "\t", "\n"])
    def test_parse_unquoted_text__matches_whitespace(self, text):
        expected = text
        self.assert_match_with_parse_unquoted_and_converts_to_string(text, expected)

    @pytest.mark.parametrize("text", ['Some "more', 'Alice "Bob and Charly"'])
    def test_parse_unquoted_text__mismatches_string_with_double_quotes(self, text):
        self.assert_mismatch_with_parse_unquoted(text)


class TestParseEnvironmentVar(object):
    TYPE_REGISTRY = dict(EnvironmentVar=parse_environment_var)
    PATTERN = 'EnvironmentVar: "{param:EnvironmentVar}"'
    TEXT_TEMPLATE = 'EnvironmentVar: "{}"'

    @classmethod
    def assert_match_with_parse_environment_var_returns_to_namedtuple(cls, text, expected):
        parser = Parser(cls.PATTERN, extra_types=cls.TYPE_REGISTRY)
        result = parser.parse(cls.TEXT_TEMPLATE.format(text))
        actual_param = result["param"]
        assert actual_param.value == expected
        assert isinstance(actual_param.value, str)
        assert isinstance(actual_param, EnvironmentVar)

    @classmethod
    def assert_match_with_parse_environment_var_and_undefined_returns_namedtuple_with_none(cls, text):
        parser = Parser(cls.PATTERN, extra_types=cls.TYPE_REGISTRY)
        result = parser.parse(cls.TEXT_TEMPLATE.format(text))
        actual_param = result["param"]
        assert actual_param.value is None
        assert isinstance(actual_param, EnvironmentVar)

    @classmethod
    def assert_mismatch_with_parse_environment_var(cls, text):
        parser = Parser(cls.PATTERN, extra_types=cls.TYPE_REGISTRY)
        result = parser.parse(cls.TEXT_TEMPLATE.format(text))
        assert result is None

    @pytest.mark.parametrize("env_var", [
        EnvironmentVar("SSH_AGENT", "localhost:12345"),
        EnvironmentVar("SSH_PID", "1234"),
    ])
    def test_parse_environment_var__uses_defined_variable(self, env_var):
        text = "${}".format(env_var.name)
        expected = env_var.value
        with os_environ() as environ:
            environ[env_var.name] = env_var.value
            self.assert_match_with_parse_environment_var_returns_to_namedtuple(text, expected)

    def test_parse_environment_var__uses_undefined_variable(self):
        env_var = EnvironmentVar("UNDEFINED_VAR", None)
        text = "${}".format(env_var.name)
        with os_environ() as environ:
            assert env_var.name not in environ
            self.assert_match_with_parse_environment_var_and_undefined_returns_namedtuple_with_none(text)
