import sys

from behave.configuration import Configuration, ConfigError
from behave.formatter.ansi_escapes import escapes
from behave.runner import Runner

TAG_HELP = """
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

Positive tags can be given a threshold to limit the number of occurrences.
Which can be practical if you are practicing Kanban or CONWIP. This will fail
if there are more than 3 occurrences of the @qa tag:

--tags @qa:3
""".strip()


def main():
    config = Configuration()

    if config.tags_help:
        print TAG_HELP
        sys.exit(0)

    #if not config.paths:
        #config.paths = ['features']

    stream = config.output

    runner = Runner(config)
    try:
        failed = runner.run()
    except ConfigError, e:
        sys.exit(str(e))

    def format_summary(statement_type, summary):
        first = True
        parts = []
        for status in ('passed', 'failed', 'skipped', 'undefined'):
            if status not in summary:
                continue
            if first:
                label = statement_type
                if summary[status] != 1:
                    label += 's'
                part = '{0:d} {1:s} {2:s}'.format(summary[status], label,
                                                  status)
                first = False
            else:
                part = '{0:d} {1:s}'.format(summary[status], status)
            parts.append(part)
        return ', '.join(parts) + '\n'

    stream.write(format_summary('feature', runner.feature_summary))
    stream.write(format_summary('scenario', runner.scenario_summary))
    stream.write(format_summary('step', runner.step_summary))

    if runner.undefined:
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
