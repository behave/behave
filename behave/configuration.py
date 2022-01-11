# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function
import argparse
import inspect
import json
import logging
import os
import re
import sys
import shlex
import six
from six.moves import configparser

from behave.model import ScenarioOutline
from behave.model_core import FileLocation
from behave.reporter.junit import JUnitReporter
from behave.reporter.summary import SummaryReporter
from behave.tag_expression import make_tag_expression
from behave.formatter.base import StreamOpener
from behave.formatter import _registry as _format_registry
from behave.userdata import UserData, parse_user_define
from behave._types import Unknown
from behave.textutil import select_best_encoding, to_texts

# -- PYTHON 2/3 COMPATIBILITY:
# SINCE Python 3.2: ConfigParser = SafeConfigParser
ConfigParser = configparser.ConfigParser
if six.PY2:
    ConfigParser = configparser.SafeConfigParser

try:
    if sys.version_info >= (3, 11):
        import tomllib
    elif sys.version_info < (3, 0):
        import toml as tomllib
    else:
        import tomli as tomllib
    _TOML_AVAILABLE = True
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
options = [
    (("-c", "--no-color"),
     dict(action="store_false", dest="color",
          help="Disable the use of ANSI color escapes.")),

    (("--color",),
     dict(dest="color", choices=["never", "always", "auto"],
          default=os.getenv('BEHAVE_COLOR'), const="auto", nargs="?",
          help="""Use ANSI color escapes. Defaults to %(const)r.
                  This switch is used to override a
                  configuration file setting.""")),

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
                  Only supported by test runners that support parallel execution.""")),

    ((),  # -- CONFIGFILE only
     dict(dest="default_format", default="pretty",
          help="Specify default formatter (default: %(default)s).")),


    (("-f", "--format"),
     dict(action="append",
          help="""Specify a formatter. If none is specified the default
                  formatter is used. Pass "--format help" to get a
                  list of available formatters.""")),

    (("--steps-catalog",),
     dict(action="store_true", dest="steps_catalog",
          help="""Show a catalog of all available step definitions.
                  SAME AS: --format=steps.catalog --dry-run --no-summary -q""")),

    ((),  # -- CONFIGFILE only
     dict(dest="scenario_outline_annotation_schema",
          help="""Specify name annotation schema for scenario outline
                  (default="{name} -- @{row.id} {examples.name}").""")),

    (("--no-skipped",),
     dict(action="store_false", dest="show_skipped",
          help="Don't print skipped steps (due to tags).")),

    (("--show-skipped",),
     dict(action="store_true",
          help="""Print skipped steps.
                  This is the default behaviour. This switch is used to
                  override a configuration file setting.""")),

    (("--no-snippets",),
     dict(action="store_false", dest="show_snippets",
          help="Don't print snippets for unimplemented steps.")),
    (("--snippets",),
     dict(action="store_true", dest="show_snippets",
          help="""Print snippets for unimplemented steps.
                  This is the default behaviour. This switch is used to
                  override a configuration file setting.""")),

    (("--no-multiline",),
     dict(action="store_false", dest="show_multiline",
          help="""Don't print multiline strings and tables under steps.""")),

    (("--multiline", ),
     dict(action="store_true", dest="show_multiline",
          help="""Print multiline strings and tables under steps.
                  This is the default behaviour. This switch is used to
                  override a configuration file setting.""")),

    (("-n", "--name"),
     dict(action="append", metavar="NAME_PATTERN",
          help="""Select feature elements (scenarios, ...) to run
                  which match part of the given name (regex pattern).
                  If this option is given more than once,
                  it will match against all the given names.""")),

    (("--no-capture",),
     dict(action="store_false", dest="stdout_capture",
          help="""Don't capture stdout (any stdout output will be
                  printed immediately.)""")),

    (("--capture",),
     dict(action="store_true", dest="stdout_capture",
          help="""Capture stdout (any stdout output will be
                  printed if there is a failure.)
                  This is the default behaviour. This switch is used to
                  override a configuration file setting.""")),

    (("--no-capture-stderr",),
     dict(action="store_false", dest="stderr_capture",
          help="""Don't capture stderr (any stderr output will be
                  printed immediately.)""")),

    (("--capture-stderr",),
     dict(action="store_true", dest="stderr_capture",
          help="""Capture stderr (any stderr output will be
                  printed if there is a failure.)
                  This is the default behaviour. This switch is used to
                  override a configuration file setting.""")),

    (("--no-logcapture",),
     dict(action="store_false", dest="log_capture",
          help="""Don't capture logging. Logging configuration will
                  be left intact.""")),

    (("--logcapture",),
     dict(action="store_true", dest="log_capture",
          help="""Capture logging. All logging during a step will be captured
                  and displayed in the event of a failure.
                  This is the default behaviour. This switch is used to
                  override a configuration file setting.""")),

    (("--logging-level",),
     dict(type=LogLevel.parse_type,
          help="""Specify a level to capture logging at. The default
                  is INFO - capturing everything.""")),

    (("--logging-format",),
     dict(help="""Specify custom format to print statements. Uses the
                  same format as used by standard logging handlers. The
                  default is "%%(levelname)s:%%(name)s:%%(message)s".""")),

    (("--logging-datefmt",),
     dict(help="""Specify custom date/time format to print
                  statements.
                  Uses the same format as used by standard logging
                  handlers.""")),

    (("--logging-filter",),
     dict(help="""Specify which statements to filter in/out. By default,
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
          help="Clear all other logging handlers.")),

    (("--no-summary",),
     dict(action="store_false", dest="summary",
          help="""Don't display the summary at the end of the run.""")),

    (("--summary",),
     dict(action="store_true", dest="summary",
          help="""Display the summary at the end of the run.""")),

    (("-o", "--outfile"),
     dict(action="append", dest="outfiles", metavar="FILE",
          help="Write to specified file instead of stdout.")),

    ((),  # -- CONFIGFILE only
     dict(action="append", dest="paths",
          help="Specify default feature paths, used when none are provided.")),

    (("-q", "--quiet"),
     dict(action="store_true",
          help="Alias for --no-snippets --no-source.")),

    (("-r", "--runner"),
     dict(dest="runner", action="store", metavar="RUNNER_CLASS",
          default=DEFAULT_RUNNER_CLASS_NAME,
          help='Use own runner class, like: "behave.runner:Runner"')),

    (("--no-source",),
     dict(action="store_false", dest="show_source",
          help="""Don't print the file and line of the step definition with the
                  steps.""")),

    (("--show-source",),
     dict(action="store_true", dest="show_source",
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
                  See --tags for more information.""")),

    (("-t", "--tags"),
     dict(action="append", metavar="TAG_EXPRESSION",
          help="""Only execute features or scenarios with tags
                  matching TAG_EXPRESSION. Pass "--tags-help" for
                  more information.""",
          config_help="""Only execute certain features or scenarios based
                         on the tag expression given. See below for how to code
                         tag expressions in configuration files.""")),

    (("-T", "--no-timings"),
     dict(action="store_false", dest="show_timings",
          help="""Don't print the time taken for each step.""")),

    (("--show-timings",),
     dict(action="store_true", dest="show_timings",
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

# -- OPTIONS: With raw value access semantics in configuration file.
raw_value_options = frozenset([
    "logging_format",
    "logging_datefmt",
    # -- MAYBE: "scenario_outline_annotation_schema",
])


def values_to_str(d):
    return json.loads(
        json.dumps(d),
        parse_float=str,
        parse_int=str,
        parse_constant=str
    )


def decode_options(config):
    for fixed, keywords in options:
        if "dest" in keywords:
            dest = keywords["dest"]
        else:
            dest = None
            for opt in fixed:
                if opt.startswith("--"):
                    dest = opt[2:].replace("-", "_")
                else:
                    assert len(opt) == 2
                    dest = opt[1:]
        if (
            not dest
        ) or (
            dest in "tags_help lang_list lang_help version".split()
        ):
            continue
        try:
            if dest not in config["behave"]:
                continue
        except AttributeError as exc:
            # SafeConfigParser instance has no attribute '__getitem__' (py27)
            if "__getitem__" not in str(exc):
                raise
            if not config.has_option("behave", dest):
                continue
        except KeyError:
            continue
        action = keywords.get("action", "store")
        yield dest, action


def format_outfiles_coupling(result, config_dir):
    # -- STEP: format/outfiles coupling
    if "format" in result:
        # -- OPTIONS: format/outfiles are coupled in configuration file.
        formatters = result["format"]
        formatter_size = len(formatters)
        outfiles = result.get("outfiles", [])
        outfiles_size = len(outfiles)
        if outfiles_size < formatter_size:
            for formatter_name in formatters[outfiles_size:]:
                outfile = "%s.output" % formatter_name
                outfiles.append(outfile)
            result["outfiles"] = outfiles
        elif len(outfiles) > formatter_size:
            print("CONFIG-ERROR: Too many outfiles (%d) provided." %
                  outfiles_size)
            result["outfiles"] = outfiles[:formatter_size]

    for paths_name in ("paths", "outfiles"):
        if paths_name in result:
            # -- Evaluate relative paths relative to location.
            # NOTE: Absolute paths are preserved by os.path.join().
            paths = result[paths_name]
            result[paths_name] = \
                [os.path.normpath(os.path.join(config_dir, p)) for p in paths]


def read_configparser(path):
    # pylint: disable=too-many-locals, too-many-branches
    config = ConfigParser()
    config.optionxform = str    # -- SUPPORT: case-sensitive keys
    config.read(path)
    config_dir = os.path.dirname(path)
    result = {}

    for dest, action in decode_options(config):
        if action == "store":
            result[dest] = config.get(
                "behave", dest, raw=dest in raw_value_options
            )
        elif action in ("store_true", "store_false"):
            result[dest] = config.getboolean("behave", dest)
        elif action == "append":
            if dest == "userdata_defines":
                continue    # -- SKIP-CONFIGFILE: Command-line only option.
            result[dest] = \
                [s.strip() for s in config.get("behave", dest).splitlines()]
        else:
            raise ValueError('action "%s" not implemented' % action)

    format_outfiles_coupling(result, config_dir)

    # -- STEP: Special additional configuration sections.
    # SCHEMA: config_section: data_name
    special_config_section_map = {
        "behave.formatters": "more_formatters",
        "behave.runners":    "more_runners",
        "behave.userdata":   "userdata",
    }
    for section_name, data_name in special_config_section_map.items():
        result[data_name] = {}
        if config.has_section(section_name):
            result[data_name].update(config.items(section_name))

    return result


def read_toml(path):
    """Read configuration from pyproject.toml file.

    Configuration should be stored inside the 'tool.behave' table.

    See https://www.python.org/dev/peps/pep-0518/#tool-table
    """
    # pylint: disable=too-many-locals, too-many-branches
    with open(path, "rb") as tomlfile:
        config = json.loads(json.dumps(tomllib.load(tomlfile)))  # simple dict

    config = config['tool']
    config_dir = os.path.dirname(path)
    result = {}

    for dest, action in decode_options(config):
        raw = config["behave"][dest]
        if action == "store":
            result[dest] = str(raw)
        elif action in ("store_true", "store_false"):
            result[dest] = bool(raw)
        elif action == "append":
            if dest == "userdata_defines":
                continue    # -- SKIP-CONFIGFILE: Command-line only option.
            # toml has native arrays and quoted strings, so there's no
            # need to split by newlines or strip values
            result[dest] = raw
        else:
            raise ValueError('action "%s" not implemented' % action)
    format_outfiles_coupling(result, config_dir)

    # -- STEP: Special additional configuration sections.
    # SCHEMA: config_section: data_name
    special_config_section_map = {
        "formatters": "more_formatters",
        "userdata":   "userdata",
    }
    for section_name, data_name in special_config_section_map.items():
        result[data_name] = {}
        try:
            result[data_name] = values_to_str(config["behave"][section_name])
        except KeyError:
            result[data_name] = {}

    return result


def read_configuration(path, verbose=False):
    ext = path.split(".")[-1]
    parsers = {
        "ini": read_configparser,
        "cfg": read_configparser,
        "behaverc": read_configparser,
    }

    if _TOML_AVAILABLE:
        parsers["toml"] = read_toml
    parse_func = parsers.get(ext, None)
    if not parse_func:
        if verbose:
            print('Unable to find a parser for "%s"' % path)
        return {}
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
    # usage = "%(prog)s [options] [ [FILE|DIR|URL][:LINE[:LINE]*] ]+"
    usage = "%(prog)s [options] [ [DIR|FILE|FILE:LINE] ]+"
    description = """\
    Run a number of feature tests with behave."""
    more = """
    EXAMPLES:
    behave features/
    behave features/one.feature features/two.feature
    behave features/one.feature:10
    behave @features.txt
    """
    parser = argparse.ArgumentParser(usage=usage, description=description)
    for fixed, keywords in options:
        if not fixed:
            continue    # -- CONFIGFILE only.
        if "config_help" in keywords:
            keywords = dict(keywords)
            del keywords["config_help"]
        parser.add_argument(*fixed, **keywords)
    parser.add_argument("paths", nargs="*",
                        help="Feature directory, file or file location (FILE:LINE).")
    return parser


class Configuration(object):
    """Configuration object for behave and behave runners."""
    # pylint: disable=too-many-instance-attributes
    defaults = dict(
        color='never' if sys.platform == "win32" else os.getenv('BEHAVE_COLOR', 'auto'),
        jobs=1,
        show_snippets=True,
        show_skipped=True,
        dry_run=False,
        show_source=True,
        show_timings=True,
        stdout_capture=True,
        stderr_capture=True,
        log_capture=True,
        logging_format="%(levelname)s:%(name)s:%(message)s",
        logging_level=logging.INFO,
        runner=DEFAULT_RUNNER_CLASS_NAME,
        steps_catalog=False,
        summary=True,
        junit=False,
        stage=None,
        userdata={},
        # -- SPECIAL:
        default_format="pretty",    # -- Used when no formatters are configured.
        default_tags="",            # -- Used when no tags are defined.
        scenario_outline_annotation_schema=u"{name} -- @{row.id} {examples.name}"
    )
    cmdline_only_options = set("userdata_defines")

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
        # pylint: disable=too-many-branches, too-many-statements
        if command_args is None:
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

        if verbose is None:
            # -- AUTO-DISCOVER: Verbose mode from command-line args.
            verbose = ("-v" in command_args) or ("--verbose" in command_args)

        # Allow commands like `--color features/whizbang.feature` to work
        # Without this, argparse will treat the positional arg as the value to
        # --color and we'd get:
        #   argument --color: invalid choice: 'features/whizbang.feature'
        #   (choose from 'never', 'always', 'auto')
        if '--color' in command_args:
            color_arg_pos = command_args.index('--color')
            if os.path.exists(command_args[color_arg_pos + 1]):
                command_args.insert(color_arg_pos + 1, '--')

        self.version = None
        self.tags_help = None
        self.lang_list = None
        self.lang_help = None
        self.default_tags = None
        self.junit = None
        self.logging_format = None
        self.logging_datefmt = None
        self.name = None
        self.scope = None
        self.steps_catalog = None
        self.userdata = None
        self.wip = None
        self.verbose = verbose

        defaults = self.defaults.copy()
        for name, value in six.iteritems(kwargs):
            defaults[name] = value
        self.defaults = defaults
        self.formatters = []
        self.reporters = []
        self.name_re = None
        self.outputs = []
        self.include_re = None
        self.exclude_re = None
        self.scenario_outline_annotation_schema = None  # pylint: disable=invalid-name
        self.steps_dir = "steps"
        self.environment_file = "environment.py"
        self.userdata_defines = None
        self.more_formatters = None
        self.more_runners = None
        self.runner_aliases = dict(default=DEFAULT_RUNNER_CLASS_NAME)
        if load_config:
            load_configuration(self.defaults, verbose=verbose)
        parser = setup_parser()
        parser.set_defaults(**self.defaults)
        args = parser.parse_args(command_args)
        for key, value in six.iteritems(args.__dict__):
            if key.startswith("_") and key not in self.cmdline_only_options:
                continue
            setattr(self, key, value)

        # -- ATTRIBUTE-NAME-CLEANUP:
        self.tag_expression = None
        self._tags = self.tags
        self.tags = None
        if isinstance(self.default_tags, six.string_types):
            self.default_tags = self.default_tags.split()

        self.paths = [os.path.normpath(path) for path in self.paths]
        self.setup_outputs(args.outfiles)

        if self.steps_catalog:
            # -- SHOW STEP-CATALOG: As step summary.
            self.default_format = "steps.catalog"
            if self.format:
                self.format.append("steps.catalog")
            else:
                self.format = ["steps.catalog"]
            self.dry_run = True
            self.summary = False
            self.show_skipped = False
            self.quiet = True

        if self.wip:
            # Only run scenarios tagged with "wip".
            # Additionally:
            #  * use the "plain" formatter (per default)
            #  * do not capture stdout or logging output and
            #  * stop at the first failure.
            self.default_format = "plain"
            self._tags = ["wip"] + self.default_tags
            self.color = False
            self.stop = True
            self.log_capture = False
            self.stdout_capture = False

        self.tag_expression = make_tag_expression(self._tags or self.default_tags)
        # -- BACKWARD-COMPATIBLE (BAD-NAMING STYLE; deprecating):
        self.tags = self.tag_expression

        if self.quiet:
            self.show_source = False
            self.show_snippets = False

        if self.exclude_re:
            self.exclude_re = re.compile(self.exclude_re)

        if self.include_re:
            self.include_re = re.compile(self.include_re)
        if self.name:
            # -- SELECT: Scenario-by-name, build regular expression.
            self.name_re = self.build_name_re(self.name)

        if self.stage is None:  # pylint: disable=access-member-before-definition
            # -- USE ENVIRONMENT-VARIABLE, if stage is undefined.
            self.stage = os.environ.get("BEHAVE_STAGE", None)
        self.setup_stage(self.stage)
        self.setup_model()
        self.setup_userdata()
        self.setup_runner_aliases()

        # -- FINALLY: Setup Reporters and Formatters
        # NOTE: Reporters and Formatters can now use userdata information.
        if self.junit:
            # Buffer the output (it will be put into Junit report)
            self.stdout_capture = True
            self.stderr_capture = True
            self.log_capture = True
            self.reporters.append(JUnitReporter(self))
        if self.summary:
            self.reporters.append(SummaryReporter(self))

        self.setup_formats()
        bad_formats_and_errors = self.select_bad_formats_with_errors()
        if bad_formats_and_errors:
            bad_format_parts = []
            for name, error in bad_formats_and_errors:
                message = "%s (problem: %s)" % (name, error)
                bad_format_parts.append(message)
            parser.error("BAD_FORMAT=%s" % ", ".join(bad_format_parts))

    def setup_outputs(self, args_outfiles=None):
        if self.outputs:
            assert not args_outfiles, "ONLY-ONCE"
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
            for name, scoped_class_name in self.more_formatters.items():
                _format_registry.register_as(name, scoped_class_name)

    def setup_runner_aliases(self):
        if self.more_runners:
            for name, scoped_class_name in self.more_runners.items():
                self.runner_aliases[name] = scoped_class_name

    def select_bad_formats_with_errors(self):
        bad_formats = []
        if self.format:
            for format_name in self.format:
                formatter_valid = _format_registry.is_formatter_valid(format_name)
                if format_name == "help" or formatter_valid:
                    continue

                try:
                    _ = _format_registry.select_formatter_class(format_name)
                    bad_formats.append((format_name, "InvalidClassError"))
                except Exception as e:
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

    def setup_logging(self, level=None, configfile=None, **kwargs):
        """
        Support simple setup of logging subsystem.
        Ensures that the logging level is set.
        But note that the logging setup can only occur once.

        SETUP MODES:
          * :func:`logging.config.fileConfig()`, if ``configfile`` is provided.
          * :func:`logging.basicConfig()`, otherwise.

        .. code-block: python
            # -- FILE: features/environment.py
            def before_all(context):
                context.config.setup_logging()

        :param level:       Logging level of root logger.
                            If None, use :attr:`logging_level` value.
        :param configfile:  Configuration filename for fileConfig() setup.
        :param kwargs:      Passed to :func:`logging.basicConfig()`
        """
        if level is None:
            level = self.logging_level      # pylint: disable=no-member

        if configfile:
            from logging.config import fileConfig
            fileConfig(configfile)
        else:
            # pylint: disable=no-member
            format_ = kwargs.pop("format", self.logging_format)
            datefmt = kwargs.pop("datefmt", self.logging_datefmt)
            logging.basicConfig(format=format_, datefmt=datefmt, **kwargs)
        # -- ENSURE: Default log level is set
        #    (even if logging subsystem is already configured).
        logging.getLogger().setLevel(level)

    def setup_model(self):
        if self.scenario_outline_annotation_schema:
            name_schema = six.text_type(self.scenario_outline_annotation_schema)
            ScenarioOutline.annotation_schema = name_schema.strip()

    def setup_stage(self, stage=None):
        """Setup the test stage that selects a different set of
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
        steps_dir = "steps"
        environment_file = "environment.py"
        if stage:
            # -- USE A TEST STAGE: Select different set of implementations.
            prefix = stage + "_"
            steps_dir = prefix + steps_dir
            environment_file = prefix + environment_file
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
