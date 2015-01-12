# -*- coding: utf-8 -*-

import sys

from behave import __version__
from behave.configuration import Configuration, ConfigError
from behave.runner import Runner
from behave.runner_util import print_undefined_step_snippets, \
    InvalidFileLocationError, InvalidFilenameError, FileNotFoundError
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

# TODO
# Positive tags can be given a threshold to limit the number of occurrences.
# Which can be practical if you are practicing Kanban or CONWIP. This will fail
# if there are more than 3 occurrences of the @qa tag:
#
# --tags @qa:3
# """.strip()


def main(args=None):
    config = Configuration(args)
    if config.version:
        print "behave " + __version__
        return 0

    if config.tags_help:
        print TAG_HELP
        return 0

    if config.lang_list:
        from behave.i18n import languages
        iso_codes = languages.keys()
        iso_codes.sort()
        print "Languages available:"
        for iso_code in iso_codes:
            native = languages[iso_code]['native'][0]
            name = languages[iso_code]['name'][0]
            print u'%s: %s / %s' % (iso_code, native, name)
        return 0

    if config.lang_help:
        from behave.i18n import languages
        if config.lang_help not in languages:
            print '%s is not a recognised language: try --lang-list' % \
                    config.lang_help
            return 1
        trans = languages[config.lang_help]
        print u"Translations for %s / %s" % (trans['name'][0],
              trans['native'][0])
        for kw in trans:
            if kw in 'name native'.split():
                continue
            print u'%16s: %s' % (kw.title().replace('_', ' '),
                  u', '.join(w for w in trans[kw] if w != '*'))
        return 0

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
    if 'help' in config.format:
        from behave.formatter import formatters
        print "Available formatters:"
        formatters.list_formatters(sys.stdout)
        return 0

    if len(config.outputs) > len(config.format):
        print 'CONFIG-ERROR: More outfiles (%d) than formatters (%d).' % \
              (len(config.outputs), len(config.format))
        return 1

    failed = True
    runner = Runner(config)
    try:
        failed = runner.run()
    except ParserError, e:
        print "ParseError: %s" % e
    except ConfigError, e:
        print "ConfigError: %s" % e
    except FileNotFoundError, e:
        print "FileNotFoundError: %s" % e
    except InvalidFileLocationError, e:
        print "InvalidFileLocationError: %s" % e
    except InvalidFilenameError, e:
        print "InvalidFilenameError: %s" % e

    if config.show_snippets and runner.undefined:
        print_undefined_step_snippets(runner.undefined)

    return_code = 0
    if failed:
        return_code = 1
    return return_code

if __name__ == '__main__':
    # -- EXAMPLE: main("--version")
    sys.exit(main())
