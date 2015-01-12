# -*- coding: utf-8 -*-

import os
import re
import sys
import argparse
import ConfigParser
import logging
import shlex

from behave.model import FileLocation
from behave.reporter.junit import JUnitReporter
from behave.reporter.summary import SummaryReporter
from behave.tag_expression import TagExpression
from behave.formatter.base import StreamOpener
from behave.formatter.formatters import formatters as registered_formatters


class Unknown(object): pass

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


class ConfigError(Exception):
    pass


options = [
    (('-c', '--no-color'),
     dict(action='store_false', dest='color',
          help="Disable the use of ANSI color escapes.")),

    (('--color',),
     dict(action='store_true', dest='color',
          help="""Use ANSI color escapes. This is the default
                  behaviour. This switch is used to override a
                  configuration file setting.""")),

    (('-d', '--dry-run'),
     dict(action='store_true',
          help="Invokes formatters without executing the steps.")),

    (('--processes',),
     dict(metavar="NUMBER", dest='proc_count',
          help="""Use multiple pids to do the work faster.
		Not all options work properly under parallel mode. See README.md 
		""")),

    (('--parallel-element',),
     dict(metavar="STRING", dest='parallel_element',
          help="""If you used the --processes option, then this will control how the tests get parallelized.
		Valid values are 'feature' or 'scenario'. Anything else will error. See readme for more
		info on how this works.
		""")),

    (('-e', '--exclude'),
     dict(metavar="PATTERN", dest='exclude_re',
          help="""Don't run feature files matching regular expression
                  PATTERN.""")),

    (('-i', '--include'),
     dict(metavar="PATTERN", dest='include_re',
          help="Only run feature files matching regular expression PATTERN.")),

    (('--no-junit',),
     dict(action='store_false', dest='junit',
          help="Don't output JUnit-compatible reports.")),

    (('--junit',),
     dict(action='store_true',
          help="""Output JUnit-compatible reports.
                  When junit is enabled, all stdout and stderr
                  will be redirected and dumped to the junit report,
                  regardless of the '--capture' and '--no-capture' options.
                  """)),

    (('--junit-directory',),
     dict(metavar='PATH', dest='junit_directory',
          default='reports',
          help="""Directory in which to store JUnit reports.""")),

    ((),  # -- CONFIGFILE only
     dict(dest='default_format',
          help="Specify default formatter (default: pretty).")),

    (('-f', '--format'),
     dict(action='append',
          help="""Specify a formatter. If none is specified the default
                  formatter is used. Pass '--format help' to get a
                  list of available formatters.""")),

#    (('-g', '--guess'),
#     dict(action='store_true',
#          help="Guess best match for ambiguous steps.")),

    (('-k', '--no-skipped'),
     dict(action='store_false', dest='show_skipped',
          help="Don't print skipped steps (due to tags).")),

    (('--show-skipped',),
     dict(action='store_true',
          help="""Print skipped steps.
                  This is the default behaviour. This switch is used to
                  override a configuration file setting.""")),

    (('--no-snippets',),
     dict(action='store_false', dest='show_snippets',
          help="Don't print snippets for unimplemented steps.")),
    (('--snippets',),
     dict(action='store_true', dest='show_snippets',
          help="""Print snippets for unimplemented steps.
                  This is the default behaviour. This switch is used to
                  override a configuration file setting.""")),

    (('-m', '--no-multiline'),
     dict(action='store_false', dest='show_multiline',
          help="""Don't print multiline strings and tables under
                  steps.""")),

    (('--multiline', ),
     dict(action='store_true', dest='show_multiline',
          help="""Print multiline strings and tables under steps.
                  This is the default behaviour. This switch is used to
                  override a configuration file setting.""")),

    (('-n', '--name'),
     dict(action="append",
          help="""Only execute the feature elements which match part
                  of the given name. If this option is given more
                  than once, it will match against all the given
                  names.""")),

    (('--no-capture',),
     dict(action='store_false', dest='stdout_capture',
          help="""Don't capture stdout (any stdout output will be
                  printed immediately.)""")),

    (('--capture',),
     dict(action='store_true', dest='stdout_capture',
          help="""Capture stdout (any stdout output will be
                  printed if there is a failure.)
                  This is the default behaviour. This switch is used to
                  override a configuration file setting.""")),

    (('--no-capture-stderr',),
     dict(action='store_false', dest='stderr_capture',
          help="""Don't capture stderr (any stderr output will be
                  printed immediately.)""")),

    (('--capture-stderr',),
     dict(action='store_true', dest='stderr_capture',
          help="""Capture stderr (any stderr output will be
                  printed if there is a failure.)
                  This is the default behaviour. This switch is used to
                  override a configuration file setting.""")),

    (('--no-logcapture',),
     dict(action='store_false', dest='log_capture',
          help="""Don't capture logging. Logging configuration will
                  be left intact.""")),

    (('--logcapture',),
     dict(action='store_true', dest='log_capture',
          help="""Capture logging. All logging during a step will be captured
                  and displayed in the event of a failure.
                  This is the default behaviour. This switch is used to
                  override a configuration file setting.""")),

    (('--logging-level',),
     dict(type=LogLevel.parse_type,
          help="""Specify a level to capture logging at. The default
                  is INFO - capturing everything.""")),

    (('--logging-format',),
     dict(help="""Specify custom format to print statements. Uses the
                  same format as used by standard logging handlers. The
                  default is '%%(levelname)s:%%(name)s:%%(message)s'.""")),

    (('--logging-datefmt',),
     dict(help="""Specify custom date/time format to print
                  statements.
                  Uses the same format as used by standard logging
                  handlers.""")),

    (('--logging-filter',),
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

    (('--logging-clear-handlers',),
     dict(action='store_true',
          help="Clear all other logging handlers.")),

    (('--no-summary',),
     dict(action='store_false', dest='summary',
          help="""Don't display the summary at the end of the run.""")),

    (('--summary',),
     dict(action='store_true', dest='summary',
          help="""Display the summary at the end of the run.""")),

    (('-o', '--outfile'),
     dict(action='append', dest='outfiles', metavar='FILE',
          help="Write to specified file instead of stdout.")),

    ((),  # -- CONFIGFILE only
     dict(action='append', dest='paths',
          help="Specify default feature paths, used when none are provided.")),

    (('-q', '--quiet'),
     dict(action='store_true',
          help="Alias for --no-snippets --no-source.")),

    (('-s', '--no-source'),
     dict(action='store_false', dest='show_source',
          help="""Don't print the file and line of the step definition with the
                  steps.""")),

    (('--show-source',),
     dict(action='store_true', dest='show_source',
          help="""Print the file and line of the step
                  definition with the steps. This is the default
                  behaviour. This switch is used to override a
                  configuration file setting.""")),

    (('--stop',),
     dict(action='store_true',
          help='Stop running tests at the first failure.')),

    # -- DISABLE-UNUSED-OPTION: Not used anywhere.
    # (('-S', '--strict'),
    # dict(action='store_true',
    #    help='Fail if there are any undefined or pending steps.')),

    (('-t', '--tags'),
     dict(action='append', metavar='TAG_EXPRESSION',
          help="""Only execute features or scenarios with tags
                  matching TAG_EXPRESSION. Pass '--tags-help' for
                  more information.""",
          config_help="""Only execute certain features or scenarios based
                         on the tag expression given. See below for how to code
                         tag expressions in configuration files.""")),

    (('-T', '--no-timings'),
     dict(action='store_false', dest='show_timings',
          help="""Don't print the time taken for each step.""")),

    (('--show-timings',),
     dict(action='store_true', dest='show_timings',
          help="""Print the time taken, in seconds, of each step after the
                  step has completed. This is the default behaviour. This
                  switch is used to override a configuration file
                  setting.""")),

    (('-v', '--verbose'),
     dict(action='store_true',
          help='Show the files and features loaded.')),

    (('-w', '--wip'),
     dict(action='store_true',
          help="""Only run scenarios tagged with "wip". Additionally: use the
                  "plain" formatter, do not capture stdout or logging output
                  and stop at the first failure.""")),

    (('-x', '--expand'),
     dict(action='store_true',
          help="Expand scenario outline tables in output.")),

    (('--lang',),
     dict(metavar='LANG',
          help="Use keywords for a language other than English.")),

    (('--lang-list',),
     dict(action='store_true',
          help="List the languages available for --lang.")),

    (('--lang-help',),
     dict(metavar='LANG',
          help="List the translations accepted for one language.")),

    (('--tags-help',),
     dict(action='store_true',
          help="Show help for tag expressions.")),

    (('--version',),
     dict(action='store_true', help="Show version.")),
]

# -- OPTIONS: With raw value access semantics in configuration file.
raw_value_options = frozenset([
    "logging_format",
    "logging_datefmt"
])

def read_configuration(path):
    cfg = ConfigParser.SafeConfigParser()
    cfg.read(path)
    cfgdir = os.path.dirname(path)
    result = {}
    for fixed, keywords in options:
        if 'dest' in keywords:
            dest = keywords['dest']
        else:
            for opt in fixed:
                if opt.startswith('--'):
                    dest = opt[2:].replace('-', '_')
                else:
                    assert len(opt) == 2
                    dest = opt[1:]
        if dest in 'tags_help lang_list lang_help version'.split():
            continue
        if not cfg.has_option('behave', dest):
            continue
        action = keywords.get('action', 'store')
        if action == 'store':
            use_raw_value = dest in raw_value_options
            result[dest] = cfg.get('behave', dest, use_raw_value)
        elif action in ('store_true', 'store_false'):
            result[dest] = cfg.getboolean('behave', dest)
        elif action == 'append':
            result[dest] = \
                [s.strip() for s in cfg.get('behave', dest).splitlines()]
        else:
            raise ValueError('action "%s" not implemented' % action)

    if 'format' in result:
        # -- OPTIONS: format/outfiles are coupled in configuration file.
        formatters = result['format']
        formatter_size = len(formatters)
        outfiles = result.get('outfiles', [])
        outfiles_size = len(outfiles)
        if outfiles_size < formatter_size:
            for formatter_name in formatters[outfiles_size:]:
                outfile = "%s.output" % formatter_name
                outfiles.append(outfile)
            result['outfiles'] = outfiles
        elif len(outfiles) > formatter_size:
            print "CONFIG-ERROR: Too many outfiles (%d) provided." % outfiles_size
            result['outfiles'] = outfiles[:formatter_size]

    for paths_name in ('paths', 'outfiles'):
        if paths_name in result:
            # -- Evaluate relative paths relative to configfile location.
            # NOTE: Absolute paths are preserved by os.path.join().
            paths = result[paths_name]
            result[paths_name] = \
                [os.path.normpath(os.path.join(cfgdir, p)) for p in paths]

    return result


def load_configuration(defaults, verbose=False):
    paths = ['./', os.path.expanduser('~')]
    if sys.platform in ('cygwin', 'win32') and 'APPDATA' in os.environ:
        paths.append(os.path.join(os.environ['APPDATA']))

    for path in paths:
        for filename in 'behave.ini .behaverc'.split():
            filename = os.path.join(path, filename)
            if os.path.isfile(filename):
                if verbose:
                    print 'Loading config defaults from "%s"' % filename
                defaults.update(read_configuration(filename))

    if verbose:
        print 'Using defaults:'
        for k, v in defaults.items():
            print '%15s %s' % (k, v)


# construct the parser
#usage = "%(prog)s [options] [ [FILE|DIR|URL][:LINE[:LINE]*] ]+"
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
    if 'config_help' in keywords:
        keywords = dict(keywords)
        del keywords['config_help']
    parser.add_argument(*fixed, **keywords)
parser.add_argument('paths', nargs='*',
                help='Feature directory, file or file location (FILE:LINE).')


class Configuration(object):
    defaults = dict(
        color=sys.platform != 'win32',
        show_snippets=True,
        show_skipped=True,
        dry_run=False,
        show_source=True,
        show_timings=True,
        stdout_capture=True,
        stderr_capture=True,
        log_capture=True,
        logging_format='%(levelname)s:%(name)s:%(message)s',
        logging_level=logging.INFO,
        summary=True,
        junit=False,
        # -- SPECIAL:
        default_format="pretty",   # -- Used when no formatters are configured.
    )

    def __init__(self, command_args=None, verbose=None):
        """
        Constructs a behave configuration object.
          * loads the configuration defaults.
          * process the command-line args
          * store the configuration results

        :param command_args: Provide command args (as sys.argv).
            If command_args is None, sys.argv[1:] is used.
        :type command_args: list<str>, str
        :param verbose: Indicate if diagnostic output is enabled
        """
        if command_args is None:
            command_args = sys.argv[1:]
        elif isinstance(command_args, basestring):
            command_args = shlex.split(command_args)
        if verbose is None:
            # -- AUTO-DISCOVER: Verbose mode from command-line args.
            verbose = ('-v' in command_args) or ('--verbose' in command_args)

        self.formatters = []
        self.reporters = []
        self.name_re = None
        self.outputs = []
        self.include_re = None
        self.exclude_re = None
        load_configuration(self.defaults, verbose=verbose)
        parser.set_defaults(**self.defaults)
        args = parser.parse_args(command_args)
        for key, value in args.__dict__.items():
            if key.startswith('_'):
                continue
            setattr(self, key, value)

        self.paths = [os.path.normpath(path) for path in self.paths]
        if not args.outfiles:
            self.outputs.append(StreamOpener(stream=sys.stdout))
        else:
            for outfile in args.outfiles:
                if outfile and outfile != '-':
                    self.outputs.append(StreamOpener(outfile))
                else:
                    self.outputs.append(StreamOpener(stream=sys.stdout))

        if self.wip:
            # Only run scenarios tagged with "wip". Additionally: use the
            # "plain" formatter, do not capture stdout or logging output and
            # stop at the first failure.
            self.format = ['plain']
            self.tags = ['wip']
            self.stop = True
            self.log_capture = False
            self.stdout_capture = False

        self.tags = TagExpression(self.tags or [])

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

        if self.junit:
            # Buffer the output (it will be put into Junit report)
            self.stdout_capture = True
            self.stderr_capture = True
            self.log_capture = True
            self.reporters.append(JUnitReporter(self))
        if self.summary:
            self.reporters.append(SummaryReporter(self))

        unknown_formats = self.collect_unknown_formats()
        if unknown_formats:
            parser.error("format=%s is unknown" % ", ".join(unknown_formats))

    def collect_unknown_formats(self):
        unknown_formats = []
        if self.format:
            for formatter in self.format:
                if formatter == "help":
                    continue
                elif formatter not in registered_formatters:
                    unknown_formats.append(formatter)
        return unknown_formats

    @staticmethod
    def build_name_re(names):
        """
        Build regular expression for scenario selection by name
        by using a list of name parts or name regular expressions.

        :param names: List of name parts or regular expressions (as text).
        :return: Compiled regular expression to use.
        """
        pattern = u"|".join(names)
        return re.compile(pattern, flags=(re.UNICODE | re.LOCALE))

    def exclude(self, filename):
        if isinstance(filename, FileLocation):
            filename = str(filename)

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
          * :func:`logging.config.fileConfig()`, if ``configfile` is provided.
          * :func:`logging.basicConfig(), otherwise.

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
            level = self.logging_level

        if configfile:
            from logging.config import fileConfig
            fileConfig(configfile)
        else:
            format = kwargs.pop("format", self.logging_format)
            datefmt = kwargs.pop("datefmt", self.logging_datefmt)
            logging.basicConfig(format=format, datefmt=datefmt, **kwargs)
        # -- ENSURE: Default log level is set
        #    (even if logging subsystem is already configured).
        logging.getLogger().setLevel(level)
