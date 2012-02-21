import sys

from behave.configuration import Configuration, ConfigError
from behave.formatter.ansi_escapes import escapes
from behave.i18n import languages
from behave.formatter import formatters
from behave.runner import Runner
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


def main():
    config = Configuration()

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
        config.format = ['pretty']
    elif config.format == ['help']:
        print "Available formatters:"
        formatters.list_formatters(sys.stdout)
        sys.exit(0)

    stream = config.output

    runner = Runner(config)
    try:
        failed = runner.run()
    except ParserError, e:
        sys.exit(str(e))
    except ConfigError, e:
        sys.exit(str(e))

    if config.show_snippets and runner.undefined:
        msg = "\nYou can implement step definitions for undefined steps with "
        msg += "these snippets:\n\n"
        printed = set()
        for step in runner.undefined:
            if step in printed:
                continue
            printed.add(step)

            msg += "@" + step.step_type + "(" + repr(step.name) + ")\n"
            msg += "def step(context):\n"
            msg += "    assert False\n\n"

        stream.write(escapes['undefined'] + msg + escapes['reset'])
        stream.flush()

    if failed:
        sys.exit(1)

if __name__ == '__main__':
    main()
