import os.path
import sys
import tempfile
import six
import pytest
from behave import configuration
from behave.api.runner import IRunner
from behave.configuration import Configuration, UserData
from behave.exception import ClassNotFoundError, InvalidClassError
from behave.runner import Runner as DefaultRunnerClass
from behave.runner_plugin import RunnerPlugin
from unittest import TestCase


# one entry of each kind handled
TEST_CONFIG="""[behave]
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
"""

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

    def test_read_file(self):
        tn = tempfile.mktemp()
        tndir = os.path.dirname(tn)
        with open(tn, "w") as f:
            f.write(TEST_CONFIG)

        # -- WINDOWS-REQUIRES: normpath
        d = configuration.read_configuration(tn)
        assert d["outfiles"] ==[
            os.path.normpath(ROOTDIR_PREFIX + "/absolute/path1"),
            os.path.normpath(os.path.join(tndir, "relative/path2")),
        ]
        assert d["paths"] == [
            os.path.normpath(ROOTDIR_PREFIX + "/absolute/path3"),
            os.path.normpath(os.path.join(tndir, "relative/path4")),
            ]
        assert d["format"] == ["pretty", "tag-counter"]
        assert d["default_tags"] == ["@foo,~@bar", "@zap"]
        assert d["stdout_capture"] == False
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
# TEST SUPPORT:
# -----------------------------------------------------------------------------
# -- TEST-RUNNER CLASS EXAMPLES:
class CustomTestRunner(IRunner):
    """Custom, dummy runner"""

    def __init__(self, config, **kwargs):
        self.config = config

    def run(self):
        return True     # OOPS: Failed.


# -- BAD TEST-RUNNER CLASS EXAMPLES:
# PROBLEM: Is not a class
INVALID_TEST_RUNNER_CLASS0 = True


class InvalidTestRunner1(object):
    """PROBLEM: Missing IRunner.register(InvalidTestRunner)."""
    def run(self, features): pass


class InvalidTestRunner2(IRunner):
    """PROBLEM: run() method signature differs"""
    def run(self, features): pass


# -----------------------------------------------------------------------------
# TEST SUITE:
# -----------------------------------------------------------------------------
class TestConfigurationRunner(object):
    """Test the runner-plugin configuration."""

    def test_runner_default(self, capsys):
        config = Configuration("")
        runner = RunnerPlugin().make_runner(config)
        assert config.runner == configuration.DEFAULT_RUNNER_CLASS_NAME
        assert isinstance(runner, DefaultRunnerClass)

    def test_runner_with_normal_runner_class(self, capsys):
        config = Configuration(["--runner=behave.runner:Runner"])
        runner = RunnerPlugin().make_runner(config)
        assert isinstance(runner, DefaultRunnerClass)

    def test_runner_with_own_runner_class(self):
        config = Configuration(["--runner=tests.unit.test_configuration:CustomTestRunner"])
        runner = RunnerPlugin().make_runner(config)
        assert isinstance(runner, CustomTestRunner)

    def test_runner_with_unknown_module(self, capsys):
        with pytest.raises(ImportError):
            config = Configuration(["--runner=unknown_module:Runner"])
            runner = RunnerPlugin().make_runner(config)
        captured = capsys.readouterr()
        if six.PY2:
            assert "No module named unknown_module" in captured.out
        else:
            assert "No module named 'unknown_module'" in captured.out

    def test_runner_with_unknown_class(self, capsys):
        with pytest.raises(ClassNotFoundError) as exc_info:
            config = Configuration(["--runner=behave.runner:UnknownRunner"])
            RunnerPlugin().make_runner(config)

        captured = capsys.readouterr()
        assert "FAILED to load runner-class" in captured.out
        assert "ClassNotFoundError: behave.runner:UnknownRunner" in captured.out

        expected = "behave.runner:UnknownRunner"
        assert exc_info.type is ClassNotFoundError
        assert exc_info.match(expected)

    def test_runner_with_invalid_runner_class0(self):
        with pytest.raises(TypeError) as exc_info:
            config = Configuration(["--runner=tests.unit.test_configuration:INVALID_TEST_RUNNER_CLASS0"])
            RunnerPlugin().make_runner(config)

        expected = "tests.unit.test_configuration:INVALID_TEST_RUNNER_CLASS0: not a class"
        assert exc_info.type is InvalidClassError
        assert exc_info.match(expected)

    def test_runner_with_invalid_runner_class1(self):
        with pytest.raises(TypeError) as exc_info:
            config = Configuration(["--runner=tests.unit.test_configuration:InvalidTestRunner1"])
            RunnerPlugin().make_runner(config)

        expected = "tests.unit.test_configuration:InvalidTestRunner1: not subclass-of behave.api.runner.IRunner"
        assert exc_info.type is InvalidClassError
        assert exc_info.match(expected)

    def test_runner_with_invalid_runner_class2(self):
        with pytest.raises(TypeError) as exc_info:
            config = Configuration(["--runner=tests.unit.test_configuration:InvalidTestRunner2"])
            RunnerPlugin().make_runner(config)

        expected = "Can't instantiate abstract class InvalidTestRunner2 with abstract methods __init__"
        assert exc_info.type is TypeError
        assert exc_info.match(expected)


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
