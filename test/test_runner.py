from __future__ import with_statement

from collections import defaultdict
import os.path
import StringIO
import sys
import warnings
import tempfile

from mock import Mock, patch
from nose.tools import *

from behave import model, runner, step_registry
from behave.configuration import ConfigError
from behave.log_capture import MemoryHandler

class TestContext(object):
    def setUp(self):
        r = Mock()
        self.config = r.config = Mock()
        r.config.verbose = False
        self.context = runner.Context(r)

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
    def test_context_deletable(self):
        eq_('thing' in self.context, False)
        self.context.thing = 'stuff'
        eq_('thing' in self.context, True)
        self.context._push()
        eq_('thing' in self.context, True)
        del self.context.thing


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
        r.hooks['before_lunch'] = hook = Mock()
        args = (runner.Context(Mock()), Mock(), Mock())
        r.run_hook('before_lunch', *args)

        hook.assert_called_with(*args)

    def test_setup_capture_creates_stringio_for_stdout(self):
        r = runner.Runner(Mock())
        r.config.stdout_capture = True
        r.config.log_capture = False

        r.setup_capture()

        assert r.stdout_capture is not None
        assert isinstance(r.stdout_capture, StringIO.StringIO)

    def test_setup_capture_does_not_create_stringio_if_not_wanted(self):
        r = runner.Runner(Mock())
        r.config.stdout_capture = False
        r.config.log_capture = False

        r.setup_capture()

        assert r.stdout_capture is None

    @patch('behave.runner.MemoryHandler')
    def test_setup_capture_creates_memory_handler_for_logging(self, handler):
        r = runner.Runner(Mock())
        r.config.stdout_capture = False
        r.config.log_capture = True

        r.setup_capture()

        assert r.log_capture is not None
        handler.assert_called_with(r.config)
        r.log_capture.inveigle.assert_called_with()

    def test_setup_capture_does_not_create_memory_handler_if_not_wanted(self):
        r = runner.Runner(Mock())
        r.config.stdout_capture = False
        r.config.log_capture = False

        r.setup_capture()

        assert r.log_capture is None

    def test_start_stop_capture_switcheroos_sys_stdout(self):
        old_stdout = sys.stdout
        sys.stdout = new_stdout = Mock()

        r = runner.Runner(Mock())
        r.config.stdout_capture = True
        r.config.log_capture = False

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


class TestRunWithPaths(object):
    def setUp(self):
        self.config = Mock()
        self.config.reporters = []
        self.runner = runner.Runner(self.config)
        self.load_hooks = self.runner.load_hooks = Mock()
        self.load_step_definitions = self.runner.load_step_definitions = Mock()
        self.run_hook = self.runner.run_hook = Mock()
        self.run_step = self.runner.run_step = Mock()
        self.feature_files = self.runner.feature_files = Mock()
        self.calculate_summaries = self.runner.calculate_summaries = Mock()

        self.formatter_class = patch('behave.formatter.pretty.PrettyFormatter')
        formatter_class = self.formatter_class.start()
        formatter_class.return_value = self.formatter = Mock()

    def tearDown(self):
        self.formatter_class.stop()

    def test_loads_hooks_and_step_definitions(self):
        self.feature_files.return_value = []
        self.runner.run_with_paths()

        assert self.load_hooks.called
        assert self.load_step_definitions.called

    def test_runs_before_all_and_after_all_hooks(self):
        # Make runner.feature_files() and runner.run_hook() the same mock so
        # we can make sure things happen in the right order.
        self.runner.feature_files = self.run_hook
        self.runner.feature_files.return_value = []
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
        feature_files = ['one', 'two', 'three']
        feature = Mock()
        feature.tags = []
        feature.__iter__ = Mock(return_value=iter([]))
        feature.run.return_value = False
        self.runner.feature_files.return_value = feature_files
        abspath.side_effect = lambda x: x.upper()
        self.config.lang = 'fritz'
        self.config.format = ['plain']
        self.config.output.encoding = None
        self.config.exclude = lambda s: False
        self.config.junit = False
        self.config.summary = False
        parse_file.return_value = feature

        self.runner.run_with_paths()

        expected_parse_file_args = \
            [((x.upper(),), {'language': 'fritz'}) for x in feature_files]
        eq_(parse_file.call_args_list, expected_parse_file_args)
        eq_(self.runner.features, [feature] * 3)


class FsMock(object):
    def __init__(self, *paths):
        self.base = os.path.abspath('.')
        paths = [os.path.join(self.base, path) for path in paths]
        self.paths = paths
        self.files = set()
        self.dirs = defaultdict(list)
        for path in paths:
            if path[-1] == '/':
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

        ok_(('isdir', os.path.join(fs.base, 'features/steps')) in fs.calls)

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


