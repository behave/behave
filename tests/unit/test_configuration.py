from __future__ import absolute_import, print_function
from contextlib import contextmanager
import os.path
from pathlib import Path
import sys
import six
import pytest
from behave import configuration
from behave.configuration import (
    Configuration,
    UserData,
    configfile_options_iter
)
from behave.tag_expression import TagExpressionProtocol
from unittest import TestCase


# one entry of each kind handled
# configparser and toml
TEST_CONFIGS = [
    (".behaverc", """[behave]
outfiles= /absolute/path1
          relative/path2
paths = /absolute/path3
        relative/path4
default_tags = (@foo and not @bar) or @zap
format=pretty
       tag-counter
capture_stdout=no
bogus=spam

[behave.userdata]
foo    = bar
answer = 42
"""),

    # -- TOML CONFIG-FILE:
    ("pyproject.toml", """[tool.behave]
outfiles = ["/absolute/path1", "relative/path2"]
paths = ["/absolute/path3", "relative/path4"]
default_tags = ["(@foo and not @bar) or @zap"]
format = ["pretty", "tag-counter"]
capture_stdout = false
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


@contextmanager
def use_current_directory(directory_path):
    """Use directory as current directory.

    ::

        with use_current_directory("/tmp/some_directory"):
            pass # DO SOMETHING in current directory.
        # -- ON EXIT: Restore old current-directory.
    """
    # -- COMPATIBILITY: Use directory-string instead of Path
    initial_directory = str(Path.cwd())
    try:
        os.chdir(str(directory_path))
        yield directory_path
    finally:
        os.chdir(initial_directory)


# -----------------------------------------------------------------------------
# TEST SUITE:
# -----------------------------------------------------------------------------
class TestConfiguration(object):

    @pytest.mark.parametrize(("filename", "contents"), list(TEST_CONFIGS))
    def test_read_file(self, filename, contents, tmp_path):
        tndir = str(tmp_path)
        file_path = os.path.normpath(os.path.join(tndir, filename))
        with open(file_path, "w") as fp:
            fp.write(contents)

        # -- WINDOWS-REQUIRES: normpath
        # DISABLED: pprint(d, sort_dicts=True)
        from pprint import pprint
        extra_kwargs = {}
        if six.PY3:
            extra_kwargs = {"sort_dicts": True}

        d = configuration.read_configuration(file_path)
        pprint(d, **extra_kwargs)
        assert d["outfiles"] == [
            os.path.normpath(ROOTDIR_PREFIX + "/absolute/path1"),
            os.path.normpath(os.path.join(tndir, "relative/path2")),
        ]
        assert d["paths"] == [
            os.path.normpath(ROOTDIR_PREFIX + "/absolute/path3"),
            os.path.normpath(os.path.join(tndir, "relative/path4")),
            ]
        assert d["format"] == ["pretty", "tag-counter"]
        assert d["default_tags"] == ["(@foo and not @bar) or @zap"]
        assert d["capture_stdout"] is False
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
        assert config.userdata.getbool("foo") is True

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


class TestConfigFileParser(object):

    def test_configfile_iter__verify_option_names(self):
        config_options = configfile_options_iter(None)
        config_options_names = [opt[0] for opt in config_options]
        expected_names = [
            "capture",
            "capture_hooks",
            "capture_log",
            "capture_stderr",
            "capture_stdout",
            "color",
            "default_format",
            "default_tags",
            "dry_run",
            "exclude_re",
            "format",
            "include_re",
            "jobs",
            "junit",
            "junit_directory",
            "lang",
            "logging_clear_handlers",
            "logging_datefmt",
            "logging_filter",
            "logging_format",
            "logging_level",
            "name",
            "outfiles",
            "paths",
            "quiet",
            "runner",
            "scenario_outline_annotation_schema",
            "show_multiline",
            "show_skipped",
            "show_snippets",
            "show_source",
            "show_timings",
            "stage",
            "steps_catalog",
            "stop",
            "summary",
            "tag_expression_protocol",
            "tags",
            "verbose",
            "wip",
        ]
        assert sorted(config_options_names) == expected_names


class TestConfigFile(object):

    @staticmethod
    def make_config_file_with_tag_expression_protocol(value, tmp_path):
        config_file = tmp_path / "behave.ini"
        config_file.write_text(u"""
[behave]
tag_expression_protocol = {value}
""".format(value=value))
        assert config_file.exists()

    @classmethod
    def check_tag_expression_protocol_with_valid_value(cls, value, tmp_path):
        TagExpressionProtocol.use(TagExpressionProtocol.DEFAULT)
        cls.make_config_file_with_tag_expression_protocol(value, tmp_path)
        with use_current_directory(tmp_path):
            config = Configuration([])
            print("USE: tag_expression_protocol.value={0}".format(value))
            print("USE: config.tag_expression_protocol={0}".format(
                config.tag_expression_protocol))

        assert config.tag_expression_protocol in TagExpressionProtocol
        assert TagExpressionProtocol.current() is config.tag_expression_protocol

    @pytest.mark.parametrize("value", TagExpressionProtocol.choices())
    def test_tag_expression_protocol(self, value, tmp_path):
        self.check_tag_expression_protocol_with_valid_value(value, tmp_path)

    @pytest.mark.parametrize("value", [
        "v1", "V1",
        "v2", "V2",
        "auto_detect", "AUTO_DETECT", "Auto_detect",
        # -- DEPRECATING:
        "strict", "STRICT", "Strict",
    ])
    def test_tag_expression_protocol__is_not_case_sensitive(self, value, tmp_path):
        self.check_tag_expression_protocol_with_valid_value(value, tmp_path)

    @pytest.mark.parametrize("value", [
        "__UNKNOWN__",
        # -- SIMILAR: to valid values
        "v1_", "_v2",
        ".auto", "auto_detect.",
        "_strict", "strict_"
    ])
    def test_tag_expression_protocol__with_invalid_value_raises_error(self, value, tmp_path):
        default_value = TagExpressionProtocol.DEFAULT
        TagExpressionProtocol.use(default_value)
        self.make_config_file_with_tag_expression_protocol(value, tmp_path)
        with use_current_directory(tmp_path):
            with pytest.raises(ValueError) as exc_info:
                config = Configuration([])
                print("USE: tag_expression_protocol.value={0}".format(value))
                print("USE: config.tag_expression_protocol={0}".format(
                    config.tag_expression_protocol))

        choices = ", ".join(TagExpressionProtocol.choices())
        expected = "{value} (expected: {choices})".format(value=value, choices=choices)
        assert TagExpressionProtocol.current() is default_value
        assert exc_info.type is ValueError
        assert expected in str(exc_info.value)
