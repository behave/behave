import collections
import os
import os.path
import sys
import time
import traceback

import yaml

from behave import model, parser, runner
from behave.configuration import Configuration
from behave.formatter.ansi_escapes import escapes
from behave.formatter.pretty_formatter import PrettyFormatter

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

class Language(object):
    @classmethod
    def load(cls, language_name, default_language_name="en"):
        directory, _f = os.path.split(os.path.abspath(__file__))
        language_path = os.path.join(directory, 'languages.yml')
        languages = yaml.load(open(language_path))
        if language_name not in languages:
            return None
        return cls(languages[language_name], languages[default_language_name])

    def __init__(self, mappings, default_mappings=None):
        self.mappings = mappings
        self.default_mappings = default_mappings

    def words(self, key):
        """
        Give all the synonymns of a word in the requested language
        (or the default language if no word is available).
        """
        if self.default_mappings is not None and key not in self.mappings:
            return self.default_mappings[key].encode('utf').split("|")
        else:
            return self.mappings[key].encode('utf').split("|")

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

    if config.tags and config.tags == 'help':
        print TAG_HELP
        sys.exit(0)

    if not config.paths:
        config.paths = ['features']

    passed = []
    failed = []
    undefined = []
    skipped = []

    stream = sys.stdout

    start = os.path.abspath(config.paths[0])
    if not os.path.isdir(start):
        start = os.path.dirname(start)
    while not os.path.isdir(os.path.join(start, 'step_definitions')):
        start = os.path.dirname(start)
        if start == os.getcwd():
            start = None
            break

    if start:
        step_defs_dir = os.path.join(start, 'step_definitions')
        sys.path.insert(0, step_defs_dir)
        for name in os.listdir(step_defs_dir):
            if name.endswith('.py'):
                __import__(name[:-3])
            elif os.path.isdir(os.path.join(step_defs_dir, name)):
                dirname = os.path.join(step_defs_dir, name)
                if os.path.exists(os.path.join(dirname, '__init__.py')):
                    __import__(name)

    context = runner.Context()
    features = []

    for filename in feature_files(config.paths):
        context.reset_feature()

        feature = parser.parse_file(os.path.abspath(filename), Language.load('en'))
        features.append(feature)

        feature_match = config.tags.check(feature.tags)

        formatter = PrettyFormatter(stream, False, False)
        formatter.uri(filename)
        formatter.feature(feature)
        if feature.has_background():
            formatter.background(feature.background)

        for scenario in feature:
            run_steps = feature_match or config.tags.check(scenario.tags)

            formatter.scenario(scenario)

            context.reset_scenario()

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
                        try:
                            start = time.time()
                            match.run(context)
                            elapsed = time.time() - start
                            step.status = 'passed'
                            step.duration = elapsed
                        except:
                            elapsed = time.time() - start
                            error = traceback.format_exc()
                            step.status = 'failed'
                            step.duration = elapsed
                            step.error_message = error
                            run_steps = False

                        formatter.result(step)
                else:
                    step.status = 'skipped'
                    if scenario.status is None:
                        scenario.status = 'skipped'

        formatter.eof()

        print ''

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
                part = '{:d} {:s} {:s}'.format(summary[status], label, status)
                first = False
            else:
                part = '{:d} {:s}'.format(summary[status], status)
            parts.append(part)
        return ', '.join(parts) + '\n'
        
    stream.write(format_summary('feature', feature_summary))
    stream.write(format_summary('scenario', scenario_summary))
    stream.write(format_summary('step', step_summary))
        
    if undefined:
        msg =  "You can implement step definitions for undefined steps with "
        msg += "these snippets:\n\n"
        printed = set()
        for step in undefined:
            if step in printed:
                continue
            printed.add(step)

            func_name = step.name.lower().replace(' ', '_')
            msg += "@" + step.keyword + "('" + step.name + "')\n"
            msg += "def " + func_name + "(context):\n"
            msg += "    assert False\n\n"

        stream.write(escapes['undefined'] + msg + escapes['reset'])
        stream.flush()
