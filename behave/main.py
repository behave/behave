# -*- coding: utf-8 -*-

import sys

from behave import __version__
from behave.configuration import Configuration, ConfigError
from behave.formatter.ansi_escapes import escapes
from behave.i18n import languages
from behave.formatter import formatters
from behave.runner import Runner, make_undefined_step_snippet
from behave.parser import ParserError

TAG_HELP = """
Scenarios inherit tags declared on the Feature level. The simplest
TAG_EXPRESSION is simply a tag::

    --tags @dev

You may even leave off the "@" - behave doesn't mind.

When a tag in a tag expression starts with a ~, this represents boolean NOT::

    --tags ~@dev

A tag expression can have several tags separated by a comma, which represents
logical OR::

    --tags @dev,@wip

The --tags option can be specified several times, and this represents logical
AND, for instance this represents the boolean expression
"(@foo or not @bar) and @zap"::

    --tags @foo,~@bar --tags @zap.

Beware that if you want to use several negative tags to exclude several tags
you have to use logical AND::

    --tags ~@fixme --tags ~@buggy.
""".strip()

# TODO: Enable positive Tags w/ threshold
# Positive tags can be given a threshold to limit the number of occurrences.
# Which can be practical if you are practicing Kanban or CONWIP. This will fail
# if there are more than 3 occurrences of the @qa tag:
#
# --tags @qa:3
# """.strip()

# -- WORKMARK: issue #47: Formatter processing chain is broken
# Disable multi-formatter until issue is solved.
# Can be reenabled by local behave script for exploration/fixing the problem.
DISABLE_MULTI_FORMATTERS = True


def main():
    # pylint: disable=R0912,R0915
    #   R0912   Too many branches (17/12)
    #   R0915   Too many statements (57/50)
    config = Configuration()

    if config.version:
        print "behave " + __version__
        sys.exit(0)

    if config.tags_help:
        print TAG_HELP
        sys.exit(0)

    if config.lang_list:
        iso_codes = languages.keys()
        iso_codes.sort()
        print "Languages available:"
        for iso_code in iso_codes:
            native = languages[iso_code]['native'][0]
            name = languages[iso_code]['name'][0]
            print u'%s: %s / %s' % (iso_code, native, name)
        sys.exit(0)

    if config.lang_help:
        if config.lang_help not in languages:
            sys.exit('%s is not a recognised language: try --lang-list' %
                     config.lang_help)
        trans = languages[config.lang_help]
        print u"Translations for %s / %s" % (trans['name'][0],
              trans['native'][0])
        for kw in trans:
            if kw in 'name native'.split():
                continue
            print u'%16s: %s' % (kw.title().replace('_', ' '),
                  u', '.join(w for w in trans[kw] if w != '*'))
        sys.exit(0)

    if not config.format:
        default_format = config.defaults["default_format"]
        config.format = [ default_format ]
    elif config.format and "format" in config.defaults:
        # -- CASE: Formatter are specified in behave configuration file.
        #    Check if formatter are provided on command-line, too.
        if len(config.format) == len(config.defaults["format"]):
            # -- NO FORMATTER on command-line: Add default formatter.
            default_format = config.defaults["default_format"]
            config.format.append(default_format)
    elif 'help' in config.format:
        print "Available formatters:"
        formatters.list_formatters(sys.stdout)
        sys.exit(0)

    if len(config.outputs) > len(config.format):
        print 'CONFIG-ERROR: More outfiles (%d) than formatters (%d).' % \
              (len(config.outputs), len(config.format))
        sys.exit(1)

    runner = Runner(config)
    try:
        failed = runner.run()
    except ParserError, e:
        sys.exit(str(e))
    except ConfigError, e:
        sys.exit(str(e))

    if config.show_snippets and runner.undefined:
        msg = u"\nYou can implement step definitions for undefined steps with "
        msg += u"these snippets:\n\n"
        printed = set()
        for step in runner.undefined:
            if step in printed:
                continue
            printed.add(step)
            msg += make_undefined_step_snippet(step)

        # -- OOPS: Unclear if stream supports ANSI coloring.
        sys.stderr.write(escapes['undefined'] + msg + escapes['reset'])
        sys.stderr.flush()

    if failed:
        sys.exit(1)
    # -- OTHERWISE: Successful run.
    sys.exit(0)

if __name__ == '__main__':
    main()
