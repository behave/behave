# -*- coding: UTF-8 -*-

from __future__ import absolute_import
from behave.userdata import parse_user_define, UserData, UserDataNamespace
from behave._types import Unknown
import pytest


class TestParseUserDefine(object):
    """Test parse_user_define() function."""

    def test_parse__name_value(self):
        parts = parse_user_define("person=Alice")
        assert parts == ("person", "Alice")

    def test_parse__name_only_for_boolean_flag(self):
        parts = parse_user_define("boolean_flag")
        assert parts == ("boolean_flag", "true")


    @pytest.mark.parametrize("text", [
        "  person=Alice",
        "person=Alice  ",
        "person = Alice",
    ])
    def test_parse__name_value_with_padded_whitespace(self, text):
        parts = parse_user_define(text)
        assert parts == ("person", "Alice")


    @pytest.mark.parametrize("text", [
        '"person=Alice and Bob"',
        "'person=Alice and Bob'",
    ])
    def test_parse__name_value_with_quoted_name_value_pair(self, text):
        parts = parse_user_define(text)
        assert parts == ("person", "Alice and Bob")

    @pytest.mark.parametrize("text", [
        'person="Alice and Bob"',
        "person='Alice and Bob'",
    ])
    def test_parse__name_value_with_quoted_value(self, text):
        parts = parse_user_define(text)
        assert parts == ("person", "Alice and Bob")




class TestUserData(object):
    """Test UserData class."""

    def test_userdata_is_dictlike(self):
        userdata = UserData(name="Foo", number=42)
        value1 = userdata["name"]
        value2 = userdata.get("number")
        value3 = userdata.get("unknown", Unknown)
        assert isinstance(userdata, dict)
        assert value1 == "Foo"
        assert value2 == 42
        assert value3 is Unknown

    def test_getas__with_known_param_and_valid_text(self):
        userdata = UserData(param="42")
        assert "param" in userdata, "ENSURE: known param"

        value = userdata.getas(int, "param")
        assert isinstance(value, int)
        assert value == 42

    def test_getas__with_known_param_and_invalid_text_raises_ValueError(self):
        userdata = UserData(param="__BAD_NUMBER__")
        assert "param" in userdata, "ENSURE: known param"
        with pytest.raises(ValueError):
            userdata.getas(int, "param")

    def test_getas__with_known_param_and_preconverted_value(self):
        userdata = UserData(param=42)
        assert "param" in userdata, "ENSURE: known param"

        value = userdata.getas(int, "param")
        assert isinstance(value, int)
        assert value == 42

    def test_getas__with_known_param_and_preconverted_value_and_valuetype(self):
        userdata = UserData(param=42)
        assert "param" in userdata, "ENSURE: known param"

        def parse_int(text):
            return int(text)

        value = userdata.getas(parse_int, "param", valuetype=int)
        assert isinstance(value, int)
        assert value == 42

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
        assert value == 123


    def test_getint__with_known_param_and_valid_text(self):
        userdata = UserData(param="42")
        value = userdata.getint("param")
        assert isinstance(value, int)
        assert value ==  42

    def test_getint__with_known_param_and_invalid_text_raises_ValueError(self):
        userdata = UserData(param="__BAD_NUMBER__")
        with pytest.raises(ValueError):
            userdata.getint("param")

    def test_getint__with_unknown_param_without_default_returns_zero(self):
        userdata = UserData()
        value = userdata.getint("param")
        assert value == 0

    def test_getint__with_unknown_param_returns_default_value(self):
        userdata = UserData()
        value = userdata.getint("param", 123)
        assert isinstance(value, int)
        assert value == 123

    def test_getfloat__with_known_param_and_valid_text(self):
        for valid_text in ["1.2", "2", "-1E+3", "+2.34E-5"]:
            userdata = UserData(param=valid_text)
            value = userdata.getfloat("param")
            assert isinstance(value, float)
            assert value == float(valid_text)

    def test_getfloat__with_known_param_and_invalid_text_raises_ValueError(self):
        userdata = UserData(param="__BAD_NUMBER__")
        with pytest.raises(ValueError):
            userdata.getfloat("param")

    def test_getfloat__with_unknown_param_without_default_returns_zero(self):
        userdata = UserData()
        value = userdata.getfloat("param")
        assert value == 0.0

    def test_getfloat__with_unknown_param_returns_default_value(self):
        userdata = UserData()
        value = userdata.getint("param", 1.2)
        assert isinstance(value, float)
        assert value == 1.2


    @pytest.mark.parametrize("text", [
        "true", "TRUE", "True", "yes", "on", "1"
    ])
    def test_getbool__with_known_param_and_valid_true_text(self, text):
        true_text = text
        userdata = UserData(param=true_text)
        value = userdata.getbool("param")
        assert isinstance(value, bool), "text=%s" % true_text
        assert value is True

    @pytest.mark.parametrize("text", [
        "false", "FALSE", "False", "no", "off", "0"
    ])
    def test_getbool__with_known_param_and_valid_false_text(self, text):
        false_text = text
        userdata = UserData(param=false_text)
        value = userdata.getbool("param")
        assert isinstance(value, bool), "text=%s" % false_text
        assert value is False

    def test_getbool__with_known_param_and_invalid_text_raises_ValueError(self):
        userdata = UserData(param="__BAD_VALUE__")
        with pytest.raises(ValueError):
            userdata.getbool("param")

    def test_getbool__with_unknown_param_without_default_returns_false(self):
        userdata = UserData()
        value = userdata.getfloat("param")
        assert value == False

    def test_getbool__with_unknown_param_returns_default_value(self):
        userdata = UserData()
        value = userdata.getint("param", 1.2)
        assert isinstance(value, float)
        assert value == 1.2


class TestUserDataNamespace(object):

    def test_make_scoped(self):
        scoped_name = UserDataNamespace.make_scoped("my.scope", "param")
        assert scoped_name == "my.scope.param"

    def test_make_scoped__with_empty_scope(self):
        scoped_name = UserDataNamespace.make_scoped("", "param")
        assert scoped_name == "param"

    def test_ctor__converts_dict_into_userdata(self):
        userdata = {"my.scope.param1": 12}
        config = UserDataNamespace("my.scope", userdata)
        assert isinstance(config.data, UserData)
        assert config.data is not userdata
        assert config.data == userdata

    def test_ctor__converts_items_into_userdata(self):
        userdata = {"my.scope.param1": 12}
        config = UserDataNamespace("my.scope", userdata.items())
        assert isinstance(config.data, UserData)
        assert config.data is not userdata
        assert config.data == userdata

    def test_ctor__can_assign_userdata_afterwards(self):
        userdata = UserData({"my.scope.param1": 12})
        config = UserDataNamespace("my.scope")
        config.data = userdata
        assert isinstance(config.data, UserData)
        assert config.data is userdata

    def test_get__retrieves_value_when_scoped_param_exists(self):
        userdata = UserData({"my.scope.param1": 12})
        config = UserDataNamespace("my.scope", userdata)
        assert config.get("param1") == 12
        assert config["param1"] == 12

    def test_get__returns_default_when_scoped_param_not_exists(self):
        config = UserDataNamespace("my.scope", UserData({}))
        assert config.get("UNKNOWN_PARAM", "DEFAULT1") == "DEFAULT1"
        assert config.get("UNKNOWN_PARAM", "DEFAULT2") == "DEFAULT2"

    def test_getint__retrieves_value_when_scoped_param_exists(self):
        userdata = UserData({"my.scope.param1": "12"})
        config = UserDataNamespace("my.scope", userdata)
        assert config.getint("param1") == 12

    def test_getint__retrieves_value_when_scoped_param_exists(self):
        userdata = UserData({"my.scope.param2": "12"})
        config = UserDataNamespace("my.scope", userdata)
        assert config.getint("param2") == 12

    def test_getint__returns_default_when_scoped_param_not_exists(self):
        userdata = UserData({})
        config = UserDataNamespace("my.scope", userdata)
        assert config.getint("UNKNOWN_PARAM", 123) == 123
        assert config.getint("UNKNOWN_PARAM", 321) == 321

    def test_getbool__retrieves_value_when_scoped_param_exists(self):
        userdata = UserData({"my.scope.param3": "yes"})
        config = UserDataNamespace("my.scope", userdata)
        assert config.getbool("param3") == True

    def test_getbool__returns_default_when_scoped_param_not_exists(self):
        userdata = UserData({})
        config = UserDataNamespace("my.scope", userdata)
        assert config.getint("UNKNOWN_PARAM", True)  == True
        assert config.getint("UNKNOWN_PARAM", False) == False

    def test_contains__when_scoped_param_exists(self):
        userdata = UserData({"my.scope.param": 12})
        config = UserDataNamespace("my.scope", userdata)
        assert "param" in config
        assert not("param" not in config)

    def test_contains__when_scoped_param_not_exists(self):
        userdata = UserData({"my.scope.param": 12})
        config = UserDataNamespace("my.scope", userdata)
        assert "UNKNOWN_PARAM" not in config
        assert not ("UNKNOWN_PARAM" in config)

    def test_getitem__returns_value_when_param_exists(self):
        userdata = UserData({"my.scope.param": "123"})
        config = UserDataNamespace("my.scope", userdata)
        assert config["param"] == "123"

    def test_getitem__raises_error_when_param_not_exists(self):
        userdata = UserData({"my.scope.param": "123"})
        config = UserDataNamespace("my.scope", userdata)
        with pytest.raises(KeyError):
            _ = config["UNKNOWN_PARAM"]

    def test_setitem__stores_value(self):
        userdata = UserData({"my.scope.param1": "123"})
        config = UserDataNamespace("my.scope", userdata)
        scoped_name = "my.scope.new_param"
        config["new_param"] = 1234
        assert "new_param" in config
        assert config["new_param"] == 1234
        assert scoped_name in config.data
        assert config.data[scoped_name] == 1234

    def test_length__returns_zero_without_params(self):
        userdata = UserData({"my.other_scope.param1": "123"})
        config = UserDataNamespace("my.scope", userdata)
        assert len(config) == 0

    def test_length__with_scoped_params(self):
        userdata1 = UserData({"my.scope.param1": "123"})
        userdata2 = UserData({
            "my.other_scope.param1": "123",
            "my.scope.param1": "123",
            "my.scope.param2": "456",
        })
        userdata3 = UserData({
            "my.other_scope.param1": "123",
            "my.scope.param1": "123",
            "my.scope.param2": "456",
            "my.scope.param3": "789",
            "my.other_scope.param2": "123",
        })
        config = UserDataNamespace("my.scope")
        config.data = userdata1
        assert len(config) == 1
        config.data = userdata2
        assert len(config) == 2
        config.data = userdata3
        assert len(config) == 3

    def test_scoped_keys__with_scoped_params(self):
        userdata = UserData({
            "my.other_scope.param1": "123",
            "my.scope.param1": "123",
            "my.scope.param2": "456",
            "my.other_scope.param2": "123",
        })
        config = UserDataNamespace("my.scope", userdata)
        assert sorted(config.scoped_keys()) == ["my.scope.param1", "my.scope.param2"]

    def test_keys__with_scoped_params(self):
        userdata = UserData({
            "my.other_scope.param1": "__OTHER1__",
            "my.scope.param1": "123",
            "my.scope.param2": "456",
            "my.other_scope.param2": "__OTHER2__",
        })
        config = UserDataNamespace("my.scope", userdata)
        assert sorted(config.keys()) == ["param1", "param2"]

    def test_values__with_scoped_params(self):
        userdata = UserData({
            "my.other_scope.param1": "__OTHER1__",
            "my.scope.param1": "123",
            "my.scope.param2": "456",
            "my.other_scope.param2": "__OTHER2__",
        })
        config = UserDataNamespace("my.scope", userdata)
        assert sorted(config.values()) == ["123", "456"]

    def test_items__with_scoped_params(self):
        userdata = UserData({
            "my.other_scope.param1": "__OTHER1__",
            "my.scope.param1": "123",
            "my.scope.param2": "456",
            "my.other_scope.param2": "__OTHER2__",
        })
        config = UserDataNamespace("my.scope", userdata)
        assert sorted(config.items()) == [("param1", "123"), ("param2", "456")]
