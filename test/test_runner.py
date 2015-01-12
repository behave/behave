# -*- coding: utf-8 -*-

from __future__ import with_statement
from collections import defaultdict
import os.path
import StringIO
import sys
import warnings
import tempfile

from mock import Mock, patch
from nose.tools import *
import unittest

from behave import model, parser, runner, step_registry
from behave.configuration import ConfigError
from behave.log_capture import LoggingCapture
from behave.formatter.base import StreamOpener


class TestContext(object):
    def setUp(self):
        r = Mock()
        self.config = r.config = Mock()
        r.config.verbose = False
        self.context = runner.Context(r)

    def test_user_mode_shall_restore_behave_mode(self):
        # -- CASE: No exception is raised.
        with self.context.user_mode():
            eq_(self.context._mode, runner.Context.USER)
            self.context.thing = 'stuff'
        eq_(self.context._mode, runner.Context.BEHAVE)

    def test_user_mode_shall_restore_behave_mode_if_assert_fails(self):
        try:
            with self.context.user_mode():
                eq_(self.context._mode, runner.Context.USER)
                assert False, "XFAIL"
        except AssertionError:
            eq_(self.context._mode, runner.Context.BEHAVE)

    def test_user_mode_shall_restore_behave_mode_if_exception_is_raised(self):
        try:
            with self.context.user_mode():
                eq_(self.context._mode, runner.Context.USER)
                raise RuntimeError("XFAIL")
        except Exception:
            eq_(self.context._mode, runner.Context.BEHAVE)

    def test_context_contains(self):
        eq_('thing' in self.context, False)
        self.context.thing = 'stuff'
        eq_('thing' in self.context, True)
        self.context._push()
        eq_('thing' in self.context, True)

    def test_attribute_set_at_upper_level_visible_at_lower_level(self):
        self.context.thing = 'stuff'
        self.context._push()
        eq_(self.context.thing, 'stuff')

    def test_attribute_set_at_lower_level_not_visible_at_upper_level(self):
        self.context._push()
        self.context.thing = 'stuff'
        self.context._pop()
        assert getattr(self.context, 'thing', None) is None

    def test_attributes_set_at_upper_level_visible_at_lower_level(self):
        self.context.thing = 'stuff'
        self.context._push()
        eq_(self.context.thing, 'stuff')
        self.context.other_thing = 'more stuff'
        self.context._push()
        eq_(self.context.thing, 'stuff')
        eq_(self.context.other_thing, 'more stuff')
        self.context.third_thing = 'wombats'
        self.context._push()
        eq_(self.context.thing, 'stuff')
        eq_(self.context.other_thing, 'more stuff')
        eq_(self.context.third_thing, 'wombats')

    def test_attributes_set_at_lower_level_not_visible_at_upper_level(self):
        self.context.thing = 'stuff'

        self.context._push()
        self.context.other_thing = 'more stuff'

        self.context._push()
        self.context.third_thing = 'wombats'
        eq_(self.context.thing, 'stuff')
        eq_(self.context.other_thing, 'more stuff')
        eq_(self.context.third_thing, 'wombats')

        self.context._pop()
        eq_(self.context.thing, 'stuff')
        eq_(self.context.other_thing, 'more stuff')
        assert getattr(self.context, 'third_thing', None) is None, '%s is not None' % self.context.third_thing

        self.context._pop()
        eq_(self.context.thing, 'stuff')
        assert getattr(self.context, 'other_thing', None) is None, '%s is not None' % self.context.other_thing
        assert getattr(self.context, 'third_thing', None) is None, '%s is not None' % self.context.third_thing

    def test_masking_existing_user_attribute_when_verbose_causes_warning(self):
        warns = []

        def catch_warning(*args, **kwargs):
            warns.append(args[0])

        old_showwarning = warnings.showwarning
        warnings.showwarning = catch_warning

        self.config.verbose = True
        with self.context.user_mode():
            self.context.thing = 'stuff'
            self.context._push()
            self.context.thing = 'other stuff'

        warnings.showwarning = old_showwarning

        print repr(warns)
        assert warns, 'warns is empty!'
        warning = warns[0]
        assert isinstance(warning, runner.ContextMaskWarning), 'warning is not a ContextMaskWarning'
        info = warning.args[0]
        assert info.startswith('user code'), "%r doesn't start with 'user code'" % info
        assert "'thing'" in info, '%r not in %r' % ("'thing'", info)
        assert 'tutorial' in info, '"tutorial" not in %r' % (info, )

    def test_masking_existing_user_attribute_when_not_verbose_causes_no_warning(self):
        warns = []

        def catch_warning(*args, **kwargs):
            warns.append(args[0])

        old_showwarning = warnings.showwarning
        warnings.showwarning = catch_warning

        # explicit
        self.config.verbose = False
        with self.context.user_mode():
            self.context.thing = 'stuff'
            self.context._push()
            self.context.thing = 'other stuff'

        warnings.showwarning = old_showwarning

        assert not warns

    def test_behave_masking_user_attribute_causes_warning(self):
        warns = []

        def catch_warning(*args, **kwargs):
            warns.append(args[0])

        old_showwarning = warnings.showwarning
        warnings.showwarning = catch_warning

        with self.context.user_mode():
            self.context.thing = 'stuff'
        self.context._push()
        self.context.thing = 'other stuff'

        warnings.showwarning = old_showwarning

        print repr(warns)
        assert warns, 'warns is empty!'
        warning = warns[0]
        assert isinstance(warning, runner.ContextMaskWarning), 'warning is not a ContextMaskWarning'
        info = warning.args[0]
        assert info.startswith('behave runner'), "%r doesn't start with 'behave runner'" % info
        assert "'thing'" in info, '%r not in %r' % ("'thing'", info)
        file = __file__.rsplit('.', 1)[0]
        assert file in info, '%r not in %r' % (file, info)

    def test_setting_root_attribute_that_masks_existing_causes_warning(self):
        warns = []

        def catch_warning(*args, **kwargs):
            warns.append(args[0])

        old_showwarning = warnings.showwarning
        warnings.showwarning = catch_warning

        with self.context.user_mode():
            self.context._push()
            self.context.thing = 'teak'
        self.context._set_root_attribute('thing', 'oak')

        warnings.showwarning = old_showwarning

        print repr(warns)
        assert warns
        warning = warns[0]
        assert isinstance(warning, runner.ContextMaskWarning)
        info = warning.args[0]
        assert info.startswith('behave runner'), "%r doesn't start with 'behave runner'" % info
        assert "'thing'" in info, '%r not in %r' % ("'thing'", info)
        file = __file__.rsplit('.', 1)[0]
        assert file in info, '%r not in %r' % (file, info)

    def test_context_deletable(self):
        eq_('thing' in self.context, False)
        self.context.thing = 'stuff'
        eq_('thing' in self.context, True)
        del self.context.thing
        eq_('thing' in self.context, False)

    @raises(AttributeError)
    def test_context_deletable_raises(self):
        eq_('thing' in self.context, False)
        self.context.thing = 'stuff'
        eq_('thing' in self.context, True)
        self.context._push()
        eq_('thing' in self.context, True)
        del self.context.thing

class ExampleSteps(object):
    text  = None
    table = None

    @staticmethod
    def step_passes(context):
        pass

    @staticmethod
    def step_fails(context):
        assert False, "XFAIL"

    @classmethod
    def step_with_text(cls, context):
        assert context.text is not None, "REQUIRE: multi-line text"
        cls.text = context.text

    @classmethod
    def step_with_table(cls, context):
        assert context.table, "REQUIRE: table"
        cls.table = context.table

    @classmethod
    def register_steps_with(cls, step_registry):
        STEP_DEFINITIONS = [
            ("step", "a step passes", cls.step_passes),
            ("step", "a step fails",  cls.step_fails),
            ("step", "a step with text",    cls.step_with_text),
            ("step", "a step with a table",  cls.step_with_table),
        ]
        for keyword, string, func in STEP_DEFINITIONS:
            step_registry.add_step_definition(keyword, string, func)

class TestContext_ExecuteSteps(unittest.TestCase):
    """
    Test the behave.runner.Context.execute_steps() functionality.
    """
    step_registry = None

    def setUp(self):
        runner_ = Mock()
        self.config = runner_.config = Mock()
        runner_.config.verbose = False
        runner_.config.stdout_capture  = False
        runner_.config.stderr_capture  = False
        runner_.config.log_capture  = False
        self.context = runner.Context(runner_)
        # self.context.text = None
        # self.context.table = None
        runner_.context = self.context
        self.context.feature = Mock()
        self.context.feature.parser = parser.Parser()
        if not self.step_registry:
            # -- SETUP ONCE:
            self.step_registry = step_registry.StepRegistry()
            ExampleSteps.register_steps_with(self.step_registry)
        ExampleSteps.text  = None
        ExampleSteps.table = None

    def test_execute_steps_with_simple_steps(self):
        doc = u'''
Given a step passes
Then a step passes
'''.lstrip()
        with patch('behave.step_registry.registry', self.step_registry):
            result = self.context.execute_steps(doc)
            eq_(result, True)

    def test_execute_steps_with_failing_step(self):
        doc = u'''
Given a step passes
When a step fails
Then a step passes
'''.lstrip()
        with patch('behave.step_registry.registry', self.step_registry):
            try:
                result = self.context.execute_steps(doc)
            except AssertionError, e:  # -- PY26-CLEANUP-MARK
                ok_("FAILED SUB-STEP: When a step fails" in str(e))

    def test_execute_steps_with_undefined_step(self):
        doc = u'''
Given a step passes
When a step is undefined
Then a step passes
'''.lstrip()
        with patch('behave.step_registry.registry', self.step_registry):
            try:
                result = self.context.execute_steps(doc)
            except AssertionError, e:  # -- PY26-CLEANUP-MARK
                ok_("UNDEFINED SUB-STEP: When a step is undefined" in str(e))

    def test_execute_steps_with_text(self):
        doc = u'''
Given a step passes
When a step with text:
    """
    Lorem ipsum
    Ipsum lorem
    """
Then a step passes
'''.lstrip()
        with patch('behave.step_registry.registry', self.step_registry):
            result = self.context.execute_steps(doc)
            expected_text = "Lorem ipsum\nIpsum lorem"
            eq_(result, True)
            eq_(expected_text, ExampleSteps.text)

    def test_execute_steps_with_table(self):
        doc = u'''
Given a step with a table:
    | Name  | Age |
    | Alice |  12 |
    | Bob   |  23 |
Then a step passes
'''.lstrip()
        with patch('behave.step_registry.registry', self.step_registry):
            result = self.context.execute_steps(doc)
            expected_table = model.Table([u"Name", u"Age"], 0, [
                    [u"Alice", u"12"],
                    [u"Bob",   u"23"],
            ])
            eq_(result, True)
            eq_(expected_table, ExampleSteps.table)

    def test_context_table_is_restored_after_execute_steps_without_table(self):
        doc = u'''
Given a step passes
Then a step passes
'''.lstrip()
        with patch('behave.step_registry.registry', self.step_registry):
            original_table = "<ORIGINAL_TABLE>"
            self.context.table = original_table
            self.context.execute_steps(doc)
            eq_(self.context.table, original_table)

    def test_context_table_is_restored_after_execute_steps_with_table(self):
        doc = u'''
Given a step with a table:
    | Name  | Age |
    | Alice |  12 |
    | Bob   |  23 |
Then a step passes
'''.lstrip()
        with patch('behave.step_registry.registry', self.step_registry):
            original_table = "<ORIGINAL_TABLE>"
            self.context.table = original_table
            self.context.execute_steps(doc)
            eq_(self.context.table, original_table)

    def test_context_text_is_restored_after_execute_steps_without_text(self):
        doc = u'''
Given a step passes
Then a step passes
'''.lstrip()
        with patch('behave.step_registry.registry', self.step_registry):
            original_text = "<ORIGINAL_TEXT>"
            self.context.text = original_text
            self.context.execute_steps(doc)
            eq_(self.context.text, original_text)

    def test_context_text_is_restored_after_execute_steps_with_text(self):
        doc = u'''
Given a step passes
When a step with text:
    """
    Lorem ipsum
    Ipsum lorem
    """
'''.lstrip()
        with patch('behave.step_registry.registry', self.step_registry):
            original_text = "<ORIGINAL_TEXT>"
            self.context.text = original_text
            self.context.execute_steps(doc)
            eq_(self.context.text, original_text)


    @raises(ValueError)
    def test_execute_steps_should_fail_when_called_without_feature(self):
        doc = u'''
Given a passes
Then a step passes
'''.lstrip()
        with patch('behave.step_registry.registry', self.step_registry):
            self.context.feature = None
            self.context.execute_steps(doc)


class TestRunner(object):
    def test_load_hooks_execfiles_hook_file(self):
        with patch('behave.runner.exec_file') as ef:
            with patch('os.path.exists') as exists:
                exists.return_value = True
                base_dir = 'fake/path'
                hooks_path = os.path.join(base_dir, 'environment.py')

                r = runner.Runner(None)
                r.base_dir = base_dir
                r.load_hooks()

                exists.assert_called_with(hooks_path)
                ef.assert_called_with(hooks_path, r.hooks)

    def test_run_hook_runs_a_hook_that_exists(self):
        r = runner.Runner(None)
        r.config = Mock()
        r.config.dry_run = False
        r.hooks['before_lunch'] = hook = Mock()
        args = (runner.Context(Mock()), Mock(), Mock())
        r.run_hook('before_lunch', *args)

        hook.assert_called_with(*args)

    def test_run_hook_does_not_runs_a_hook_that_exists_if_dry_run(self):
        r = runner.Runner(None)
        r.config = Mock()
        r.config.dry_run = True
        r.hooks['before_lunch'] = hook = Mock()
        args = (runner.Context(Mock()), Mock(), Mock())
        r.run_hook('before_lunch', *args)

        assert len(hook.call_args_list) == 0

    def test_setup_capture_creates_stringio_for_stdout(self):
        r = runner.Runner(Mock())
        r.config.stdout_capture = True
        r.config.log_capture = False
        r.context = Mock()

        r.setup_capture()

        assert r.stdout_capture is not None
        assert isinstance(r.stdout_capture, StringIO.StringIO)

    def test_setup_capture_does_not_create_stringio_if_not_wanted(self):
        r = runner.Runner(Mock())
        r.config.stdout_capture = False
        r.config.stderr_capture = False
        r.config.log_capture = False

        r.setup_capture()

        assert r.stdout_capture is None

    @patch('behave.runner.LoggingCapture')
    def test_setup_capture_creates_memory_handler_for_logging(self, handler):
        r = runner.Runner(Mock())
        r.config.stdout_capture = False
        r.config.log_capture = True
        r.context = Mock()

        r.setup_capture()

        assert r.log_capture is not None
        handler.assert_called_with(r.config)
        r.log_capture.inveigle.assert_called_with()

    def test_setup_capture_does_not_create_memory_handler_if_not_wanted(self):
        r = runner.Runner(Mock())
        r.config.stdout_capture = False
        r.config.stderr_capture = False
        r.config.log_capture = False

        r.setup_capture()

        assert r.log_capture is None

    def test_start_stop_capture_switcheroos_sys_stdout(self):
        old_stdout = sys.stdout
        sys.stdout = new_stdout = Mock()

        r = runner.Runner(Mock())
        r.config.stdout_capture = True
        r.config.log_capture = False
        r.context = Mock()

        r.setup_capture()
        r.start_capture()

        eq_(sys.stdout, r.stdout_capture)

        r.stop_capture()

        eq_(sys.stdout, new_stdout)

        sys.stdout = old_stdout

    def test_start_stop_capture_leaves_sys_stdout_alone_if_off(self):
        r = runner.Runner(Mock())
        r.config.stdout_capture = False
        r.config.log_capture = False

        old_stdout = sys.stdout

        r.start_capture()

        eq_(sys.stdout, old_stdout)

        r.stop_capture()

        eq_(sys.stdout, old_stdout)

    def test_teardown_capture_removes_log_tap(self):
        r = runner.Runner(Mock())
        r.config.stdout_capture = False
        r.config.log_capture = True

        r.log_capture = Mock()

        r.teardown_capture()

        r.log_capture.abandon.assert_called_with()

    def test_exec_file(self):
        fn = tempfile.mktemp()
        with open(fn, 'w') as f:
            f.write('spam = __file__\n')
        g = {}
        l = {}
        runner.exec_file(fn, g, l)
        assert '__file__' in l
        assert 'spam' in l, '"spam" variable not set in locals (%r)' % (g, l)
        eq_(l['spam'], fn)

    def test_run_returns_true_if_everything_passed(self):
        r = runner.Runner(Mock())
        r.setup_capture = Mock()
        r.setup_paths = Mock()
        r.run_with_paths = Mock()
        r.run_with_paths.return_value = True
        assert r.run()

    def test_run_returns_false_if_anything_failed(self):
        r = runner.Runner(Mock())
        r.setup_capture = Mock()
        r.setup_paths = Mock()
        r.run_with_paths = Mock()
        r.run_with_paths.return_value = False
        assert not r.run()


class TestRunWithPaths(object):
    def setUp(self):
        self.config = Mock()
        self.config.reporters = []
        self.config.logging_level = None
        self.config.logging_filter = None
        self.config.outputs = [ Mock(), StreamOpener(stream=sys.stdout) ]
        self.config.format = [ "plain", "progress" ]
        self.runner = runner.Runner(self.config)
        self.load_hooks = self.runner.load_hooks = Mock()
        self.load_step_definitions = self.runner.load_step_definitions = Mock()
        self.run_hook = self.runner.run_hook = Mock()
        self.run_step = self.runner.run_step = Mock()
        self.feature_locations = self.runner.feature_locations = Mock()
        self.calculate_summaries = self.runner.calculate_summaries = Mock()

        self.formatter_class = patch('behave.formatter.pretty.PrettyFormatter')
        formatter_class = self.formatter_class.start()
        formatter_class.return_value = self.formatter = Mock()

    def tearDown(self):
        self.formatter_class.stop()

    def test_loads_hooks_and_step_definitions(self):
        self.feature_locations.return_value = []
        self.runner.run_with_paths()

        assert self.load_hooks.called
        assert self.load_step_definitions.called

    def test_runs_before_all_and_after_all_hooks(self):
        # Make runner.feature_locations() and runner.run_hook() the same mock so
        # we can make sure things happen in the right order.
        self.runner.feature_locations = self.run_hook
        self.runner.feature_locations.return_value = []
        self.runner.context = Mock()
        self.runner.run_with_paths()

        eq_(self.run_hook.call_args_list, [
            (('before_all', self.runner.context), {}),
            ((), {}),
            (('after_all', self.runner.context), {}),
        ])

    @patch('behave.parser.parse_file')
    @patch('os.path.abspath')
    def test_parses_feature_files_and_appends_to_feature_list(self, abspath,
                                                              parse_file):
        feature_locations = ['one', 'two', 'three']
        feature = Mock()
        feature.tags = []
        feature.__iter__ = Mock(return_value=iter([]))
        feature.run.return_value = False
        self.runner.feature_locations.return_value = feature_locations
        abspath.side_effect = lambda x: x.upper()
        self.config.lang = 'fritz'
        self.config.format = ['plain']
        self.config.outputs = [ StreamOpener(stream=sys.stdout) ]
        self.config.output.encoding = None
        self.config.exclude = lambda s: False
        self.config.junit = False
        self.config.summary = False
        parse_file.return_value = feature

        self.runner.run_with_paths()

        expected_parse_file_args = \
            [((x.upper(),), {'language': 'fritz'}) for x in feature_locations]
        eq_(parse_file.call_args_list, expected_parse_file_args)
        eq_(self.runner.features, [feature] * 3)


class FsMock(object):
    def __init__(self, *paths):
        self.base = os.path.abspath('.')
        self.sep  = os.path.sep

        # This bit of gymnastics is to support Windows. We feed in a bunch of
        # paths in places using FsMock that assume that POSIX-style paths
        # work. This is faster than fixing all of those but at some point we
        # should totally do it properly with os.path.join() and all that.
        def full_split(path):
            bits = []

            while path:
                path, bit = os.path.split(path)
                bits.insert(0, bit)

            return bits

        paths = [os.path.join(self.base, *full_split(path)) for path in paths]
        print repr(paths)
        self.paths = paths
        self.files = set()
        self.dirs = defaultdict(list)
        separators = [sep for sep in (os.path.sep, os.path.altsep) if sep]
        for path in paths:
            if path[-1] in separators:
                self.dirs[path[:-1]] = []
                d, p = os.path.split(path[:-1])
                while d and p:
                    self.dirs[d].append(p)
                    d, p = os.path.split(d)
            else:
                self.files.add(path)
                d, f = os.path.split(path)
                self.dirs[d].append(f)
        self.calls = []

    def listdir(self, dir):
        # pylint: disable=W0622
        #   W0622   Redefining built-in dir
        self.calls.append(('listdir', dir))
        return self.dirs.get(dir, [])

    def isfile(self, path):
        self.calls.append(('isfile', path))
        return path in self.files

    def isdir(self, path):
        self.calls.append(('isdir', path))
        return path in self.dirs

    def exists(self, path):
        self.calls.append(('exists', path))
        return path in self.dirs or path in self.files

    def walk(self, path, l=None):
        if l is None:
            assert path in self.dirs, '%s not in %s' % (path, self.dirs)
            l = []
        dirnames = []
        filenames = []
        for e in self.dirs[path]:
            if os.path.join(path, e) in self.dirs:
                dirnames.append(e)
                self.walk(os.path.join(path, e), l)
            else:
                filenames.append(e)
        l.append((path, dirnames, filenames))
        return l

    # utilities that we need
    def dirname(self, path, orig=os.path.dirname):
        return orig(path)

    def abspath(self, path, orig=os.path.abspath):
        return orig(path)

    def join(self, a, b, orig=os.path.join):
        return orig(a, b)

    def split(self, path, orig=os.path.split):
        return orig(path)

    def splitdrive(self, path, orig=os.path.splitdrive):
        return orig(path)


class TestFeatureDirectory(object):
    def test_default_path_no_steps(self):
        config = Mock()
        config.paths = []
        config.verbose = True
        r = runner.Runner(config)

        fs = FsMock()

        # will look for a "features" directory and not find one
        with patch('os.path', fs):
            assert_raises(ConfigError, r.setup_paths)

        ok_(('isdir', os.path.join(fs.base, 'features', 'steps')) in fs.calls)

    def test_default_path_no_features(self):
        config = Mock()
        config.paths = []
        config.verbose = True
        r = runner.Runner(config)

        fs = FsMock('features/steps/')
        with patch('os.path', fs):
            with patch('os.walk', fs.walk):
                assert_raises(ConfigError, r.setup_paths)

    def test_default_path(self):
        config = Mock()
        config.paths = []
        config.verbose = True
        r = runner.Runner(config)

        fs = FsMock('features/steps/', 'features/foo.feature')

        with patch('os.path', fs):
            with patch('os.walk', fs.walk):
                with r.path_manager:
                    r.setup_paths()

        eq_(r.base_dir, os.path.abspath('features'))

    def test_supplied_feature_file(self):
        config = Mock()
        config.paths = ['foo.feature']
        config.verbose = True
        r = runner.Runner(config)
        r.context = Mock()

        fs = FsMock('steps/', 'foo.feature')

        with patch('os.path', fs):
            with patch('os.walk', fs.walk):
                with r.path_manager:
                    r.setup_paths()
        ok_(('isdir', os.path.join(fs.base, 'steps')) in fs.calls)
        ok_(('isfile', os.path.join(fs.base, 'foo.feature')) in fs.calls)

        eq_(r.base_dir, fs.base)

    def test_supplied_feature_file_no_steps(self):
        config = Mock()
        config.paths = ['foo.feature']
        config.verbose = True
        r = runner.Runner(config)

        fs = FsMock('foo.feature')

        with patch('os.path', fs):
            with patch('os.walk', fs.walk):
                with r.path_manager:
                    assert_raises(ConfigError, r.setup_paths)

    def test_supplied_feature_directory(self):
        config = Mock()
        config.paths = ['spam']
        config.verbose = True
        r = runner.Runner(config)

        fs = FsMock('spam/', 'spam/steps/', 'spam/foo.feature')

        with patch('os.path', fs):
            with patch('os.walk', fs.walk):
                with r.path_manager:
                    r.setup_paths()

        ok_(('isdir', os.path.join(fs.base, 'spam', 'steps')) in fs.calls)

        eq_(r.base_dir, os.path.join(fs.base, 'spam'))

    def test_supplied_feature_directory_no_steps(self):
        config = Mock()
        config.paths = ['spam']
        config.verbose = True
        r = runner.Runner(config)

        fs = FsMock('spam/', 'spam/foo.feature')

        with patch('os.path', fs):
            with patch('os.walk', fs.walk):
                assert_raises(ConfigError, r.setup_paths)

        ok_(('isdir', os.path.join(fs.base, 'spam', 'steps')) in fs.calls)

    def test_supplied_feature_directory_missing(self):
        config = Mock()
        config.paths = ['spam']
        config.verbose = True
        r = runner.Runner(config)

        fs = FsMock()

        with patch('os.path', fs):
            with patch('os.walk', fs.walk):
                assert_raises(ConfigError, r.setup_paths)


class TestFeatureDirectoryLayout2(object):
    def test_default_path(self):
        config = Mock()
        config.paths = []
        config.verbose = True
        r = runner.Runner(config)

        fs = FsMock(
            'features/',
            'features/steps/',
            'features/group1/',
            'features/group1/foo.feature',
        )

        with patch('os.path', fs):
            with patch('os.walk', fs.walk):
                with r.path_manager:
                    r.setup_paths()

        eq_(r.base_dir, os.path.abspath('features'))

    def test_supplied_root_directory(self):
        config = Mock()
        config.paths = [ 'features' ]
        config.verbose = True
        r = runner.Runner(config)

        fs = FsMock(
            'features/',
            'features/group1/',
            'features/group1/foo.feature',
            'features/steps/',
        )

        with patch('os.path', fs):
            with patch('os.walk', fs.walk):
                with r.path_manager:
                    r.setup_paths()

        ok_(('isdir',  os.path.join(fs.base, 'features', 'steps')) in fs.calls)
        eq_(r.base_dir, os.path.join(fs.base, 'features'))

    def test_supplied_root_directory_no_steps(self):
        config = Mock()
        config.paths = [ 'features' ]
        config.verbose = True
        r = runner.Runner(config)

        fs = FsMock(
            'features/',
            'features/group1/',
            'features/group1/foo.feature',
        )

        with patch('os.path', fs):
            with patch('os.walk', fs.walk):
                with r.path_manager:
                    assert_raises(ConfigError, r.setup_paths)

        ok_(('isdir',  os.path.join(fs.base, 'features', 'steps')) in fs.calls)
        eq_(r.base_dir, None)


    def test_supplied_feature_file(self):
        config = Mock()
        config.paths = [ 'features/group1/foo.feature' ]
        config.verbose = True
        r = runner.Runner(config)
        r.context = Mock()

        fs = FsMock(
            'features/',
            'features/group1/',
            'features/group1/foo.feature',
            'features/steps/',
        )

        with patch('os.path', fs):
            with patch('os.walk', fs.walk):
                with r.path_manager:
                    r.setup_paths()

        ok_(('isdir',  os.path.join(fs.base, 'features', 'steps'))  in fs.calls)
        ok_(('isfile', os.path.join(fs.base, 'features', 'group1', 'foo.feature')) in fs.calls)
        eq_(r.base_dir, fs.join(fs.base, "features"))

    def test_supplied_feature_file_no_steps(self):
        config = Mock()
        config.paths = [ 'features/group1/foo.feature' ]
        config.verbose = True
        r = runner.Runner(config)

        fs = FsMock(
            'features/',
            'features/group1/',
            'features/group1/foo.feature',
        )

        with patch('os.path', fs):
            with patch('os.walk', fs.walk):
                with r.path_manager:
                    assert_raises(ConfigError, r.setup_paths)

    def test_supplied_feature_directory(self):
        config = Mock()
        config.paths = [ 'features/group1' ]
        config.verbose = True
        r = runner.Runner(config)

        fs = FsMock(
            'features/',
            'features/group1/',
            'features/group1/foo.feature',
            'features/steps/',
        )

        with patch('os.path', fs):
            with patch('os.walk', fs.walk):
                with r.path_manager:
                    r.setup_paths()

        ok_(('isdir',  os.path.join(fs.base, 'features', 'steps')) in fs.calls)
        eq_(r.base_dir, os.path.join(fs.base, 'features'))


    def test_supplied_feature_directory_no_steps(self):
        config = Mock()
        config.paths = [ 'features/group1' ]
        config.verbose = True
        r = runner.Runner(config)

        fs = FsMock(
            'features/',
            'features/group1/',
            'features/group1/foo.feature',
        )

        with patch('os.path', fs):
            with patch('os.walk', fs.walk):
                assert_raises(ConfigError, r.setup_paths)

        ok_(('isdir',  os.path.join(fs.base, 'features', 'steps')) in fs.calls)

