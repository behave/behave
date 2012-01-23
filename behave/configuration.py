import os
import re
import sys
import argparse
import ConfigParser

from behave.reporter.junit import JUnitReporter
from behave.reporter.summary import SummaryReporter
from behave.tag_expression import TagExpression


class ConfigError(Exception):
    pass


options = [
    (('-c', '--no-color'), dict(action='store_false', dest='color',
         help="Disable the use of ANSI color escapes.")),
    (('--color',), dict(action='store_true', dest='color',
         help="""Use ANSI color escapes. This is the default
                 behaviour. This switch is used to override a
                 configuration file setting.""")),
    (('-d', '--dry-run'), dict(action='store_true',
         help="Invokes formatters without executing the steps.")),
    (('-e', '--exclude'), dict(metavar="PATTERN", dest='exclude_re',
         help="Don't run feature files matching regular expression PATTERN.")),
    (('-i', '--include'), dict(metavar="PATTERN", dest='include_re',
         help="Only run feature files matching regular expression PATTERN.")),
    (('--no-junit',), dict(action='store_false', dest='junit',
         help="Don't output JUnit-compatible reports.")),
    (('--junit',), dict(action='store_true',
         help="""Output JUnit-compatible reports.""")),
    (('--junit-directory',), dict(metavar='PATH', dest='junit_directory',
         default='reports',
         help="""Directory in which to store JUnit reports.""")),
    (('-f', '--format'), dict(action='append',
         help="""Specify a formatter. By default the 'pretty'
                 formatter is used. Pass '--format help' to get a
                 list of available formatters.""")),
#    (('-g', '--guess'), dict(action='store_true',
#         help="Guess best match for ambiguous steps.")),

    (('-k', '--no-skipped'), dict(action='store_false', dest='show_skipped',
         help="Don't print skipped steps (due to tags).")),
    (('--show-skipped',), dict(action='store_true',
         help="""Print skipped steps.
                 This is the default behaviour. This switch is used to override
                 a configuration file setting.""")),
    (('--no-snippets',), dict(action='store_false', dest='show_snippets',
         help="Don't print snippets for unimplemented steps.")),
    (('--snippets',), dict(action='store_true',
         help="""Print snippets for unimplemented steps.
                 This is the default behaviour. This switch is used to override
                 a configuration file setting.""")),
    (('-m', '--no-multiline'), dict(action='store_false',
         dest='show_multiline',
         help="""Don't print multiline strings and tables under
                 steps.""")),
    (('--multiline', ), dict(action='store_true', dest='show_multiline',
         help="""Print multiline strings and tables under steps.
                 This is the default behaviour. This switch is used to override
                 a configuration file setting.""")),
    (('-n', '--name'), dict(action="append",
         help="""Only execute the feature elements which match part
                 of the given name. If this option is given more
                 than once, it will match against all the given
                 names.""")),
    (('--no-capture',), dict(action='store_false', dest='stdout_capture',
         help="""Don't capture stdout (any stdout output will be
                 printed immediately.)""")),
    (('--capture',), dict(action='store_true', dest='stdout_capture',
         help="""Capture stdout (any stdout output will be
                 printed if there is a failure.)
                 This is the default behaviour. This switch is used to override
                 a configuration file setting.""")),
    (('--no-logcapture',), dict(action='store_false', dest='log_capture',
         help="""Don't capture logging. Logging configuration will
                 be left intact.""")),
    (('--logcapture',), dict(action='store_true', dest='log_capture',
         help="""Capture logging. All logging during a step will be captured
                 and displayed in the event of a failure.
                 This is the default behaviour. This switch is used to override
                 a configuration file setting.""")),
    (('--logging-format',), dict(
         help="""Specify custom format to print statements. Uses the
             same format as used by standard logging handlers. The
             default is '%%(levelname)s:%%(name)s:%%(message)s'.""")),
    (('--logging-level',), dict(
         help="""Specify a level to capture logging at. The default
             is NOTSET - capturing everything.""")),
    (('--logging-datefmt',), dict(
         help="""Specify custom date/time format to print
                 statements.
                 Uses the same format as used by standard logging
                 handlers.""")),
    (('--logging-filter',), dict(
         help="""
             Specify which statements to filter in/out. By default, everything
             is captured. If the output is too verbose, use this option to
             filter out needless output.  Example: --logging-filter=foo will
             capture statements issued ONLY to foo or foo.what.ever.sub but not
             foobar or other logger. Specify multiple loggers with comma:
             filter=foo,bar,baz. If any logger name is prefixed with a minus,
             eg filter=-foo, it will be excluded rather than included.""",
         config_help="""
             Specify which statements to filter in/out. By default, everything
             is captured. If the output is too verbose, use this option to
             filter out needless output.  Example: ``logging_filter = foo``
             will capture statements issued ONLY to "foo" or
             "foo.what.ever.sub" but not "foobar" or other logger. Specify
             multiple loggers with comma: ``logging_filter = foo,bar,baz``. If
             any logger name is prefixed with a minus, eg
             ``logging_filter = -foo``, it will be excluded rather than
             included.""")),
    (('--logging-clear-handlers',), dict(action='store_true',
             help="Clear all other logging handlers.")),
    (('--no-summary',), dict(action='store_false', dest='summary',
         help="""Don't display the summary at the end of the run.""")),
    (('--summary',), dict(action='store_true', dest='summary',
         help="""Display the summary at the end of the run.""")),
    (('-o', '--outfile'), dict(metavar='FILE',
         help="Write to specified file instead of stdout.")),
    (('-q', '--quiet'), dict(action='store_true',
         help="Alias for --no-snippets --no-source.")),
    (('-s', '--no-source'), dict(action='store_false', dest='show_source',
         help="""Don't print the file and line of the step
                 definition with the steps.""")),
    (('--show-source',), dict(action='store_true', dest='show_source',
         help="""Print the file and line of the step
                 definition with the steps. This is the default
                 behaviour. This switch is used to override a
                 configuration file setting.""")),
    (('--stop',), dict(action='store_true',
         help='Stop running tests at the first failure.')),
    (('-S', '--strict'), dict(action='store_true',
         help='Fail if there are any undefined or pending steps.')),
    (('-t', '--tags'), dict(action='append', metavar='TAG_EXPRESSION',
         help="""Only execute features or scenarios with tags
                 matching TAG_EXPRESSION. Pass '--tag-help' for
                 more information.""",
         config_help="""Only execute certain features or scenarios based
                 on the tag expression given. See below for how to code
                 tag expressions in configuration files.""")),
    (('-v', '--verbose'), dict(action='store_true',
         help='Show the files and features loaded.')),
    (('-w', '--wip'), dict(action='store_true',
         help="""Only run scenarios tagged with "wip". Additionally: use the
                 "plain" formatter, do not capture stdout or logging output and
                 stop at the first failure.""")),
    (('-x', '--expand'), dict(action='store_true',
         help="Expand scenario outline tables in output.")),
    (('--lang',), dict(metavar='LANG',
         help="Use keywords for a language other than English.")),
    (('--lang-list',), dict(action='store_true',
         help="List the languages available for --lang.")),
    (('--lang-help',), dict(metavar='LANG',
         help="List the translations accepted for one language.")),
    (('--tags-help',), dict(action='store_true',
         help="Show help for tag expressions.")),
    (('--version',), dict(action='store_true', help="Show version.")),
]


def read_configuration(path):
    cfg = ConfigParser.ConfigParser()
    cfg.read(path)
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
            result[dest] = cfg.get('behave', dest)
        elif action in ('store_true', 'store_false'):
            result[dest] = cfg.getboolean('behave', dest)
        elif action == 'append':
            result[dest] = \
                [s.strip() for s in cfg.get('behave', dest).splitlines()]
        else:
            raise ValueError('action "%s" not implemented' % action)
    return result


def load_configuration(defaults):
    paths = ['./', os.path.expanduser('~')]
    if sys.platform in ('cygwin', 'win32') and 'APPDATA' in os.environ:
        paths.append(os.path.join(os.environ['APPDATA']))

    verbose = ('-v' in sys.argv) or ('--verbose' in sys.argv)

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
usage = "%(prog)s [options] [ [FILE|DIR] ]+"
parser = argparse.ArgumentParser(usage=usage)
for fixed, keywords in options:
    if 'config_help' in keywords:
        keywords = dict(keywords)
        del keywords['config_help']
    parser.add_argument(*fixed, **keywords)
parser.add_argument('paths', nargs='*')


class Configuration(object):
    def __init__(self):
        self.formatters = []
        self.reporters = []

        defaults = dict(
            color=True,
            stdout_capture=True,
            show_snippets=True,
            show_skipped=True,
            log_capture=True,
            dry_run=False,
            show_source=True,
            logging_format='%(levelname)s:%(name)s:%(message)s',
            summary=True,
            junit=False,
        )
        load_configuration(defaults)
        parser.set_defaults(**defaults)

        args = parser.parse_args()
        for key, value in args.__dict__.items():
            if key.startswith('_'):
                continue
            setattr(self, key, value)

        if args.outfile and args.outfile != '-':
            self.output = open(args.outfile, 'w')
        else:
            self.output = sys.stdout

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

        if self.junit:
            self.reporters.append(JUnitReporter(self))
        if self.summary:
            self.reporters.append(SummaryReporter(self))

    def exclude(self, filename):
        if self.include_re and self.include_re.search(filename) is None:
            return True
        if self.exclude_re and self.exclude_re.search(filename) is not None:
            return True
        return False
