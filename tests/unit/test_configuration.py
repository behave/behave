import os.path
import sys
import tempfile
import six
import pytest
from behave import configuration
from behave.configuration import Configuration, UserData
from unittest import TestCase


# one entry of each kind handled
# configparser and toml
TEST_CONFIGS = [
    (
        ".behaverc",
        """[behave]
outfiles= /absolute/path1
          relative/path2
paths = /absolute/path3
        relative/path4
default_tags = @foo,~@bar
       @zap
format=pretty
       tag-counter
stdout_capture=no
bogus=spam

[behave.userdata]
foo    = bar
answer = 42
"""),
    (
        "pyproject.toml",
        """[tool.behave]
outfiles = ["/absolute/path1", "relative/path2"]
paths = ["/absolute/path3", "relative/path4"]
default_tags = ["@foo,~@bar", "@zap"]
format = ["pretty", "tag-counter"]
stdout_capture = false
bogus = "spam"

[tool.behave.userdata]
foo    = "bar"
answer = 42
""")
]

# -----------------------------------------------------------------------------
# TEST SUPPORT:
# -----------------------------------------------------------------------------
ROOTDIR_PREFIX = ""
if sys.platform.startswith("win"):
    # -- OR: ROOTDIR_PREFIX = os.path.splitdrive(sys.executable)
    # NOTE: python2 requires lower-case drive letter.
    ROOTDIR_PREFIX_DEFAULT = "C:"
    if six.PY2:
        ROOTDIR_PREFIX_DEFAULT = ROOTDIR_PREFIX_DEFAULT.lower()
    ROOTDIR_PREFIX = os.environ.get("BEHAVE_ROOTDIR_PREFIX", ROOTDIR_PREFIX_DEFAULT)


# -----------------------------------------------------------------------------
# TEST SUITE:
# -----------------------------------------------------------------------------
class TestConfiguration(object):

    @pytest.mark.parametrize(
        ("filename", "contents"),
        list(TEST_CONFIGS)
    )
    def test_read_file(self, filename, contents):
        tndir = tempfile.mkdtemp()
        file_path = os.path.normpath(os.path.join(tndir, filename))
        with open(file_path, "w") as fp:
            fp.write(contents)
        # -- WINDOWS-REQUIRES: normpath
        d = configuration.read_configuration(file_path)
        assert d["outfiles"] == [
            os.path.normpath(ROOTDIR_PREFIX + "/absolute/path1"),
            os.path.normpath(os.path.join(tndir, "relative/path2")),
        ]
        assert d["paths"] == [
            os.path.normpath(ROOTDIR_PREFIX + "/absolute/path3"),
            os.path.normpath(os.path.join(tndir, "relative/path4")),
            ]
        assert d["format"] == ["pretty", "tag-counter"]
        assert d["default_tags"] == ["@foo,~@bar", "@zap"]
        assert d["stdout_capture"] is False
        assert "bogus" not in d
        assert d["userdata"] == {"foo": "bar", "answer": "42"}

    def ensure_stage_environment_is_not_set(self):
        if "BEHAVE_STAGE" in os.environ:
            del os.environ["BEHAVE_STAGE"]

    def test_settings_without_stage(self):
        # -- OR: Setup with default, unnamed stage.
        self.ensure_stage_environment_is_not_set()
        assert "BEHAVE_STAGE" not in os.environ
        config = Configuration("")
        assert "steps" == config.steps_dir
        assert "environment.py" == config.environment_file

    def test_settings_with_stage(self):
        config = Configuration(["--stage=STAGE1"])
        assert "STAGE1_steps" == config.steps_dir
        assert "STAGE1_environment.py" == config.environment_file

    def test_settings_with_stage_and_envvar(self):
        os.environ["BEHAVE_STAGE"] = "STAGE2"
        config = Configuration(["--stage=STAGE1"])
        assert "STAGE1_steps" == config.steps_dir
        assert "STAGE1_environment.py" == config.environment_file
        del os.environ["BEHAVE_STAGE"]

    def test_settings_with_stage_from_envvar(self):
        os.environ["BEHAVE_STAGE"] = "STAGE2"
        config = Configuration("")
        assert "STAGE2_steps" == config.steps_dir
        assert "STAGE2_environment.py" == config.environment_file
        del os.environ["BEHAVE_STAGE"]


# -----------------------------------------------------------------------------
# TEST SUITE:
# -----------------------------------------------------------------------------
class TestConfigurationUserData(TestCase):
    """Test userdata aspects in behave.configuration.Configuration class."""

    def test_cmdline_defines(self):
        config = Configuration([
            "-D", "foo=foo_value",
            "--define=bar=bar_value",
            "--define", "baz=BAZ_VALUE",
        ])
        assert "foo_value" == config.userdata["foo"]
        assert "bar_value" == config.userdata["bar"]
        assert "BAZ_VALUE" == config.userdata["baz"]

    def test_cmdline_defines_override_configfile(self):
        userdata_init = {"foo": "XXX", "bar": "ZZZ", "baz": 42}
        config = Configuration(
                    "-D foo=foo_value --define bar=123",
                    load_config=False, userdata=userdata_init)
        assert "foo_value" == config.userdata["foo"]
        assert "123" == config.userdata["bar"]
        assert 42 == config.userdata["baz"]

    def test_cmdline_defines_without_value_are_true(self):
        config = Configuration("-D foo --define bar -Dbaz")
        assert "true" == config.userdata["foo"]
        assert "true" == config.userdata["bar"]
        assert "true" == config.userdata["baz"]
        assert True == config.userdata.getbool("foo")

    def test_cmdline_defines_with_empty_value(self):
        config = Configuration("-D foo=")
        assert "" == config.userdata["foo"]

    def test_cmdline_defines_with_assign_character_as_value(self):
        config = Configuration("-D foo=bar=baz")
        assert "bar=baz" == config.userdata["foo"]

    def test_cmdline_defines__with_quoted_name_value_pair(self):
        cmdlines = [
            '-D "person=Alice and Bob"',
            "-D 'person=Alice and Bob'",
        ]
        for cmdline in cmdlines:
            config = Configuration(cmdline, load_config=False)
            assert config.userdata == dict(person="Alice and Bob")

    def test_cmdline_defines__with_quoted_value(self):
        cmdlines = [
            '-D person="Alice and Bob"',
            "-D person='Alice and Bob'",
        ]
        for cmdline in cmdlines:
            config = Configuration(cmdline, load_config=False)
            assert config.userdata == dict(person="Alice and Bob")

    def test_setup_userdata(self):
        config = Configuration("", load_config=False)
        config.userdata = dict(person1="Alice", person2="Bob")
        config.userdata_defines = [("person2", "Charly")]
        config.setup_userdata()

        expected_data = dict(person1="Alice", person2="Charly")
        assert config.userdata == expected_data

    def test_update_userdata__with_cmdline_defines(self):
        # -- NOTE: cmdline defines are reapplied.
        config = Configuration("-D person2=Bea", load_config=False)
        config.userdata = UserData(person1="AAA", person3="Charly")
        config.update_userdata(dict(person1="Alice", person2="Bob"))

        expected_data = dict(person1="Alice", person2="Bea", person3="Charly")
        assert config.userdata == expected_data
        assert config.userdata_defines == [("person2", "Bea")]

    def test_update_userdata__without_cmdline_defines(self):
        config = Configuration("", load_config=False)
        config.userdata = UserData(person1="AAA", person3="Charly")
        config.update_userdata(dict(person1="Alice", person2="Bob"))

        expected_data = dict(person1="Alice", person2="Bob", person3="Charly")
        assert config.userdata == expected_data
        assert config.userdata_defines is None
