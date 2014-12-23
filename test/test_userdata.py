# -*- coding: utf-8 -*-

from __future__ import absolute_import
from behave.configuration import Configuration
from behave.userdata import UserData, parse_user_define
from behave._types import Unknown
from unittest import TestCase
from nose.tools import eq_


class TestParseUserDefine(TestCase):
    """Test parse_user_define() function."""

    def test_parse__name_value(self):
        parts = parse_user_define("person=Alice")
        self.assertEqual(parts, ("person", "Alice"))

    def test_parse__name_only_for_boolean_flag(self):
        parts = parse_user_define("boolean_flag")
        self.assertEqual(parts, ("boolean_flag", "true"))

    def test_parse__name_value_with_padded_whitespace(self):
        texts = [
            "  person=Alice",
            "person=Alice  ",
            "person = Alice",
        ]
        for text in texts:
            parts = parse_user_define(text)
            self.assertEqual(parts, ("person", "Alice"))

    def test_parse__name_value_with_quoted_name_value_pair(self):
        texts = [
            '"person=Alice and Bob"',
            "'person=Alice and Bob'",
        ]
        for text in texts:
            parts = parse_user_define(text)
            self.assertEqual(parts, ("person", "Alice and Bob"))

    def test_parse__name_value_with_quoted_value(self):
        texts = [
            'person="Alice and Bob"',
            "person='Alice and Bob'",
        ]
        for text in texts:
            parts = parse_user_define(text)
            self.assertEqual(parts, ("person", "Alice and Bob"))




class TestUserData(TestCase):
    """Test UserData class."""

    def test_userdata_is_dictlike(self):
        userdata = UserData(name="Foo", number=42)
        value1 = userdata["name"]
        value2 = userdata.get("number")
        value3 = userdata.get("unknown", Unknown)
        assert isinstance(userdata, dict)
        self.assertEqual(value1, "Foo")
        self.assertEqual(value2, 42)
        assert value3 is Unknown

    def test_getas__with_known_param_and_valid_text(self):
        userdata = UserData(param="42")
        assert "param" in userdata, "ENSURE: known param"

        value = userdata.getas(int, "param")
        assert isinstance(value, int)
        self.assertEqual(value, 42)

    def test_getas__with_known_param_and_invalid_text_raises_ValueError(self):
        userdata = UserData(param="__BAD_NUMBER__")
        assert "param" in userdata, "ENSURE: known param"
        self.assertRaises(ValueError, userdata.getas, int, "param")

    def test_getas__with_known_param_and_preconverted_value(self):
        userdata = UserData(param=42)
        assert "param" in userdata, "ENSURE: known param"

        value = userdata.getas(int, "param")
        assert isinstance(value, int)
        self.assertEqual(value, 42)

    def test_getas__with_known_param_and_preconverted_value_and_valuetype(self):
        userdata = UserData(param=42)
        assert "param" in userdata, "ENSURE: known param"

        def parse_int(text):
            return int(text)

        value = userdata.getas(parse_int, "param", valuetype=int)
        assert isinstance(value, int)
        self.assertEqual(value, 42)

    def test_getas__with_unknown_param_without_default_returns_none(self):
        userdata = UserData()
        assert "param" not in userdata, "ENSURE: unknown param"

        value = userdata.getas(int, "param")
        assert value is None

    def test_getas__with_unknown_param_returns_default_value(self):
        userdata = UserData()
        assert "param" not in userdata, "ENSURE: unknown param"

        value = userdata.getas(int, "param", 123)
        assert isinstance(value, int)
        self.assertEqual(value, 123)


    def test_getint__with_known_param_and_valid_text(self):
        userdata = UserData(param="42")
        value = userdata.getint("param")
        assert isinstance(value, int)
        self.assertEqual(value, 42)

    def test_getint__with_known_param_and_invalid_text_raises_ValueError(self):
        userdata = UserData(param="__BAD_NUMBER__")
        self.assertRaises(ValueError, userdata.getint, "param")

    def test_getint__with_unknown_param_without_default_returns_zero(self):
        userdata = UserData()
        value = userdata.getint("param")
        self.assertEqual(value, 0)

    def test_getint__with_unknown_param_returns_default_value(self):
        userdata = UserData()
        value = userdata.getint("param", 123)
        assert isinstance(value, int)
        self.assertEqual(value, 123)

    def test_getfloat__with_known_param_and_valid_text(self):
        for valid_text in ["1.2", "2", "-1E+3", "+2.34E-5"]:
            userdata = UserData(param=valid_text)
            value = userdata.getfloat("param")
            assert isinstance(value, float)
            self.assertEqual(value, float(valid_text))

    def test_getfloat__with_known_param_and_invalid_text_raises_ValueError(self):
        userdata = UserData(param="__BAD_NUMBER__")
        self.assertRaises(ValueError, userdata.getfloat, "param")

    def test_getfloat__with_unknown_param_without_default_returns_zero(self):
        userdata = UserData()
        value = userdata.getfloat("param")
        self.assertEqual(value, 0.0)

    def test_getfloat__with_unknown_param_returns_default_value(self):
        userdata = UserData()
        value = userdata.getint("param", 1.2)
        assert isinstance(value, float)
        self.assertEqual(value, 1.2)


    def test_getbool__with_known_param_and_valid_text(self):
        for true_text in ["true", "TRUE", "True", "yes", "on", "1"]:
            userdata = UserData(param=true_text)
            value = userdata.getbool("param")
            assert isinstance(value, bool), "text=%s" % true_text
            self.assertEqual(value, True)

        for false_text in ["false", "FALSE", "False", "no", "off", "0"]:
            userdata = UserData(param=false_text)
            value = userdata.getbool("param")
            assert isinstance(value, bool), "text=%s" % false_text
            self.assertEqual(value, False)

    def test_getbool__with_known_param_and_invalid_text_raises_ValueError(self):
        userdata = UserData(param="__BAD_VALUE__")
        self.assertRaises(ValueError, userdata.getbool, "param")

    def test_getbool__with_unknown_param_without_default_returns_false(self):
        userdata = UserData()
        value = userdata.getfloat("param")
        self.assertEqual(value, False)

    def test_getbool__with_unknown_param_returns_default_value(self):
        userdata = UserData()
        value = userdata.getint("param", 1.2)
        assert isinstance(value, float)
        self.assertEqual(value, 1.2)
