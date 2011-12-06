import os
import sys
import argparse
import ConfigParser

from behave.tag_expression import TagExpression


class ConfigError(Exception):
    pass


options = [
#    (('-b', '--backtrace'), dict(action='store_true',
#         help="Show full backtraces for all errors.")),
    (('-c', '--no-color'), dict(action='store_true',
         help="Disable the use of ANSI color escapes.")),
    (('-d', '--dry-run'), dict(action='store_true',
         help="Invokes formatters without executing the steps.")),
#    (('-e', '--exclude'), dict(metavar="PATTERN",
#         help="Don't run feature files matching PATTERN.")),
    (('-f', '--format'), dict(action='append',
         help="""Specify a formatter. By default the 'pretty'
                 formatter is used. Pass '--format help' to get a
                 list of available formatters.""")),
#    (('-g', '--guess'), dict(action='store_true',
#         help="Guess best match for ambiguous steps.")),
    (('-i', '--no-snippets'), dict(action='store_true',
         help="Don't print snippets for pending steps.")),
    (('-m', '--no-multiline'), dict(action='store_true',
         help="""Don't print multiline strings and tables under
                 steps.""")),
    (('-n', '--name'), dict(action="append",
         help="""Only execute the feature elements which match part
                 of the given name. If this option is given more
                 than once, it will match against all the given
                 names.""")),
    (('--nocapture',), dict(action='store_false', dest='stdout_capture',
         help="""Don't capture stdout (any stdout output will be
                 printed immediately.)""")),
    (('--nologcapture',), dict(action='store_false', dest='log_capture',
         help="""Don't capture logging. Logging configuration will
                 be left intact.""")),
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
             Specify which statements to filter in/out. By default,
             everything is captured. If the output is too verbose,
             use this option to filter out needless output.
             Example: --logging-filter=foo will capture statements
             issued ONLY to foo or foo.what.ever.sub but not foobar
             or other logger. Specify multiple loggers with comma:
             filter=foo,bar,baz. If any logger name is prefixed
             with a minus, eg filter=-foo, it will be excluded
             rather than included.""")),
    (('--logging-clear-handlers',), dict(action='store_true',
             help="Clear all other logging handlers")),
    (('-o', '--outfile'), dict(metavar='FILE',
         help="Write to specified file instead of stdout.")),
    (('-q', '--quiet'), dict(action='store_true',
         help="Alias for --no-snippets --no-source.")),
    (('-s', '--no-source'), dict(action='store_true',
         help="""Don't print the file and line of the step
                 definition with the steps.""")),
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
         help="Fail if there are any passing scenarios.")),
    (('-x', '--expand'), dict(action='store_true',
         help="Expand scenario outline tables in output.")),
    (('--lang',), dict(metavar='LANG',
         help="Use keywords for a language other than English.")),
    (('--lang-list',), dict(action='store_true',
         help="List the languages abailable for --lang")),
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
        elif action in ('store_true','store_false'):
            result[dest] = cfg.getboolean('behave', dest)
        elif action == 'append':
            if dest == 'tags':
                c = '&'
            else:
                c = ','
            result[dest] = [s.strip() for s in cfg.get('behave', dest).split(c)]
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

        defaults = dict(
            stdout_capture=True,
            log_capture=True,
            dry_run=False,
            logging_format='%(levelname)s:%(name)s:%(message)s',
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

        self.tags = TagExpression(self.tags or [])
