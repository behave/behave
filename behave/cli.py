import collections
import os
import os.path
import StringIO
import sys
import time
import traceback
import logging

import yaml

from behave import decorators, model, parser, runner
from behave.configuration import Configuration
from behave.formatter.ansi_escapes import escapes
from behave.formatter.pretty_formatter import PrettyFormatter
from behave.log_capture import MemoryHandler

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

Positive tags can be given a threshold to limit the number of occurrences. Which
can be practical if you are practicing Kanban or CONWIP. This will fail if there
are more than 3 occurrences of the @qa tag:

--tags @qa:3
""".strip()

def feature_files(paths):
    files = []
    for path in paths:
        if os.path.isdir(path):
            for dirpath, dirnames, filenames in os.walk(path):
                for filename in filenames:
                    if filename.endswith('.feature'):
                        files.append(os.path.join(dirpath, filename))
        elif path.startswith('@'):
            files.extend([filename.strip() for filename in open(path)])
        elif os.path.exists(path):
            files.append(path)
        else:
            raise Exception("Can't find path: " + path)
    return files

def main():
    config = Configuration()

    if config.tags_help:
        print TAG_HELP
        sys.exit(0)

    if not config.paths:
        config.paths = ['features']

    passed = []
    failed = []
    undefined = []
    skipped = []

    stream = sys.stdout

    base_dir = os.path.abspath(config.paths[0])
    if not os.path.isdir(base_dir):
        base_dir = os.path.dirname(base_dir)
    while not os.path.isdir(os.path.join(base_dir, 'steps')):
        base_dir = os.path.dirname(base_dir)
        if base_dir == os.getcwd():
            base_dir = None
            break

    hooks = {}

    if base_dir:
        sys.path.insert(0, base_dir)

        steps_dir = os.path.join(base_dir, 'steps')

        # allow steps to import other stuff from the steps dir
        sys.path.insert(0, steps_dir)

        for name in os.listdir(steps_dir):
            step_globals = {}
            for step_type in ('given', 'when', 'then', 'step'):
                step_globals[step_type] = getattr(decorators, step_type)
                step_type = step_type.title()
                step_globals[step_type] = getattr(decorators, step_type)

            if name.endswith('.py'):
                execfile(os.path.join(steps_dir, name), step_globals)

        # clean up the path
        sys.path.pop(0)

        hooks_path = os.path.join(base_dir, 'environment.py')
        if os.path.exists(hooks_path):
            execfile(hooks_path, hooks)

    def run_hook(name, *args):
        if name in hooks:
            hooks[name](*args)

    context = runner.Context()
    features = []

    run_hook('before_all', context)

    for filename in feature_files(config.paths):
        context._push()

        feature = parser.parse_file(os.path.abspath(filename))
        features.append(feature)

        formatter = PrettyFormatter(stream, False, True)
        formatter.uri(filename)
        formatter.feature(feature)

        run_hook('before_feature', context, feature)

        if feature.background:
            formatter.background(feature.background)

        for scenario in feature:
            run_scenario = config.tags.check(feature.tags + scenario.tags)
            run_steps = run_scenario

            formatter.scenario(scenario)

            context._push()

            if run_scenario:
                run_hook('before_scenario', context, scenario)

            for step in scenario:
                formatter.step(step)

            for step in scenario:
                if run_steps:
                    match = runner.steps.find_match(step)
                    if match is None:
                        undefined.append(step)
                        formatter.match(model.NoMatch())
                        step.status = 'undefined'
                        formatter.result(step)
                        run_steps = False
                    else:
                        formatter.match(match)
                        run_hook('before_step', context, step)
                        old_stdout = sys.stdout
                        stdout_capture = sys.stdout = StringIO.StringIO()
                        log = MemoryHandler()
                        log.inveigle()
                        try:
                            start = time.time()
                            match.run(context)
                            step.status = 'passed'
                        except AssertionError, e:
                            step.status = 'failed'
                            error = 'Assertion Failed: %s' % (e, )
                        except Exception:
                            step.status = 'failed'
                            error = traceback.format_exc()

                        step.duration = time.time() - start

                        # stop snarfing these guys
                        log.abandon()
                        sys.stdout = old_stdout

                        # flesh out the failure with details
                        if step.status == 'failed':
                            output = stdout_capture.getvalue()
                            if output:
                                error += '\nCaptured stdout:\n' + output
                            if log:
                                error += '\nCaptured logging:\n' + log.getvalue()
                            step.error_message = error
                            run_steps = False

                        formatter.result(step)
                        run_hook('after_step', context, step)
                else:
                    step.status = 'skipped'
                    if scenario.status is None:
                        scenario.status = 'skipped'

            if run_scenario:
                run_hook('after_scenario', context, scenario)

            context._pop()

        formatter.eof()

        run_hook('after_feature', context, feature)

        context._pop()

        print ''

    run_hook('after_all', context)

    feature_summary = {'passed': 0, 'failed': 0, 'skipped': 0}
    scenario_summary = {'passed': 0, 'failed': 0, 'skipped': 0}
    step_summary = {'passed': 0, 'failed': 0, 'skipped': 0, 'undefined': 0}
    duration = 0.0

    for feature in features:
        feature_summary[feature.status or 'skipped'] += 1
        for scenario in feature:
            scenario_summary[scenario.status or 'skipped'] += 1
            for step in scenario:
                step_summary[step.status or 'skipped'] += 1
                duration += step.duration or 0.0

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
                part = '{0:d} {1:s} {2:s}'.format(summary[status], label, status)
                first = False
            else:
                part = '{0:d} {1:s}'.format(summary[status], status)
            parts.append(part)
        return ', '.join(parts) + '\n'

    stream.write(format_summary('feature', feature_summary))
    stream.write(format_summary('scenario', scenario_summary))
    stream.write(format_summary('step', step_summary))

    if undefined:
        msg =  "\nYou can implement step definitions for undefined steps with "
        msg += "these snippets:\n\n"
        printed = set()
        for step in undefined:
            if step in printed:
                continue
            printed.add(step)

            func_name = step.name.lower().replace(' ', '_')
            msg += "@" + step.keyword + "('" + step.name + "')\n"
            msg += "def step(context):\n"
            msg += "    assert False\n\n"

        stream.write(escapes['undefined'] + msg + escapes['reset'])
        stream.flush()
