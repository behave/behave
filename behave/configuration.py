# -*- coding: UTF-8 -*-
# pylint: disable=redundant-u-string-prefix
# pylint: disable=consider-using-f-string
# pylint: disable=too-many-lines
# pylint: disable=useless-object-inheritance
# pylint: disable=use-dict-literal
"""
This module provides the configuration for :mod:`behave`:

* Configuration object(s)
* config-file loading and storing params in Configuration object(s)
* command-line parsing and storing params in Configuration object(s)
"""

from __future__ import absolute_import, print_function
import argparse
from collections import namedtuple
import json
import logging
import os
import re
import sys
import shlex
import six
import warnings
from six.moves import configparser

from behave._types import Unknown
from behave.exception import ConfigParamTypeError
from behave.model_type import FileLocation
from behave.formatter.base import StreamOpener
from behave.tag_expression import TagExpressionProtocol
from behave.textutil import select_best_encoding, to_texts
from behave.userdata import UserData, parse_user_define


# -- APPLY CONFIG SETTINGS: Use LATE-IMPORT to avoid dependency coupling.
# from behave.formatter import _registry as _format_registry
# from behave.log_config import LoggingConfigurator
# from behave.model import ScenarioOutline
# from behave.reporter.junit import JUnitReporter
# from behave.reporter.summary import SummaryReporter
# from behave.tag_expression import  make_tag_expression

# -- PYTHON 2/3 COMPATIBILITY:
# SINCE Python 3.2: ConfigParser = SafeConfigParser
ConfigParser = configparser.ConfigParser
if six.PY2:  # pragma: no cover
    ConfigParser = configparser.SafeConfigParser

# -- OPTIONAL TOML SUPPORT: Using "pyproject.toml" as config-file
_TOML_AVAILABLE = True
if _TOML_AVAILABLE:  # pragma: no cover
    try:
        if sys.version_info >= (3, 11):
            import tomllib
        elif sys.version_info < (3, 0):
            import toml as tomllib
        else:
            import tomli as tomllib
    except ImportError:
        _TOML_AVAILABLE = False


# -----------------------------------------------------------------------------
# CONSTANTS:
# -----------------------------------------------------------------------------
DEFAULT_RUNNER_CLASS_NAME = "behave.runner:Runner"


# -----------------------------------------------------------------------------
# CONFIGURATION DATA TYPES and TYPE CONVERTERS:
# -----------------------------------------------------------------------------
class LogLevel(object):
    names = [
        "NOTSET", "CRITICAL", "FATAL", "ERROR",
        "WARNING", "WARN", "INFO", "DEBUG",
    ]

    @staticmethod
    def parse(levelname, unknown_level=None):
        """
        Convert levelname into a numeric log level.

        :param levelname: Logging levelname (as string)
        :param unknown_level: Used if levelname is unknown (optional).
        :return: Numeric log-level or unknown_level, if levelname is unknown.
        """
        return getattr(logging, levelname.upper(), unknown_level)

    @classmethod
    def parse_type(cls, levelname):
        level = cls.parse(levelname, Unknown)
        if level is Unknown:
            message = "%s is unknown, use: %s" % \
                      (levelname, ", ".join(cls.names[1:]))
            raise argparse.ArgumentTypeError(message)
        return level

    @staticmethod
    def to_string(level):
        return logging.getLevelName(level)


def positive_number(text):
    """Converts a string into a positive integer number."""
    value = int(text)
    if value < 0:
        raise ValueError("POSITIVE NUMBER, but was: %s" % text)
    return value


# -----------------------------------------------------------------------------
# CONFIGURATION SCHEMA:
# -----------------------------------------------------------------------------
COLOR_CHOICES = ["auto", "on", "off", "always", "never"]
COLOR_DEFAULT = os.getenv("BEHAVE_COLOR", "auto")
COLOR_DEFAULT_OFF = "off"
COLOR_ON_VALUES = ("on", "always")
COLOR_OFF_VALUES = ("off", "never")


OPTIONS = [
    (("-C", "--no-color"),
     dict(dest="color", action="store_const", const=COLOR_DEFAULT_OFF,
          help="Disable colored mode.")),

    (("--color",),
     dict(dest="color", choices=COLOR_CHOICES,
          default=COLOR_DEFAULT, const=COLOR_DEFAULT, nargs="?",
          help="""Use colored mode or not (default: %(default)s).""")),

    (("-d", "--dry-run"),
     dict(action="store_true",
          help="Invokes formatters without executing the steps.")),

    (("-D", "--define"),
     dict(dest="userdata_defines", type=parse_user_define, action="append",
          metavar="NAME=VALUE",
          help="""Define user-specific data for the config.userdata dictionary.
                  Example: -D foo=bar to store it in config.userdata["foo"].""")),

    (("-e", "--exclude"),
     dict(metavar="PATTERN", dest="exclude_re",
          help="""Don't run feature files matching regular expression
                  PATTERN.""")),

    (("-i", "--include"),
     dict(metavar="PATTERN", dest="include_re",
          help="Only run feature files matching regular expression PATTERN.")),

    (("--no-junit",),
     dict(action="store_false", dest="junit",
          help="Don't output JUnit-compatible reports.")),

    (("--junit",),
     dict(action="store_true",
          help="""Output JUnit-compatible reports.
                  When junit is enabled, all stdout and stderr
                  will be redirected and dumped to the junit report,
                  regardless of the "--capture" and "--no-capture" options.
                  """)),

    (("--junit-directory",),
     dict(metavar="PATH", dest="junit_directory",
          default="reports",
          help="""Directory in which to store JUnit reports.""")),

    (("-j", "--jobs", "--parallel"),
     dict(metavar="NUMBER", dest="jobs", default=1, type=positive_number,
          help="""Number of concurrent jobs to use (default: %(default)s).
                  Only supported by test runners that support parallel execution.
                  """)),

    ((),  # -- CONFIGFILE only
     dict(dest="default_format", default="pretty",
          help="Specify default formatter (default: %(default)s).")),


    (("-f", "--format"),
     dict(dest="format", action="append", metavar="FORMATTER",
          help="""Specify a formatter. If none is specified the default
                  formatter is used. Pass "--format help" to get a
                  list of available formatters.""")),

    (("--steps-catalog",),
     dict(dest="steps_catalog", action="store_true",
          help="""Show a catalog of all available step definitions.
                  SAME AS: "--format=steps.catalog --dry-run --no-summary -q".""")),

    ((),  # -- CONFIGFILE only
     dict(dest="scenario_outline_annotation_schema",
          help="""Specify name annotation schema for scenario outline
                  (default="{name} -- @{row.id} {examples.name}").""")),

    ((),  # -- CONFIGFILE only
     dict(dest="use_nested_step_modules", action="store_true",
          type=bool, default=False,
          help="""Use subdirectories of steps directory to import steps
                  (default: false).""")),

    (("--no-skipped",),
     dict(dest="show_skipped", action="store_false",
          help="Don't print skipped steps (due to tags).")),

    (("--show-skipped",),
     dict(action="store_true",
          help="""Print skipped steps.
                  This is the default behaviour. This switch is used to
                  override a configuration file setting.""")),

    (("--no-snippets",),
     dict(dest="show_snippets", action="store_false",
          help="Don't print snippets for unimplemented steps.")),
    (("--snippets",),
     dict(dest="show_snippets", action="store_true",
          help="""Print snippets for unimplemented steps.
                  This is the default behaviour. This switch is used to
                  override a configuration file setting.""")),

    (("--no-multiline",),
     dict(dest="show_multiline", action="store_false",
          help="""Don't print multiline strings and tables under steps.""")),

    (("--multiline", ),
     dict(dest="show_multiline", action="store_true",
          help="""Print multiline strings and tables under steps.
                  This is the default behaviour. This switch is used to
                  override a configuration file setting.""")),

    (("-n", "--name"),
     dict(dest="name", action="append", metavar="NAME_PATTERN",
          help="""Select feature elements (scenarios, ...) to run
                  which match part of the given name (regex pattern).
                  If this option is given more than once,
                  it will match against all the given names.""")),

    (("--capture",),
     dict(dest="capture", action="store_true",
          help="""Enable capture mode (stdout/stderr/log-output).
                  Any capture output will be printed on a failure/error.""")),

    (("--no-capture",),
     dict(dest="capture", action="store_false",
          help="""Disable capture mode (stdout/stderr/log-output).""")),

    (("--capture-stdout",),
     dict(dest="capture_stdout", action="store_true",
          help="""Enable capture of stdout.""")),

    (("--no-capture-stdout",),
     dict(dest="capture_stdout", action="store_false",
          help="""Disable capture of stdout.""")),

    (("--capture-stderr",),
     dict(dest="capture_stderr", action="store_true",
          help="""Enable capture of stderr.""")),

    (("--no-capture-stderr",),
     dict(dest="capture_stderr", action="store_false",
          help="""Disable capture of stderr.""")),

    (("--capture-log",
      # -- OLD-NAME:
      "--logcapture",),
     dict(dest="capture_log", action="store_true",
          help="""Enable capture of logging output.""")),

    (("--no-capture-log",
      # -- OLD-NAME:
      "--no-logcapture",),
     dict(dest="capture_log", action="store_false",
          help="""Disable capture of logging output.""")),

    (("--capture-hooks",),
     dict(dest="capture_hooks", action="store_true",
          help="""Enable capture of hooks (except: before_all).""")),

    (("--no-capture-hooks",),
     dict(dest="capture_hooks", action="store_false",
          help="""Disable capture of hooks.""")),

    (("--logging-level",),
     dict(type=LogLevel.parse_type, default=logging.INFO, metavar="LOG_LEVEL",
          help="""Specify a level to capture logging at. The default
                  is INFO - capturing everything.""")),

    (("--logging-format",),
     dict(metavar="LOG_FORMAT",
         help="""Specify custom format to print statements. Uses the
                  same format as used by standard logging handlers. The
                  default is "%%(levelname)s:%%(name)s:%%(message)s".""")),

    (("--logging-datefmt",),
     dict(metavar="LOG_DATE_FORMAT",
          help="""Specify custom date/time format to print
                  statements.
                  Uses the same format as used by standard logging
                  handlers.""")),

    (("--logging-filter",),
     dict(metavar="LOG_FILTER",
         help="""Specify which statements to filter in/out. By default,
                  everything is captured. If the output is too verbose, use
                  this option to filter out needless output.
                  Example: --logging-filter=foo will capture statements issued
                  ONLY to foo or foo.what.ever.sub but not foobar or other
                  logger. Specify multiple loggers with comma:
                  filter=foo,bar,baz.
                  If any logger name is prefixed with a minus, eg filter=-foo,
                  it will be excluded rather than included.""",
          config_help="""Specify which statements to filter in/out. By default,
                         everything is captured. If the output is too verbose,
                         use this option to filter out needless output.
                         Example: ``logging_filter = foo`` will capture
                         statements issued ONLY to "foo" or "foo.what.ever.sub"
                         but not "foobar" or other logger. Specify multiple
                         loggers with comma: ``logging_filter = foo,bar,baz``.
                         If any logger name is prefixed with a minus, eg
                         ``logging_filter = -foo``, it will be excluded rather
                         than included.""")),

    (("--logging-clear-handlers",),
     dict(action="store_true",
          help="Clear existing logging handlers (during capture-log).")),
    (("--no-logging-clear-handlers",),
     dict(action="store_false",
          help="Keep existing logging handlers (during capture-log).")),

    (("--no-summary",),
     dict(action="store_false", dest="summary",
          help="""Don't display the summary at the end of the run.""")),

    (("--summary",),
     dict(action="store_true", dest="summary",
          help="""Display the summary at the end of the run.""")),

    (("-o", "--outfile"),
     dict(dest="outfiles", action="append", metavar="FILENAME",
          help="Write formatter output to output-file (default: stdout).")),

    ((),  # -- CONFIGFILE only
     dict(dest="paths", action="append",
          help="Specify default feature paths, used when none are provided.")),
    ((),  # -- CONFIGFILE only
     dict(dest="tag_expression_protocol", type=TagExpressionProtocol.from_name,
          choices=TagExpressionProtocol.choices(),
          default=TagExpressionProtocol.DEFAULT.name.lower(),
          help="""\
Specify the tag-expression protocol to use (default: %(default)s).
With "v1", only tag-expressions v1 are supported.
With "v2", only tag-expressions v2 are supported.
With "auto_detect", tag-expressions v1 and v2 are auto-detected.
""")),

    (("-q", "--quiet"),
     dict(action="store_true",
          help="Alias for --no-snippets --no-source.")),

    (("-r", "--runner"),
     dict(dest="runner", action="store", metavar="RUNNER_CLASS",
          default=DEFAULT_RUNNER_CLASS_NAME,
          help='Use own runner class, like: "behave.runner:Runner"')),

    (("--no-source",),
     dict( dest="show_source", action="store_false",
          help="""Don't print the file and line of the step definition with the
                  steps.""")),

    (("--show-source",),
     dict(dest="show_source", action="store_true",
          help="""Print the file and line of the step
                  definition with the steps. This is the default
                  behaviour. This switch is used to override a
                  configuration file setting.""")),

    (("--stage",),
     dict(help="""Defines the current test stage.
                  The test stage name is used as name prefix for the environment
                  file and the steps directory (instead of default path names).
                  """)),

    (("--stop",),
     dict(action="store_true",
          help="Stop running tests at the first failure.")),

    # -- DISABLE-UNUSED-OPTION: Not used anywhere.
    # (("-S", "--strict"),
    # dict(action="store_true",
    #    help="Fail if there are any undefined or pending steps.")),

    ((),  # -- CONFIGFILE only
     dict(dest="default_tags", metavar="TAG_EXPRESSION", action="append",
          help="""Define default tags when non are provided.
                  See :option:`--tags` for more information.""")),

    (("-t", "--tags"),
     dict(action="append", metavar="TAG_EXPRESSION",
          help="""Only execute features or scenarios with tags
                  matching TAG_EXPRESSION.
                  Use :option:`--tags-help` option for more information.""",
          config_help="""Only execute certain features or scenarios based
                         on the tag expression given. See below for how to code
                         tag expressions in configuration files.""")),

    (("-T", "--no-timings"),
     dict( dest="show_timings", action="store_false",
          help="""Don't print the time taken for each step.""")),

    (("--show-timings",),
     dict(dest="show_timings", action="store_true",
          help="""Print the time taken, in seconds, of each step after the
                  step has completed. This is the default behaviour. This
                  switch is used to override a configuration file
                  setting.""")),

    (("-v", "--verbose"),
     dict(action="store_true",
          help="Show the files and features loaded.")),

    (("-w", "--wip"),
     dict(action="store_true",
          help="""Only run scenarios tagged with "wip". Additionally: use the
                  "plain" formatter, do not capture stdout or logging output
                  and stop at the first failure.""")),

    (("--lang",),
     dict(metavar="LANG",
          help="Use keywords for a language other than English.")),

    (("--lang-list",),
     dict(action="store_true",
          help="List the languages available for --lang.")),

    (("--lang-help",),
     dict(metavar="LANG",
          help="List the translations accepted for one language.")),

    (("--tags-help",),
     dict(action="store_true",
          help="Show help for tag expressions.")),

    (("--version",),
     dict(action="store_true", help="Show version.")),
]


# -- CONFIG-FILE SKIPS:
# * Skip SOME_HELP options, like: --tags-help, --lang-list, ...
# * Skip --no-<name> options (action: "store_false", "store_const")
CONFIGFILE_EXCLUDED_OPTIONS = set([
    "tags_help", "lang_list", "lang_help",
    "version",
    "userdata_defines",
])
CONFIGFILE_EXCLUDED_ACTIONS = set(["store_false", "store_const"])

# -- OPTIONS: With raw value access semantics in configuration file.
RAW_VALUE_OPTIONS = frozenset([
    "logging_format",
    "logging_datefmt",
    # -- MAYBE: "scenario_outline_annotation_schema",
])

# -- SPECIAL CONFIGURATION SECTIONS
# Maps config sections to their data names in the final config
SPECIAL_CONFIG_SECTIONS = {
    "behave.formatters": "more_formatters",
    "behave.runners":    "more_runners",
    "behave.userdata":   "userdata",
}


def _values_to_str(data):
    return json.loads(json.dumps(data),
        parse_float=str,
        parse_int=str,
        parse_constant=str
    )


def has_negated_option(option_words):
    return any(word.startswith("--no-") for word in option_words)


def derive_dest_from_long_option(fixed_options):
    for option_name in fixed_options:
        if option_name.startswith("--"):
            return option_name[2:].replace("-", "_")
    return None


ConfigFileOption = namedtuple("ConfigFileOption", ("dest", "action", "type"))


def configfile_options_iter(config):
    skip_missing = bool(config)
    def config_has_param(config, param_name):
        try:
            return param_name in config["behave"]
        except AttributeError:  # pragma: no cover
            # H-- INT: PY27: SafeConfigParser instance has no attribute "__getitem__"
            return config.has_option("behave", param_name)
        except KeyError:
            return False

    for fixed, keywords in OPTIONS:
        action = keywords.get("action", "store")
        if has_negated_option(fixed) or action == "store_false":
            # -- SKIP NEGATED OPTIONS, like: --no-color
            continue
        if "dest" in keywords:
            dest = keywords["dest"]
        else:
            # -- CASE: dest=... keyword is missing
            # DERIVE IT FROM: fixed-option words.
            dest = derive_dest_from_long_option(fixed)
        if not dest or (dest in CONFIGFILE_EXCLUDED_OPTIONS):
            continue
        if skip_missing and not config_has_param(config, dest):
            continue

        # -- FINALLY:
        action = keywords.get("action", "store")
        value_type = keywords.get("type", None)
        yield ConfigFileOption(dest, action, value_type)


def format_outfiles_coupling(config_data, config_dir):
    # -- STEP: format/outfiles coupling
    if "format" in config_data:
        # -- OPTIONS: format/outfiles are coupled in configuration file.
        formatters = config_data["format"]
        formatter_size = len(formatters)
        outfiles = config_data.get("outfiles", [])
        outfiles_size = len(outfiles)
        if outfiles_size < formatter_size:
            for formatter_name in formatters[outfiles_size:]:
                outfile = "%s.output" % formatter_name
                outfiles.append(outfile)
            config_data["outfiles"] = outfiles
        elif len(outfiles) > formatter_size:
            print("CONFIG-ERROR: Too many outfiles (%d) provided." %
                  outfiles_size)
            config_data["outfiles"] = outfiles[:formatter_size]

    for paths_name in ("paths", "outfiles"):
        if paths_name in config_data:
            # -- Evaluate relative paths relative to location.
            # NOTE: Absolute paths are preserved by os.path.join().
            paths = config_data[paths_name]
            config_data[paths_name] = [
                os.path.normpath(os.path.join(config_dir, p))
                for p in paths
            ]


def read_configparser(path):
    # pylint: disable=too-many-locals, too-many-branches
    config = ConfigParser()
    config.optionxform = str    # -- SUPPORT: case-sensitive keys
    config.read(path)
    this_config = {}

    for dest, action, value_type in configfile_options_iter(config):
        param_name = dest
        if dest == "tags":
            # -- SPECIAL CASE: Distinguish config-file tags from command-line.
            param_name = "config_tags"

        if action == "store":
            raw_mode = dest in RAW_VALUE_OPTIONS
            value = config.get("behave", dest, raw=raw_mode)
            if value_type:
                value = value_type(value)  # May raise ParseError/ValueError, etc.
            this_config[param_name] = value
        elif action == "store_true":
            # -- HINT: Only non-negative options are used in config-file.
            # SKIPS: --no-color, --no-snippets, ...
            this_config[param_name] = config.getboolean("behave", dest)
        elif action == "append":
            value_parts = config.get("behave", dest).splitlines()
            value_type = value_type or six.text_type
            this_config[param_name] = [value_type(part.strip()) for part in value_parts]
        elif action not in CONFIGFILE_EXCLUDED_ACTIONS:  # pragma: no cover
            raise ValueError('action "%s" not implemented' % action)

    config_dir = os.path.dirname(path)
    format_outfiles_coupling(this_config, config_dir)

    # -- STEP: Special additional configuration sections.
    # SCHEMA: config_section: data_name
    for section_name, data_name in SPECIAL_CONFIG_SECTIONS.items():
        this_config[data_name] = {}
        if config.has_section(section_name):
            this_config[data_name].update(config.items(section_name))

    return this_config


def read_toml_config(path):
    """
    Read configuration from "pyproject.toml" file.
    The "behave" configuration should be stored in TOML table(s):

    * "tool.behave"
    * "tool.behave.*"

    SEE: https://www.python.org/dev/peps/pep-0518/#tool-table
    """
    # pylint: disable=too-many-locals, too-many-branches
    with open(path, "rb") as toml_file:
        # -- HINT: Use simple dictionary for "config".
        config = json.loads(json.dumps(tomllib.load(toml_file)))

    this_config = {}
    try:
        config_tool = config["tool"]
    except KeyError:
        # -- SPECIAL CASE: A pyproject.toml may not contain a tool section.
        return this_config

    for dest, action, value_type in configfile_options_iter(config_tool):
        param_name = dest
        if dest == "tags":
            # -- SPECIAL CASE: Distinguish config-file tags from command-line.
            param_name = "config_tags"

        raw_value = config_tool["behave"][dest]
        if action == "store":
            this_config[param_name] = str(raw_value)
        elif action in ("store_true", "store_false"):
            this_config[param_name] = bool(raw_value)
        elif action == "append":
            # -- TOML SPECIFIC:
            #  TOML has native arrays and quoted strings.
            #  There is no need to split by newlines or strip values.
            value_type = value_type or six.text_type
            if not isinstance(raw_value, list):
                message = "%s = %r (expected: list<%s>, was: %s)" % \
                          (param_name, raw_value, value_type.__name__,
                           type(raw_value).__name__)
                raise ConfigParamTypeError(message)
            this_config[param_name] = raw_value
        elif action not in CONFIGFILE_EXCLUDED_ACTIONS:
            raise ValueError('action "%s" not implemented' % action)

    config_dir = os.path.dirname(path)
    format_outfiles_coupling(this_config, config_dir)

    # -- STEP: Special additional configuration sections.
    # SCHEMA: config_section: data_name
    for section_name, data_name in SPECIAL_CONFIG_SECTIONS.items():
        this_section_name = section_name.replace("behave.", "", 1)
        this_config[data_name] = {}
        try:
            section_data = config_tool["behave"][this_section_name]
            this_config[data_name] = _values_to_str(section_data)
        except KeyError:
            this_config[data_name] = {}

    return this_config


CONFIG_FILE_PARSERS = {
    "ini": read_configparser,
    "cfg": read_configparser,
    "behaverc": read_configparser,
}
if _TOML_AVAILABLE:
    CONFIG_FILE_PARSERS["toml"] = read_toml_config


def read_configuration(path, verbose=False):
    """
    Read the "behave" config from a config-file.

    :param path:    Path to the config-file
    """
    file_extension = path.split(".")[-1]
    parse_func = CONFIG_FILE_PARSERS.get(file_extension, None)
    if not parse_func:
        if verbose:
            print("MISSING CONFIG-FILE PARSER FOR: %s" % path)
        return {}

    # -- NORMAL CASE:
    parsed = parse_func(path)
    return parsed


def config_filenames():
    paths = ["./", os.path.expanduser("~")]
    if sys.platform in ("cygwin", "win32") and "APPDATA" in os.environ:
        paths.append(os.path.join(os.environ["APPDATA"]))

    for path in reversed(paths):
        for filename in reversed((
            "behave.ini", ".behaverc", "setup.cfg", "tox.ini", "pyproject.toml"
        )):
            filename = os.path.join(path, filename)
            if os.path.isfile(filename):
                yield filename


def load_configuration(defaults, verbose=False):
    for filename in config_filenames():
        if verbose:
            print('Loading config defaults from "%s"' % filename)
        defaults.update(read_configuration(filename, verbose))

    if verbose:
        print("Using CONFIGURATION DEFAULTS:")
        for k, v in sorted(six.iteritems(defaults)):
            print("%18s: %s" % (k, v))


def setup_parser():
    # construct the parser
    # usage = "%(prog)s [options] [FILE|DIR|FILE:LINE|AT_FILE]+"
    usage = "%(prog)s [options] [DIRECTORY|FILE|FILE:LINE|AT_FILE]*"
    description = """Run a number of feature tests with behave.

EXAMPLES:
  behave features/
  behave features/one.feature features/two.feature
  behave features/one.feature:10
  behave @features.txt
"""
    formatter_class = argparse.RawDescriptionHelpFormatter
    parser = argparse.ArgumentParser(usage=usage,
                                     description=description,
                                     formatter_class=formatter_class)
    for fixed, keywords in OPTIONS:
        if not fixed:
            # -- SKIP: CONFIG-FILE ONLY OPTION.
            continue

        if "config_help" in keywords:
            keywords = dict(keywords)
            del keywords["config_help"]
        parser.add_argument(*fixed, **keywords)
    parser.add_argument("paths", nargs="*",
                        help="Feature directory, file or file-location (FILE:LINE).")
    return parser


def setup_config_file_parser():
    # -- TEST-BALLOON: Auto-documentation of config-file schema.
    # COVERS: config-file.section="behave"
    description = "config-file schema"
    formatter_class = argparse.RawDescriptionHelpFormatter
    parser = argparse.ArgumentParser(description=description,
                                     formatter_class=formatter_class)
    for fixed, keywords in configfile_options_iter(None):
        if "config_help" in keywords:
            keywords = dict(keywords)
            config_help = keywords["config_help"]
            keywords["help"] = config_help
            del keywords["config_help"]
        parser.add_argument(*fixed, **keywords)
    return parser

class Configuration(object):
    """
    Configuration object for behave and behave runners.

    .. attribute:: tag_expression
        :type: behave.tag_expression.v2.TagExpression | behave.tag_expression.v1.TagExpression

        Provides the Tag-Expression object based on the :option:`--tags` option(s)
        on command-line and `:confval:`default_tags` parameter in the config-file.
    """
    # pylint: disable=too-many-instance-attributes
    defaults = dict(
        color=os.getenv("BEHAVE_COLOR", COLOR_DEFAULT),
        jobs=1,
        show_snippets=True,
        show_skipped=True,
        dry_run=False,
        show_source=True,
        show_timings=True,
        capture=None,
        capture_stdout=True,
        capture_stderr=True,
        capture_log=True,
        capture_hooks=True,
        logging_format="LOG_%(levelname)s:%(name)s: %(message)s",
        logging_level=logging.INFO,
        runner=DEFAULT_RUNNER_CLASS_NAME,
        steps_catalog=False,
        summary=True,
        tag_expression_protocol=TagExpressionProtocol.DEFAULT,
        junit=False,
        stage=None,
        userdata={},
        # -- SPECIAL:
        default_format="pretty",    # -- Used when no formatters are configured.
        default_tags="",            # -- Used when no tags are defined.
        config_tags=None,
        scenario_outline_annotation_schema=u"{name} -- @{row.id} {examples.name}",
        use_nested_step_modules=False,
    )

    def __init__(self, command_args=None, load_config=True, verbose=None,
                 **kwargs):
        """
        Constructs a behave configuration object.
          * loads the configuration defaults (if needed).
          * process the command-line args
          * store the configuration results

        :param command_args: Provide command args (as sys.argv).
            If command_args is None, sys.argv[1:] is used.
        :type command_args: list<str>, str
        :param load_config: Indicate if configfile should be loaded (=true)
        :param verbose: Indicate if diagnostic output is enabled
        :param kwargs:  Used to hand-over/overwrite default values.
        """
        self.init(verbose=verbose, **kwargs)

        # -- STEP: Load config-file(s) and parse command-line
        command_args = self.make_command_args(command_args, verbose=verbose)
        if load_config:
            load_configuration(self.defaults, verbose=self.verbose)
        parser = setup_parser()
        parser.set_defaults(**self.defaults)
        args = parser.parse_args(command_args)
        for key, value in six.iteritems(args.__dict__):
            if key.startswith("_"):
                continue
            setattr(self, key, value)

        self.paths = [os.path.normpath(path) for path in self.paths]
        self.setup_outputs(args.outfiles)

        if self.steps_catalog:
            self.setup_steps_catalog_mode()
        if self.wip:
            self.setup_wip_mode()
        if self.quiet:
            self.show_source = False
            self.show_snippets = False

        self.setup_capture()
        self.setup_tag_expression()
        self.setup_select_by_filters()
        self.setup_stage(self.stage)
        self.setup_model()
        self.setup_userdata()
        self.setup_runner_aliases()

        # -- FINALLY: Setup Reporters and Formatters
        # NOTE: Reporters and Formatters can now use userdata information.
        self.setup_reporters()
        self.setup_formats()
        self.show_bad_formats_and_fail(parser)

    def init(self, verbose=None, **kwargs):
        """
        (Re-)Init this configuration object.
        """
        self.defaults = self.make_defaults(**kwargs)
        self.version = None
        self.capture = None
        self.capture_stdout = None
        self.capture_stderr = None
        self.capture_log = None
        self.capture_hooks = None
        self.tags_help = None
        self.lang_list = None
        self.lang_help = None
        self.default_tags = None
        self.junit = None
        self.logging_format = None
        self.logging_datefmt = None
        self.logging_level = None
        self.name = None
        self.stage = None
        self.steps_catalog = None
        self.tag_expression_protocol = None
        self.tag_expression = None
        self.tags = None
        self.config_tags = None
        self.default_tags = None
        self.userdata = None
        self.wip = None
        self.verbose = verbose or False
        self.formatters = []
        self.reporters = []
        self.name_re = None
        self.outputs = []
        self.include_re = None
        self.exclude_re = None
        self.scenario_outline_annotation_schema = None  # pylint: disable=invalid-name
        self.use_nested_step_modules = False
        self.steps_dir = "steps"
        self.environment_file = "environment.py"
        self.userdata_defines = None
        self.more_formatters = None
        self.more_runners = None
        self.runner_aliases = {
            "default": DEFAULT_RUNNER_CLASS_NAME
        }

    @classmethod
    def make_defaults(cls, **kwargs):
        data = cls.defaults.copy()
        for name, value in six.iteritems(kwargs):
            data[name] = value
        return data

    def has_colored_mode(self, file=None):
        if self.color in COLOR_ON_VALUES:
            return True
        if self.color in COLOR_OFF_VALUES:
            return False

        # -- OTHERWISE in AUTO-DETECT mode: color="auto"
        output_file = file or sys.stdout
        isatty = getattr(output_file, "isatty", lambda: True)
        colored = isatty()
        return colored

    def make_command_args(self, command_args=None, verbose=None):
        # pylint: disable=too-many-branches, too-many-statements
        if command_args is None:
            command_args = []
            command_name = os.path.basename(sys.argv[0])
            command_name2 = sys.argv[0].replace("\\", "/")
            if ("behave" in command_name or
                "behave" in sys.argv or
                "behave/__main__" in command_name2):
                # -- ONLY USED IF: Using "behave" or "python -mbehave ..."
                command_args = sys.argv[1:]
        elif isinstance(command_args, six.string_types):
            encoding = select_best_encoding() or "utf-8"
            if six.PY2 and isinstance(command_args, six.text_type):
                command_args = command_args.encode(encoding)
            elif six.PY3 and isinstance(command_args, six.binary_type):
                command_args = command_args.decode(encoding)
            command_args = shlex.split(command_args)
        elif isinstance(command_args, (list, tuple)):
            command_args = to_texts(command_args)

        # -- SUPPORT OPTION: --color=VALUE and --color (without VALUE)
        # HACK: Should be handled in command-line parser specification.
        # OPTION: --color=value, --color   (hint: with optional value)
        # SUPPORTS:
        #   behave --color features/some.feature        # PROBLEM-POINT
        #   behave --color=auto features/some.feature   # NO_PROBLEM
        #   behave --color auto features/some.feature   # NO_PROBLEM
        if "--color" in command_args:
            color_arg_pos = command_args.index("--color")
            next_arg = command_args[color_arg_pos + 1]
            if os.path.exists(next_arg):
                command_args.insert(color_arg_pos + 1, "--")

        if verbose is None:
            # -- AUTO-DISCOVER: Verbose mode from command-line args.
            verbose = ("-v" in command_args) or ("--verbose" in command_args)
            self.verbose = verbose
        return command_args

    def setup_wip_mode(self):
        # Only run scenarios tagged with "wip".
        # Additionally:
        #  * use the "plain" formatter (per default)
        #  * do not capture stdout/stderr/logging output and
        #  * stop at the first failure.
        self.default_format = "plain"
        self.color = "off"
        self.stop = True
        self.capture = False
        self.capture_stdout = False
        self.capture_stderr = False
        self.capture_log = False
        self.capture_hooks = False

        # -- EXTEND TAG-EXPRESSION: Add @wip tag
        self.tags = self.tags or []
        if self.tags and isinstance(self.tags, six.string_types):
            self.tags = [self.tags]
        self.tags.append("@wip")

    def setup_steps_catalog_mode(self):
        # -- SHOW STEP-CATALOG: As step summary.
        self.default_format = "steps.catalog"
        self.format = self.format or []
        if self.format:
            self.format.append("steps.catalog")
        else:
            self.format = ["steps.catalog"]
        self.dry_run = True
        self.summary = False
        self.show_skipped = False
        self.quiet = True

    def setup_select_by_filters(self):
        if self.exclude_re:
            self.exclude_re = re.compile(self.exclude_re)
        if self.include_re:
            self.include_re = re.compile(self.include_re)
        if self.name:
            # -- SELECT: Scenario-by-name, build regular expression.
            self.name_re = self.build_name_re(self.name)

    def setup_reporters(self):
        if self.junit:
            # -- APPLY-CONFIG:
            # Buffer the output (it will be put into Junit report)
            from .reporter.junit import JUnitReporter
            self.capture_stdout = True
            self.capture_stderr = True
            self.capture_log = True
            self.reporters.append(JUnitReporter(self))
        if self.summary:
            # -- APPLY-CONFIG:
            from .reporter.summary import SummaryReporter
            self.reporters.append(SummaryReporter(self))

    def show_bad_formats_and_fail(self, parser):
        """
        Show any BAD-FORMATTER(s) and fail with :class:`~behave.parser.ParseError` if any exists.
        """
        # -- SANITY-CHECK FIRST: Is correct type used for "config.format"
        if self.format is not None and not isinstance(self.format, list):
            parser.error("CONFIG-PARAM-TYPE-ERROR: format = %r (expected: list<%s>, was: %s)" %
                         (self.format, six.text_type, type(self.format).__name__))

        bad_formats_and_errors = self.select_bad_formats_with_errors()
        if bad_formats_and_errors:
            bad_format_parts = []
            for name, error in bad_formats_and_errors:
                message = "%s (problem: %s)" % (name, error)
                bad_format_parts.append(message)
            parser.error("BAD_FORMAT=%s" % ", ".join(bad_format_parts))

    def setup_tag_expression(self, tags=None):
        """
        Build the tag_expression object from:

        * command-line tags (as tag-expression text)
        * config-file tags (as tag-expression text)
        """
        # -- APPLY-CONFIG:
        from .tag_expression import make_tag_expression
        config_tags = self.config_tags or self.default_tags or ""
        tags = tags or self.tags or config_tags
        # DISABLED: tags = self._normalize_tags(tags)

        # -- STEP: Support that tags on command-line can use config-file.tags
        TagExpressionProtocol.use(self.tag_expression_protocol)
        config_tag_expression = make_tag_expression(config_tags)
        placeholder = "{config.tags}"
        placeholder_value = "{0}".format(config_tag_expression)
        if isinstance(tags, six.string_types) and placeholder in tags:
            tags = tags.replace(placeholder, placeholder_value)
        elif isinstance(tags, (list, tuple)):
            for index, item in enumerate(tags):
                if placeholder in item:
                    new_item = item.replace(placeholder, placeholder_value)
                    tags[index] = new_item

        # -- STEP: Make tag-expression
        self.tag_expression = make_tag_expression(tags)
        self.tags = tags

    # def _normalize_tags(self, tags):
    #     if isinstance(tags, six.string_types):
    #         if tags.startswith('"') and tags.endswith('"'):
    #             return tags[1:-1]
    #         elif tags.startswith("'") and tags.endswith("'"):
    #             return tags[1:-1]
    #         return tags
    #     elif not isinstance(tags, (list, tuple)):
    #         raise TypeError("EXPECTED: string, sequence<string>", tags)
    #
    #     # -- CASE: sequence<string>
    #     unquote_needed = (any('"' in part for part in tags) or
    #                       any("'" in part for part in tags))
    #     if unquote_needed:
    #         parts = []
    #         for part in tags:
    #             parts.append(self._normalize_tags(part))
    #         tags = parts
    #     return tags

    def setup_outputs(self, args_outfiles=None):
        if self.outputs:
            if args_outfiles:
                raise RuntimeError("ONLY-ONCE with param: args_outfiles")
            return

        # -- NORMAL CASE: Setup only initially (once).
        if not args_outfiles:
            self.outputs.append(StreamOpener(stream=sys.stdout))
        else:
            for outfile in args_outfiles:
                if outfile and outfile != "-":
                    self.outputs.append(StreamOpener(outfile))
                else:
                    self.outputs.append(StreamOpener(stream=sys.stdout))

    def setup_formats(self):
        """Register more, user-defined formatters by name."""
        if self.more_formatters:
            # -- APPLY-CONFIG:
            from .formatter import _registry as _format_registry
            for name, scoped_class_name in self.more_formatters.items():
                _format_registry.register_as(name, scoped_class_name)

    def setup_runner_aliases(self):
        if self.more_runners:
            for name, scoped_class_name in self.more_runners.items():
                self.runner_aliases[name] = scoped_class_name

    def select_bad_formats_with_errors(self):
        bad_formats = []
        if self.format:
            # -- USE-APPLY-CONFIG:
            from .formatter import _registry as _format_registry
            for format_name in self.format:
                formatter_valid = _format_registry.is_formatter_valid(format_name)
                if format_name == "help" or formatter_valid:
                    continue

                try:
                    _ = _format_registry.select_formatter_class(format_name)
                    bad_formats.append((format_name, "InvalidClassError"))
                except Exception as e:  # pylint: disable=broad-exception-caught
                    formatter_error = e.__class__.__name__
                    if formatter_error == "KeyError":
                        formatter_error = "LookupError"
                    if self.verbose:
                        formatter_error += ": %s" % str(e)
                    bad_formats.append((format_name, formatter_error))
        return bad_formats

    @staticmethod
    def build_name_re(names):
        """
        Build regular expression for scenario selection by name
        by using a list of name parts or name regular expressions.

        :param names: List of name parts or regular expressions (as text).
        :return: Compiled regular expression to use.
        """
        # -- NOTE: re.LOCALE is removed in Python 3.6 (deprecated in Python 3.5)
        # flags = (re.UNICODE | re.LOCALE)
        # -- ENSURE: Names are all unicode/text values (for issue #606).
        names = to_texts(names)
        pattern = u"|".join(names)
        return re.compile(pattern, flags=re.UNICODE)

    def exclude(self, filename):
        if isinstance(filename, FileLocation):
            filename = six.text_type(filename)

        if self.include_re and self.include_re.search(filename) is None:
            return True
        if self.exclude_re and self.exclude_re.search(filename) is not None:
            return True
        return False

    def setup_logging(self, level=None, filename=None, configfile=None, **kwargs):
        """
        Support simple setup of logging subsystem.
        Ensures that the logging level is set.

        .. note:: Logging setup should occur only once.

        SETUP MODES:
          * :func:`logging.config.fileConfig()`, if ``configfile`` is provided.
          * :func:`logging.basicConfig()`, otherwise.

        .. code-block: python
            # -- FILE: features/environment.py
            def before_all(context):
                context.config.setup_logging()

        :param level:       Logging level of root logger.
                            If None, use :attr:`logging_level` value.
        :param filename:    Log to file with this filename (optional).
        :param configfile:  Configuration filename for fileConfig() setup.
        :param kwargs:      Passed to :func:`logging.basicConfig()` or
                                    :func:`logging.config.fileConfig()`

        .. versionchanged:: 1.2.7

            * Parameter "filename" was added to simplify logging to a file.
        """
        # -- APPLY-CONFIG:
        from .log_config import LoggingConfigurator
        configurator = LoggingConfigurator(self)
        if configfile:
            # -- BASED ON: logging.config.fileConfig()
            configurator.configure_by_file(configfile, level=level, **kwargs)
        elif filename:
            # -- BASED ON: logging.basicConfig(filename, ...)
            configurator.configure_file_sink(filename, level=level, **kwargs)
        else:
            # -- BASED ON: logging.basicConfig() without filename
            configurator.configure_console_sink(level=level, **kwargs)

    def setup_model(self):
        if self.scenario_outline_annotation_schema:
            # -- APPLY-CONFIG:
            from .model import ScenarioOutline
            name_schema = six.text_type(self.scenario_outline_annotation_schema)
            ScenarioOutline.annotation_schema = name_schema.strip()

    def setup_stage(self, stage=None):
        """
        Set up the test stage that selects a different set of
        steps and environment implementations.

        :param stage:   Name of current test stage (as string or None).

        EXAMPLE::

            # -- SETUP DEFAULT TEST STAGE (unnamed):
            config = Configuration()
            config.setup_stage()
            assert config.steps_dir == "steps"
            assert config.environment_file == "environment.py"

            # -- SETUP PRODUCT TEST STAGE:
            config.setup_stage("product")
            assert config.steps_dir == "product_steps"
            assert config.environment_file == "product_environment.py"
        """
        if stage is None:
            # -- USE ENVIRONMENT-VARIABLE, if stage is undefined.
            stage = os.environ.get("BEHAVE_STAGE", None)

        steps_dir = "steps"
        environment_file = "environment.py"
        if stage:
            # -- USE A TEST STAGE: Select different set of implementations.
            prefix = stage + "_"
            steps_dir = prefix + steps_dir
            environment_file = prefix + environment_file

        # -- STORE STAGE-CONFIGURATION:
        self.stage = stage
        self.steps_dir = steps_dir
        self.environment_file = environment_file

    def setup_userdata(self):
        if not isinstance(self.userdata, UserData):
            self.userdata = UserData(self.userdata)
        if self.userdata_defines:
            # -- ENSURE: Cmd-line overrides configuration file parameters.
            self.userdata.update(self.userdata_defines)

    def update_userdata(self, data):
        """Update userdata with data and reapply userdata defines (cmdline).
        :param data:  Provides (partial) userdata (as dict)
        """
        self.userdata.update(data)
        if self.userdata_defines:
            # -- REAPPLY: Cmd-line defines (override configuration file data).
            self.userdata.update(self.userdata_defines)

    # -- SINCE: behave v1.2.7
    def should_capture(self):
        return self.capture_stdout or self.capture_stderr or self.capture_log

    def should_capture_hooks(self):
        return self.capture_hooks and self.should_capture()

    def setup_capture(self):
        if isinstance(self.capture, bool):
            # -- IF SPECIFIED: Apply capture mode to stdout/stderr/log.
            self.capture_stdout = self.capture
            self.capture_stderr = self.capture
            self.capture_log = self.capture

    # -- DEPRECATED CONFIG PARAMETER NAMES:
    # DEPRECATED SINCE: behave v1.2.7
    # REMOVED IN: behave v1.4.0
    @property
    def stdout_capture(self):
        warnings.warn("Use 'capture_stdout' instead", DeprecationWarning)
        return self.capture_stdout

    @stdout_capture.setter
    def stdout_capture(self, value):
        warnings.warn("Use 'capture_stdout = ...' instead", DeprecationWarning)
        self.capture_stdout = value

    @property
    def stderr_capture(self):
        warnings.warn("Use 'capture_stderr' instead", DeprecationWarning)
        return self.capture_stderr

    @stderr_capture.setter
    def stderr_capture(self, value):
        warnings.warn("Use 'capture_stderr = ...' instead", DeprecationWarning)
        self.capture_stderr = value

    @property
    def log_capture(self):
        warnings.warn("Use 'capture_log' instead", DeprecationWarning)
        return self.capture_log

    @log_capture.setter
    def log_capture(self, value):
        warnings.warn("Use 'capture_log = ...' instead", DeprecationWarning)
        self.capture_log = value
