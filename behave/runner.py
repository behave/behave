# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function, with_statement
import contextlib
import os.path
import six
from six import StringIO
import sys
import traceback
import warnings
import weakref

from behave import matchers
from behave.step_registry import setup_step_decorators
from behave.formatter._registry import make_formatters
from behave.configuration import ConfigError
from behave.log_capture import LoggingCapture
from behave.runner_util import collect_feature_locations, parse_features


class ContextMaskWarning(UserWarning):
    '''Raised if a context variable is being overwritten in some situations.

    If the variable was originally set by user code then this will be raised if
    *behave* overwites the value.

    If the variable was originally set by *behave* then this will be raised if
    user code overwites the value.
    '''
    pass


class Context(object):
    '''Hold contextual information during the running of tests.

    This object is a place to store information related to the tests you're
    running. You may add arbitrary attributes to it of whatever value you need.

    During the running of your tests the object will have additional layers of
    namespace added and removed automatically. There is a "root" namespace and
    additional namespaces for features and scenarios.

    Certain names are used by *behave*; be wary of using them yourself as
    *behave* may overwrite the value you set. These names are:

    .. attribute:: feature

      This is set when we start testing a new feature and holds a
      :class:`~behave.model.Feature`. It will not be present outside of a
      feature (i.e. within the scope of the environment before_all and
      after_all).

    .. attribute:: scenario

      This is set when we start testing a new scenario (including the
      individual scenarios of a scenario outline) and holds a
      :class:`~behave.model.Scenario`. It will not be present outside of the
      scope of a scenario.

    .. attribute:: tags

      The current set of active tags (as a Python set containing instances of
      :class:`~behave.model.Tag` which are basically just glorified strings)
      combined from the feature and scenario. This attribute will not be
      present outside of a feature scope.

    .. attribute:: aborted

      This is set to true in the root namespace when the user aborts a test run
      (:exc:`KeyboardInterrupt` exception). Initially: False.

    .. attribute:: failed

      This is set to true in the root namespace as soon as a step fails.
      Initially: False.

    .. attribute:: table

      This is set at the step level and holds any :class:`~behave.model.Table`
      associated with the step.

    .. attribute:: text

      This is set at the step level and holds any multiline text associated
      with the step.

    .. attribute:: config

      The configuration of *behave* as determined by configuration files and
      command-line options. The attributes of this object are the same as the
      `configuration file settion names`_.

    .. attribute:: active_outline

      This is set for each scenario in a scenario outline and references the
      :class:`~behave.model.Row` that is active for the current scenario. It is
      present mostly for debugging, but may be useful otherwise.

    .. attribute:: log_capture

      If logging capture is enabled then this attribute contains the captured
      logging as an instance of :class:`~behave.log_capture.LoggingCapture`.
      It is not present if logging is not being captured.

    .. attribute:: stdout_capture

      If stdout capture is enabled then this attribute contains the captured
      output as a StringIO instance. It is not present if stdout is not being
      captured.

    .. attribute:: stderr_capture

      If stderr capture is enabled then this attribute contains the captured
      output as a StringIO instance. It is not present if stderr is not being
      captured.

    If an attempt made by user code to overwrite one of these variables, or
    indeed by *behave* to overwite a user-set variable, then a
    :class:`behave.runner.ContextMaskWarning` warning will be raised.

    You may use the "in" operator to test whether a certain value has been set
    on the context, for example:

        'feature' in context

    checks whether there is a "feature" value in the context.

    Values may be deleted from the context using "del" but only at the level
    they are set. You can't delete a value set by a feature at a scenario level
    but you can delete a value set for a scenario in that scenario.

    .. _`configuration file settion names`: behave.html#configuration-files
    '''
    BEHAVE = 'behave'
    USER = 'user'

    def __init__(self, runner):
        self._runner = weakref.proxy(runner)
        self._config = runner.config
        d = self._root = {
            'aborted': False,
            'failed': False,
            'config': self._config,
            'active_outline': None,
        }
        self._stack = [d]
        self._record = {}
        self._origin = {}
        self._mode = self.BEHAVE
        self.feature = None

    def _push(self):
        self._stack.insert(0, {})

    def _pop(self):
        self._stack.pop(0)

    @contextlib.contextmanager
    def user_mode(self):
        try:
            self._mode = self.USER
            yield
        finally:
            # -- NOTE: Otherwise skipped if AssertionError/Exception is raised.
            self._mode = self.BEHAVE

    def _set_root_attribute(self, attr, value):
        for frame in self.__dict__['_stack']:
            if frame is self.__dict__['_root']:
                continue
            if attr in frame:
                record = self.__dict__['_record'][attr]
                params = {
                    'attr': attr,
                    'filename': record[0],
                    'line': record[1],
                    'function': record[3],
                }
                self._emit_warning(attr, params)

        self.__dict__['_root'][attr] = value
        if attr not in self._origin:
            self._origin[attr] = self._mode

    def _emit_warning(self, attr, params):
        msg = ''
        if self._mode is self.BEHAVE and self._origin[attr] is not self.BEHAVE:
            msg = "behave runner is masking context attribute '%(attr)s' " \
                  "orignally set in %(function)s (%(filename)s:%(line)s)"
        elif self._mode is self.USER:
            if self._origin[attr] is not self.USER:
                msg = "user code is masking context attribute '%(attr)s' " \
                      "orignally set by behave"
            elif self._config.verbose:
                msg = "user code is masking context attribute " \
                    "'%(attr)s'; see the tutorial for what this means"
        if msg:
            msg = msg % params
            warnings.warn(msg, ContextMaskWarning, stacklevel=3)

    def _dump(self):
        for level, frame in enumerate(self._stack):
            print('Level %d' % level)
            print(repr(frame))

    def __getattr__(self, attr):
        if attr[0] == '_':
            return self.__dict__[attr]
        for frame in self._stack:
            if attr in frame:
                return frame[attr]
        msg = "'{0}' object has no attribute '{1}'"
        msg = msg.format(self.__class__.__name__, attr)
        raise AttributeError(msg)

    def __setattr__(self, attr, value):
        if attr[0] == '_':
            self.__dict__[attr] = value
            return

        for frame in self._stack[1:]:
            if attr in frame:
                record = self._record[attr]
                params = {
                    'attr': attr,
                    'filename': record[0],
                    'line': record[1],
                    'function': record[3],
                }
                self._emit_warning(attr, params)

        stack_frame = traceback.extract_stack(limit=2)[0]
        self._record[attr] = stack_frame
        frame = self._stack[0]
        frame[attr] = value
        if attr not in self._origin:
            self._origin[attr] = self._mode

    def __delattr__(self, attr):
        frame = self._stack[0]
        if attr in frame:
            del frame[attr]
            del self._record[attr]
        else:
            msg = "'{0}' object has no attribute '{1}' at the current level"
            msg = msg.format(self.__class__.__name__, attr)
            raise AttributeError(msg)

    def __contains__(self, attr):
        if attr[0] == '_':
            return attr in self.__dict__
        for frame in self._stack:
            if attr in frame:
                return True
        return False

    def execute_steps(self, steps_text):
        '''The steps identified in the "steps" text string will be parsed and
        executed in turn just as though they were defined in a feature file.

        If the execute_steps call fails (either through error or failure
        assertion) then the step invoking it will fail.

        ValueError will be raised if this is invoked outside a feature context.

        Returns boolean False if the steps are not parseable, True otherwise.
        '''
        assert isinstance(steps_text, six.text_type), "Steps must be unicode."
        if not self.feature:
            raise ValueError('execute_steps() called outside of feature')

        # -- PREPARE: Save original context data for current step.
        # Needed if step definition that called this method uses .table/.text
        original_table = getattr(self, "table", None)
        original_text  = getattr(self, "text", None)

        self.feature.parser.variant = 'steps'
        steps = self.feature.parser.parse_steps(steps_text)
        for step in steps:
            passed = step.run(self._runner, quiet=True, capture=False)
            if not passed:
                # -- ISSUE #96: Provide more substep info to diagnose problem.
                step_line = u"%s %s" % (step.keyword, step.name)
                message = "%s SUB-STEP: %s" % (step.status.upper(), step_line)
                if step.error_message:
                    message += "\nSubstep info: %s" % step.error_message
                assert False, message

        # -- FINALLY: Restore original context data for current step.
        self.table = original_table
        self.text  = original_text
        return True


def exec_file(filename, globals={}, locals=None):
    if locals is None:
        locals = globals
    locals['__file__'] = filename
    with open(filename) as f:
        # -- FIX issue #80: exec(f.read(), globals, locals)
        # try:
        filename2 = os.path.relpath(filename, os.getcwd())
        code = compile(f.read(), filename2, 'exec')
        exec(code, globals, locals)
        # except Exception as e:
        #     e_text = _text(e)
        #     print("Exception %s: %s" % (e.__class__.__name__, e_text))
        #     raise


def path_getrootdir(path):
    """
    Extract rootdir from path in a platform independent way.

    POSIX-PATH EXAMPLE:
        rootdir = path_getrootdir("/foo/bar/one.feature")
        assert rootdir == "/"

    WINDOWS-PATH EXAMPLE:
        rootdir = path_getrootdir("D:\\foo\\bar\\one.feature")
        assert rootdir == r"D:\"
    """
    drive, _ = os.path.splitdrive(path)
    if drive:
        # -- WINDOWS:
        return drive + os.path.sep
    # -- POSIX:
    return os.path.sep


class PathManager(object):
    """
    Context manager to add paths to sys.path (python search path) within a scope
    """
    def __init__(self, paths=None):
        self.initial_paths = paths or []
        self.paths = None

    def __enter__(self):
        self.paths = list(self.initial_paths)
        sys.path = self.paths + sys.path

    def __exit__(self, *crap):
        for path in self.paths:
            sys.path.remove(path)
        self.paths = None

    def add(self, path):
        if self.paths is None:
            # -- CALLED OUTSIDE OF CONTEXT:
            self.initial_paths.append(path)
        else:
            sys.path.insert(0, path)
            self.paths.append(path)


class ModelRunner(object):
    """
    Test runner for a behave model (features).
    Provides the core functionality of a test runner and
    the functional API needed by model elements.

    .. attribute:: aborted

          This is set to true when the user aborts a test run
          (:exc:`KeyboardInterrupt` exception). Initially: False.
          Stored as derived attribute in :attr:`Context.aborted`.
    """

    def __init__(self, config, features=None):
        self.config = config
        self.features = features or []
        self.hooks = {}
        self.formatters = []
        self.undefined_steps = []

        self.context = None
        self.feature = None

        self.stdout_capture = None
        self.stderr_capture = None
        self.log_capture = None
        self.old_stdout = None
        self.old_stderr = None

    # @property
    def _get_aborted(self):
        value = False
        if self.context:
            value = self.context.aborted
        return value

    # @aborted.setter
    def _set_aborted(self, value):
        assert self.context
        self.context._set_root_attribute('aborted', bool(value))

    aborted = property(_get_aborted, _set_aborted,
                       doc="Indicates that test run is aborted by the user.")

    def run_hook(self, name, context, *args):
        if not self.config.dry_run and (name in self.hooks):
            # try:
            with context.user_mode():
                self.hooks[name](context, *args)
            # except KeyboardInterrupt:
            #     self.aborted = True
            #     if name not in ("before_all", "after_all"):
            #         raise

    def setup_capture(self):
        if not self.context:
            self.context = Context(self)

        if self.config.stdout_capture:
            self.stdout_capture = StringIO()
            self.context.stdout_capture = self.stdout_capture

        if self.config.stderr_capture:
            self.stderr_capture = StringIO()
            self.context.stderr_capture = self.stderr_capture

        if self.config.log_capture:
            self.log_capture = LoggingCapture(self.config)
            self.log_capture.inveigle()
            self.context.log_capture = self.log_capture

    def start_capture(self):
        if self.config.stdout_capture:
            # -- REPLACE ONLY: In non-capturing mode.
            if not self.old_stdout:
                self.old_stdout = sys.stdout
                sys.stdout = self.stdout_capture
            assert sys.stdout is self.stdout_capture

        if self.config.stderr_capture:
            # -- REPLACE ONLY: In non-capturing mode.
            if not self.old_stderr:
                self.old_stderr = sys.stderr
                sys.stderr = self.stderr_capture
            assert sys.stderr is self.stderr_capture

    def stop_capture(self):
        if self.config.stdout_capture:
            # -- RESTORE ONLY: In capturing mode.
            if self.old_stdout:
                sys.stdout = self.old_stdout
                self.old_stdout = None
            assert sys.stdout is not self.stdout_capture

        if self.config.stderr_capture:
            # -- RESTORE ONLY: In capturing mode.
            if self.old_stderr:
                sys.stderr = self.old_stderr
                self.old_stderr = None
            assert sys.stderr is not self.stderr_capture

    def teardown_capture(self):
        if self.config.log_capture:
            self.log_capture.abandon()

    def run_model(self, features=None):
        if not self.context:
            self.context = Context(self)
        if features is None:
            features = self.features

        # -- ENSURE: context.execute_steps() works in weird cases (hooks, ...)
        context = self.context
        self.setup_capture()
        self.run_hook('before_all', context)

        run_feature = not self.aborted
        failed_count = 0
        undefined_steps_initial_size = len(self.undefined_steps)
        for feature in features:
            if run_feature:
                try:
                    self.feature = feature
                    for formatter in self.formatters:
                        formatter.uri(feature.filename)

                    failed = feature.run(self)
                    if failed:
                        failed_count += 1
                        if self.config.stop or self.aborted:
                            # -- FAIL-EARLY: After first failure.
                            run_feature = False
                except KeyboardInterrupt:
                    self.aborted = True
                    failed_count += 1
                    run_feature = False

            # -- ALWAYS: Report run/not-run feature to reporters.
            # REQUIRED-FOR: Summary to keep track of untested features.
            for reporter in self.config.reporters:
                reporter.feature(feature)

        # -- AFTER-ALL:
        if self.aborted:
            print("\nABORTED: By user.")
        for formatter in self.formatters:
            formatter.close()
        self.run_hook('after_all', self.context)
        for reporter in self.config.reporters:
            reporter.end()
        # if self.aborted:
        #     print("\nABORTED: By user.")
        failed = ((failed_count > 0) or self.aborted or
                  (len(self.undefined_steps) > undefined_steps_initial_size))
        return failed

    def run(self):
        """
        Implements the run method by running the model.
        """
        self.context = Context(self)
        return self.run_model()


class Runner(ModelRunner):
    """
    Standard test runner for behave:

      * setup paths
      * loads environment hooks
      * loads step definitions
      * select feature files, parses them and creates model (elements)
    """
    def __init__(self, config):
        super(Runner, self).__init__(config)
        self.path_manager = PathManager()
        self.base_dir = None


    def setup_paths(self):
        if self.config.paths:
            if self.config.verbose:
                print('Supplied path:', \
                      ', '.join('"%s"' % path for path in self.config.paths))
            first_path = self.config.paths[0]
            if hasattr(first_path, "filename"):
                # -- BETTER: isinstance(first_path, FileLocation):
                first_path = first_path.filename
            base_dir = first_path
            if base_dir.startswith('@'):
                # -- USE: behave @features.txt
                base_dir = base_dir[1:]
                file_locations = self.feature_locations()
                if file_locations:
                    base_dir = os.path.dirname(file_locations[0].filename)
            base_dir = os.path.abspath(base_dir)

            # supplied path might be to a feature file
            if os.path.isfile(base_dir):
                if self.config.verbose:
                    print('Primary path is to a file so using its directory')
                base_dir = os.path.dirname(base_dir)
        else:
            if self.config.verbose:
                print('Using default path "./features"')
            base_dir = os.path.abspath('features')

        # Get the root. This is not guaranteed to be '/' because Windows.
        root_dir = path_getrootdir(base_dir)
        new_base_dir = base_dir
        steps_dir = self.config.steps_dir
        environment_file = self.config.environment_file

        while True:
            if self.config.verbose:
                print('Trying base directory:', new_base_dir)

            if os.path.isdir(os.path.join(new_base_dir, steps_dir)):
                break
            if os.path.isfile(os.path.join(new_base_dir, environment_file)):
                break
            if new_base_dir == root_dir:
                break

            new_base_dir = os.path.dirname(new_base_dir)

        if new_base_dir == root_dir:
            if self.config.verbose:
                if not self.config.paths:
                    print('ERROR: Could not find "%s" directory. '\
                          'Please specify where to find your features.' % \
                                steps_dir)
                else:
                    print('ERROR: Could not find "%s" directory in your '\
                        'specified path "%s"' % (steps_dir, base_dir))

            message = 'No %s directory in "%s"' % (steps_dir, base_dir)
            raise ConfigError(message)

        base_dir = new_base_dir
        self.config.base_dir = base_dir

        for dirpath, dirnames, filenames in os.walk(base_dir):
            if [fn for fn in filenames if fn.endswith('.feature')]:
                break
        else:
            if self.config.verbose:
                if not self.config.paths:
                    print('ERROR: Could not find any "<name>.feature" files. '\
                        'Please specify where to find your features.')
                else:
                    print('ERROR: Could not find any "<name>.feature" files '\
                        'in your specified path "%s"' % base_dir)
            raise ConfigError('No feature files in "%s"' % base_dir)

        self.base_dir = base_dir
        self.path_manager.add(base_dir)
        if not self.config.paths:
            self.config.paths = [base_dir]

        if base_dir != os.getcwd():
            self.path_manager.add(os.getcwd())

    def before_all_default_hook(self, context):
        """
        Default implementation for :func:`before_all()` hook.
        Setup the logging subsystem based on the configuration data.
        """
        context.config.setup_logging()

    def load_hooks(self, filename=None):
        filename = filename or self.config.environment_file
        hooks_path = os.path.join(self.base_dir, filename)
        if os.path.exists(hooks_path):
            exec_file(hooks_path, self.hooks)

        if 'before_all' not in self.hooks:
            self.hooks['before_all'] = self.before_all_default_hook

    def load_step_definitions(self, extra_step_paths=[]):
        step_globals = {
            'use_step_matcher': matchers.use_step_matcher,
            'step_matcher':     matchers.step_matcher, # -- DEPRECATING
        }
        setup_step_decorators(step_globals)

        # -- Allow steps to import other stuff from the steps dir
        # NOTE: Default matcher can be overridden in "environment.py" hook.
        steps_dir = os.path.join(self.base_dir, self.config.steps_dir)
        paths = [steps_dir] + list(extra_step_paths)
        with PathManager(paths):
            default_matcher = matchers.current_matcher
            for path in paths:
                for name in sorted(os.listdir(path)):
                    if name.endswith('.py'):
                        # -- LOAD STEP DEFINITION:
                        # Reset to default matcher after each step-definition.
                        # A step-definition may change the matcher 0..N times.
                        # ENSURE: Each step definition has clean globals.
                        # try:
                        step_module_globals = step_globals.copy()
                        exec_file(os.path.join(path, name), step_module_globals)
                        matchers.current_matcher = default_matcher
                        # except Exception as e:
                        #     e_text = _text(e)
                        #     print("Exception %s: %s" % (e.__class__.__name__, e_text))
                        #     raise

    def feature_locations(self):
        return collect_feature_locations(self.config.paths)


    def run(self):
        with self.path_manager:
            self.setup_paths()
            return self.run_with_paths()


    def run_with_paths(self):
        self.context = Context(self)
        self.load_hooks()
        self.load_step_definitions()

        # -- ENSURE: context.execute_steps() works in weird cases (hooks, ...)
        # self.setup_capture()
        # self.run_hook('before_all', self.context)

        # -- STEP: Parse all feature files (by using their file location).
        feature_locations = [ filename for filename in self.feature_locations()
                                    if not self.config.exclude(filename) ]
        features = parse_features(feature_locations, language=self.config.lang)
        self.features.extend(features)

        # -- STEP: Run all features.
        stream_openers = self.config.outputs
        self.formatters = make_formatters(self.config, stream_openers)
        return self.run_model()




