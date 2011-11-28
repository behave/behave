import os.path
import StringIO
import sys
import time
import traceback

from behave import matchers, model, parser
from behave.formatter.pretty_formatter import PrettyFormatter
from behave.log_capture import MemoryHandler
from behave.configuration import ConfigError


class Context(object):
    def __init__(self):
        self._stack = [{}]

    def _push(self):
        self._stack.insert(0, {})

    def _pop(self):
        self._stack.pop(0)

    def _dump(self):
        for level, frame in enumerate(self._stack):
            print 'Level %d' % level
            print repr(frame)

    def __getattr__(self, attr):
        for frame in self._stack:
            if attr in frame:
                return frame[attr]
        msg = "'{0}' object has no attribute '{1}'"
        msg = msg.format(self.__class__.__name__, attr)
        raise AttributeError(msg)

    def __setattr__(self, attr, value):
        if attr == '_stack':
            self.__dict__['_stack'] = value
            return

        frame = self.__dict__['_stack'][0]
        frame[attr] = value


class StepRegistry(object):
    def __init__(self):
        self.steps = {
            'given': [],
            'when': [],
            'then': [],
            'step': [],
        }

    def add_definition(self, keyword, string, func):
        self.steps[keyword.lower()].append(matchers.get_matcher(func, string))

    def find_match(self, step):
        candidates = self.steps[step.step_type]
        if step.step_type is not 'step':
            candidates += self.steps['step']

        for matcher in candidates:
            result = matcher.match(step.name)
            if result:
                return result

        return None


def exec_file(filename, globals={}, locals=None):
    if locals is None:
        locals = globals
    if sys.version_info[0] == 3:
        with open(filename) as f:
            exec(f.read(), globals, locals)
    else:
        execfile(filename, globals, locals)


class PathManager(object):
    paths = None
    def __enter__(self):
        self.paths = []
    def __exit__(self, *crap):
        for path in self.paths:
            sys.path.remove(path)
    def add(self, path):
        assert self.paths is not None, \
            self.__class__.__name__ + '.add called outside of context'
        sys.path.insert(0, path)
        self.paths.append(path)


class Runner(object):
    def __init__(self, config):
        self.config = config

        self.steps = StepRegistry()
        self.hooks = {}

        self.features = []
        self.passed = []
        self.failed = []
        self.undefined = []
        self.skipped = []

        self.path_manager = PathManager()

        self.feature = None

        self.feature_summary = {'passed': 0, 'failed': 0, 'skipped': 0}
        self.scenario_summary = {'passed': 0, 'failed': 0, 'skipped': 0}
        self.step_summary = {'passed': 0, 'failed': 0, 'skipped': 0,
                             'undefined': 0}
        self.duration = 0.0

    def setup_paths(self):
        if self.config.paths:
            if self.config.verbose:
                print 'Supplied path:', ', '.join('"%s"' % path
                    for path in self.config.paths)
            base_dir = os.path.abspath(self.config.paths[0])

            # supplied path might be to a feature file
            if os.path.isfile(base_dir):
                if self.config.verbose:
                    print 'Primary path is to a file so using its directory'
                base_dir = os.path.dirname(base_dir)
        else:
            if self.config.verbose:
                print 'Using default path "./features"'
            base_dir = os.path.abspath('features')

        new_base_dir = base_dir

        while True:
            if self.config.verbose:
                print 'Trying base directory:', new_base_dir

            if os.path.isdir(os.path.join(new_base_dir, 'steps')):
                break
            if os.path.isfile(os.path.join(new_base_dir, 'environment.py')):
                break
            if new_base_dir == '/':
                break

            new_base_dir = os.path.dirname(new_base_dir)

        if new_base_dir == '/':
            if self.config.verbose:
                if not self.config.paths:
                    print 'ERROR: Could not find "steps" directory. Please '\
                        'specify where to find your features.'
                else:
                    print 'ERROR: Could not find "steps" directory in your '\
                        'specified path "%s"' % base_dir
            raise ConfigError('No steps directory in "%s"' % base_dir)

        base_dir = new_base_dir

        for dirpath, dirnames, filenames in os.walk(base_dir):
            if [fn for fn in filenames if fn.endswith('.feature')]:
                break
        else:
            if self.config.verbose:
                if not self.config.paths:
                    print 'ERROR: Could not find any "<name>.feature" files. '\
                        'Please specify where to find your features.'
                else:
                    print 'ERROR: Could not find any "<name>.feature" files '\
                        'in your specified path "%s"' % base_dir
            raise ConfigError('No feature files in "%s"' % base_dir)

        self.base_dir = base_dir
        self.path_manager.add(base_dir)
        if not self.config.paths:
            self.config.paths = [base_dir]

        if base_dir != os.getcwd():
            self.path_manager.add(os.getcwd())

    def load_hooks(self, filename='environment.py'):
        hooks_path = os.path.join(self.base_dir, filename)
        if os.path.exists(hooks_path):
            exec_file(hooks_path, self.hooks)

    def make_step_decorator(self, step_type):
        def decorator(string):
            def wrapper(func):
                self.steps.add_definition(step_type, string, func)
                return func
            return wrapper
        return decorator

    def execute_steps(self, steps):
        for step in steps.strip().split('\n'):
            step = step.strip()
            step_obj = self.feature.parser.parse_step(step)
            if step_obj is None:
                return False
            passed = self.run_step(step_obj, quiet=True)
            if not passed:
                assert False, "Sub-step failed: %s" % step
        return

    def load_step_definitions(self, extra_step_paths=[]):
        steps_dir = os.path.join(self.base_dir, 'steps')

        # allow steps to import other stuff from the steps dir
        sys.path.insert(0, steps_dir)

        step_globals = {
            'execute_steps': self.execute_steps,
            'step_matcher': matchers.step_matcher,
        }
        for step_type in ('given', 'when', 'then', 'step'):
            step_globals[step_type] = self.make_step_decorator(step_type)
            step_globals[step_type.title()] = step_globals[step_type]

        for path in [steps_dir] + list(extra_step_paths):
            for name in os.listdir(path):
                if name.endswith('.py'):
                    execfile(os.path.join(path, name), step_globals)

        # clean up the path
        sys.path.pop(0)

    def run_hook(self, name, *args):
        if name in self.hooks:
            self.hooks[name](*args)

    def feature_files(self):
        files = []
        for path in self.config.paths:
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

    def run(self):
        with self.path_manager:
            self.setup_paths()
            self.run_with_paths()

    def run_with_paths(self):
        self.load_hooks()
        self.load_step_definitions()

        context = self.context = Context()
        stream = self.config.output
        monochrome = self.config.no_color
        failed = False

        self.run_hook('before_all', context)

        for filename in self.feature_files():
            context._push()

            feature = parser.parse_file(os.path.abspath(filename))
            self.features.append(feature)
            self.feature = feature

            self.formatter = PrettyFormatter(stream, monochrome, True)
            self.formatter.uri(filename)
            self.formatter.feature(feature)

            run_feature = self.config.tags.check(feature.tags)

            if run_feature:
                for tag in feature.tags:
                    self.run_hook('before_tag', context, tag)
                self.run_hook('before_feature', context, feature)

            if feature.background:
                self.formatter.background(feature.background)

            for scenario in feature:
                tags = feature.tags + scenario.tags
                run_scenario = self.config.tags.check(tags)
                run_steps = run_scenario

                self.formatter.scenario(scenario)

                context._push()

                if run_scenario:
                    for tag in scenario.tags:
                        self.run_hook('before_tag', context, tag)
                    self.run_hook('before_scenario', context, scenario)

                if self.config.stdout_capture:
                    self.stdout_capture = StringIO.StringIO()

                if self.config.log_capture:
                    self.log_capture = MemoryHandler(self.config)
                    self.log_capture.inveigle()

                for step in scenario:
                    self.formatter.step(step)

                for step in scenario:
                    if run_steps:
                        if not self.run_step(step):
                            run_steps = False
                            failed = True
                    else:
                        step.status = 'skipped'
                        if scenario.status is None:
                            scenario.status = 'skipped'

                if self.config.log_capture:
                    self.log_capture.abandon()

                if run_scenario:
                    self.run_hook('after_scenario', context, scenario)
                    for tag in scenario.tags:
                        self.run_hook('after_tag', context, tag)

                context._pop()

            self.formatter.eof()

            if run_feature:
                self.run_hook('after_feature', context, feature)
                for tag in feature.tags:
                    self.run_hook('after_tag', context, tag)

            context._pop()

            stream.write('\n')

        self.run_hook('after_all', context)

        self.calculate_summaries()

        return failed

    def run_step(self, step, quiet=False):
        match = self.steps.find_match(step)
        if match is None:
            self.undefined.append(step)
            if not quiet:
                self.formatter.match(model.NoMatch())
            step.status = 'undefined'
            if not quiet:
                self.formatter.result(step)
            return False

        keep_going = True

        if not quiet:
            self.formatter.match(match)
        self.run_hook('before_step', self.context, step)
        if self.config.stdout_capture:
            old_stdout = sys.stdout
            sys.stdout = self.stdout_capture
        try:
            start = time.time()
            if step.table:
                self.context.table = step.table
            match.run(self.context)
            step.status = 'passed'
        except AssertionError, e:
            step.status = 'failed'
            error = 'Assertion Failed: %s' % (e, )
        except Exception:
            step.status = 'failed'
            error = traceback.format_exc()

        step.duration = time.time() - start

        # stop snarfing these guys
        if self.config.stdout_capture:
            sys.stdout = old_stdout

        # flesh out the failure with details
        if step.status == 'failed':
            if self.config.stdout_capture:
                output = self.stdout_capture.getvalue()
                if output:
                    error += '\nCaptured stdout:\n' + output
            if self.config.log_capture:
                output = self.log_capture.getvalue()
                if output:
                    error += '\nCaptured logging:\n' + output
            step.error_message = error
            keep_going = False

        if not quiet:
            self.formatter.result(step)
        self.run_hook('after_step', self.context, step)

        return keep_going

    def calculate_summaries(self):
        for feature in self.features:
            self.feature_summary[feature.status or 'skipped'] += 1
            for scenario in feature:
                self.scenario_summary[scenario.status or 'skipped'] += 1
                for step in scenario:
                    self.step_summary[step.status or 'skipped'] += 1
                    self.duration += step.duration or 0.0
