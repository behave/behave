import argparse
import sys

from gherkin.i18n import I18n

from behave.configuration import Configuration

parser = argparse.ArgumentParser(usage="%(prog)s [options] [ [FILE|DIR|URL][:LINE[:LINE]*] ]+")

parser.add_argument('-b', '--backtrace', action='store_true',
                    help="Show full backtraces for all errors.")
parser.add_argument('-c', '--no-color', action='store_true',
                    help="Disable the use of ANSI color escapes.")
parser.add_argument('-d', '--dry-run', action='store_true',
                    help="Invokes formatters without executing the steps.")
parser.add_argument('-e', '--exclude', metavar="PATTERN",
                    help="Don't run feature files matching PATTERN.")
parser.add_argument('-f', '--format', action='append',
                    help="""Add a formatter. By default, only a 'pretty'
                            formatter is used. Pass '--format help' to get a
                            list of available formatters.""")
parser.add_argument('-g', '--guess', action='store_true',
                    help="Guess best match for ambiguous steps.")
parser.add_argument('-i', '--no-snippets', action='store_true',
                    help="Don't print snippets for pending steps.")
parser.add_argument('-m', '--no-multiline', action='store_true',
                    help="""Don't print multiline strings and tables under
                            steps.""")
parser.add_argument('-n', '--name', action="append",
                    help="""Only execute the feature elements which match part
                            of the given name. If this option is given more than
                            once, it will match against all the given names.""")
parser.add_argument('-o', '--out', action='append', metavar='FILE|DIR',
                    help="""Write to specified file or directory instead of
                            stdout. This option applies to the immediately
                            preceding formatter or the default formatter if no
                            formatters have yet been specified. Check the
                            documentation for each formatter to see if they
                            require a file or a directory.""")
parser.add_argument('-q', '--quiet', action='store_true',
                    help="Alias for --no-snippets --no-source.")
parser.add_argument('-s', '--no-source', action='store_true',
                    help="""Don't print the file and line of the step
                            definition with the steps.""")
parser.add_argument('-S', '--strict', action='store_true',
                    help='Fail if there are any undefined or pending steps.')
parser.add_argument('-t', '--tags', action='append', metavar='TAG_EXPRESSION',
                    help="""Only execute features or scenarios with tags
                            matching TAG_EXPRESSION. Pass '--tags help' for
                            more information.""")
parser.add_argument('-v', '--verbose', action='store_true',
                    help='Show the files and features loaded.')
parser.add_argument('-w', '--wip', action='store_true',
                    help="Fail if there are any passing scenarios.")
parser.add_argument('-x', '--expand', action='store_true',
                    help="Expand scenario outline tables in output.")
parser.add_argument('--i18n', metavar='LANG',
                    help="""List keywords for a particular language
                            (use --i18n help to see all languages)""")
parser.add_argument('--version', action='store_true', help="Show version.")

parser.add_argument('files', nargs='*')

def main():
    args = parser.parse_args()

    if args.i18n:
        if args.i18n.lower() == 'help':
            Configuration.output.write(I18n.language_table())
        else:
            Configuration.output.write(I18n.get(args.i18n).keyword_table())
        sys.exit(0)
    
    if args.tags and args.tags[0] == 'help':
        print """
Scenarios inherit tags declared on the Feature level. The simplest
TAG_EXPRESSION is simply a tag:

--tags @dev

When a tag in a tag expression starts with a ~, this represents boolean NOT:

--tags ~@dev

A tag expression can have several tags separated by a comma, which represents
logical OR:

--tags @dev,@wip

The --tags option can be specified several times, and this represents logical
AND, for instance this represents the boolean expression
(@foo || !@bar) && @zap:

--tags @foo,~@bar --tags @zap.

Beware that if you want to use several negative tags to exclude several tags
you have to use logical AND:

--tags ~@fixme --tags ~@buggy.

Positive tags can be given a threshold to limit the number of occurrences. Which
can be practical if you are practicing Kanban or CONWIP. This will fail if there
are more than 3 occurrences of the @qa tag:

--tags @qa:3
"""