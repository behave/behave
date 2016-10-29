import os.path
import sys
import tempfile
from nose.tools import *
from behave import configuration
from behave.configuration import Configuration, UserData
from unittest import TestCase


# one entry of each kind handled
TEST_CONFIG="""[behave]
outfiles= /absolute/path1
          relative/path2
paths = /absolute/path3
        relative/path4
tags = @foo,~@bar
       @zap
format=pretty
       tag-counter
stdout_capture=no
bogus=spam

[behave.userdata]
foo    = bar
answer = 42
"""


ROOTDIR_PREFIX = ""
if sys.platform.startswith("win"):
    # -- OR: ROOTDIR_PREFIX = os.path.splitdrive(sys.executable)
    # NOTE: python2 requires lower-case drive letter.
    ROOTDIR_PREFIX = os.environ.get("BEHAVE_ROOTDIR_PREFIX", "c:")

class TestConfiguration(object):

    def test_read_file(self):
        tn = tempfile.mktemp()
        tndir = os.path.dirname(tn)
        with open(tn, "w") as f:
            f.write(TEST_CONFIG)

        # -- WINDOWS-REQUIRES: normpath
        d = configuration.read_configuration(tn)
        eq_(d["outfiles"], [
            os.path.normpath(ROOTDIR_PREFIX + "/absolute/path1"),
            os.path.normpath(os.path.join(tndir, "relative/path2")),
        ])
        eq_(d["paths"], [
            os.path.normpath(ROOTDIR_PREFIX + "/absolute/path3"),
            os.path.normpath(os.path.join(tndir, "relative/path4")),
            ])
        eq_(d["format"], ["pretty", "tag-counter"])
        eq_(d["tags"], ["@foo,~@bar", "@zap"])
        eq_(d["stdout_capture"], False)
        ok_("bogus" not in d)
        eq_(d["userdata"], {"foo": "bar", "answer": "42"})

    def ensure_stage_environment_is_not_set(self):
        if "BEHAVE_STAGE" in os.environ:
            del os.environ["BEHAVE_STAGE"]

    def test_settings_without_stage(self):
        # -- OR: Setup with default, unnamed stage.
        self.ensure_stage_environment_is_not_set()
        assert "BEHAVE_STAGE" not in os.environ
        config = Configuration("")
        eq_("steps", config.steps_dir)
        eq_("environment.py", config.environment_file)

    def test_settings_with_stage(self):
        config = Configuration(["--stage=STAGE1"])
        eq_("STAGE1_steps", config.steps_dir)
        eq_("STAGE1_environment.py", config.environment_file)

    def test_settings_with_stage_and_envvar(self):
        os.environ["BEHAVE_STAGE"] = "STAGE2"
        config = Configuration(["--stage=STAGE1"])
        eq_("STAGE1_steps", config.steps_dir)
        eq_("STAGE1_environment.py", config.environment_file)
        del os.environ["BEHAVE_STAGE"]

    def test_settings_with_stage_from_envvar(self):
        os.environ["BEHAVE_STAGE"] = "STAGE2"
        config = Configuration("")
        eq_("STAGE2_steps", config.steps_dir)
        eq_("STAGE2_environment.py", config.environment_file)
        del os.environ["BEHAVE_STAGE"]


class TestConfigurationUserData(TestCase):
    """Test userdata aspects in behave.configuration.Configuration class."""

    def test_cmdline_defines(self):
        config = Configuration([
            "-D", "foo=foo_value",
            "--define=bar=bar_value",
            "--define", "baz=BAZ_VALUE",
        ])
        eq_("foo_value", config.userdata["foo"])
        eq_("bar_value", config.userdata["bar"])
        eq_("BAZ_VALUE", config.userdata["baz"])

    def test_cmdline_defines_override_configfile(self):
        userdata_init = {"foo": "XXX", "bar": "ZZZ", "baz": 42}
        config = Configuration(
                    "-D foo=foo_value --define bar=123",
                    load_config=False, userdata=userdata_init)
        eq_("foo_value", config.userdata["foo"])
        eq_("123", config.userdata["bar"])
        eq_(42, config.userdata["baz"])

    def test_cmdline_defines_without_value_are_true(self):
        config = Configuration("-D foo --define bar -Dbaz")
        eq_("true", config.userdata["foo"])
        eq_("true", config.userdata["bar"])
        eq_("true", config.userdata["baz"])
        eq_(True, config.userdata.getbool("foo"))

    def test_cmdline_defines_with_empty_value(self):
        config = Configuration("-D foo=")
        eq_("", config.userdata["foo"])

    def test_cmdline_defines_with_assign_character_as_value(self):
        config = Configuration("-D foo=bar=baz")
        eq_("bar=baz", config.userdata["foo"])

    def test_cmdline_defines__with_quoted_name_value_pair(self):
        cmdlines = [
            '-D "person=Alice and Bob"',
            "-D 'person=Alice and Bob'",
        ]
        for cmdline in cmdlines:
            config = Configuration(cmdline, load_config=False)
            eq_(config.userdata, dict(person="Alice and Bob"))

    def test_cmdline_defines__with_quoted_value(self):
        cmdlines = [
            '-D person="Alice and Bob"',
            "-D person='Alice and Bob'",
        ]
        for cmdline in cmdlines:
            config = Configuration(cmdline, load_config=False)
            eq_(config.userdata, dict(person="Alice and Bob"))

    def test_setup_userdata(self):
        config = Configuration("", load_config=False)
        config.userdata = dict(person1="Alice", person2="Bob")
        config.userdata_defines = [("person2", "Charly")]
        config.setup_userdata()

        expected_data = dict(person1="Alice", person2="Charly")
        eq_(config.userdata, expected_data)

    def test_update_userdata__with_cmdline_defines(self):
        # -- NOTE: cmdline defines are reapplied.
        config = Configuration("-D person2=Bea", load_config=False)
        config.userdata = UserData(person1="AAA", person3="Charly")
        config.update_userdata(dict(person1="Alice", person2="Bob"))

        expected_data = dict(person1="Alice", person2="Bea", person3="Charly")
        eq_(config.userdata, expected_data)
        eq_(config.userdata_defines, [("person2", "Bea")])

    def test_update_userdata__without_cmdline_defines(self):
        config = Configuration("", load_config=False)
        config.userdata = UserData(person1="AAA", person3="Charly")
        config.update_userdata(dict(person1="Alice", person2="Bob"))

        expected_data = dict(person1="Alice", person2="Bob", person3="Charly")
        eq_(config.userdata, expected_data)
        self.assertFalse(config.userdata_defines)
