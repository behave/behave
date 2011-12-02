from __future__ import with_statement

from collections import defaultdict
import os.path
import sys
import warnings

from mock import Mock, patch
from nose.tools import *

from behave import model, runner
from behave.configuration import ConfigError

class TestContext(object):
    def setUp(self):
        self.config = Mock()
        self.config.verbose = False
        self.context = runner.Context(self.config)

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
        assert getattr(self.context, 'third_thing', None) is None
        self.context._pop()
        eq_(self.context.thing, 'stuff')
        assert getattr(self.context, 'other_thing', None) is None
        assert getattr(self.context, 'third_thing', None) is None

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
        assert warns
        warning = warns[0]
        assert isinstance(warning, runner.ContextMaskWarning)
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
        assert warns
        warning = warns[0]
        assert isinstance(warning, runner.ContextMaskWarning)
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

class TestStepRegistry(object):
    def test_add_definition_adds_to_lowercased_keyword(self):
        registry = runner.StepRegistry()
        with patch('behave.matchers.get_matcher') as get_matcher:
            func = lambda x: -x
            string = 'just a test string'
            magic_object = object()
            get_matcher.return_value = magic_object

            for step_type in registry.steps.keys():
                mock = Mock()
                registry.steps[step_type] = mock

                registry.add_definition(step_type.upper(), string, func)

                get_matcher.assert_called_with(func, string)
                mock.append.assert_called_with(magic_object)

    def test_find_match_with_specific_step_type_also_searches_generic(self):
        registry = runner.StepRegistry()

        given_mock = Mock()
        given_mock.match.return_value = None
        step_mock = Mock()
        step_mock.match.return_value = None

        registry.steps['given'].append(given_mock)
        registry.steps['step'].append(step_mock)

        step = Mock()
        step.step_type = 'given'
        step.name = 'just a test step'

        assert registry.find_match(step) is None

        given_mock.match.assert_called_with(step.name)
        step_mock.match.assert_called_with(step.name)

    def test_find_match_with_no_match_returns_none(self):
        registry = runner.StepRegistry()

        step_defs = [Mock() for x in range(0, 10)]
        for mock in step_defs:
            mock.match.return_value = None

        registry.steps['when'] = step_defs

        step = Mock()
        step.step_type = 'when'
        step.name = 'just a test step'

        assert registry.find_match(step) is None

    def test_find_match_with_a_match_returns_match(self):
        registry = runner.StepRegistry()

        step_defs = [Mock() for x in range(0, 10)]
        for mock in step_defs:
            mock.match.return_value = None
        magic_object = object()
        step_defs[5].match.return_value = magic_object

        registry.steps['then'] = step_defs

        step = Mock()
        step.step_type = 'then'
        step.name = 'just a test step'

        assert registry.find_match(step) is magic_object
        for mock in step_defs[6:]:
            eq_(mock.match.call_count, 0)


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

    def test_make_step_decorator_ends_up_adding_a_step_definition(self):
        r = runner.Runner(None)
        with patch.object(r.steps, 'add_definition') as add_definition:
            step_type = object()
            string = object()
            func = object()

            decorator = r.make_step_decorator(step_type)
            wrapper = decorator(string)
            assert wrapper(func) is func
            add_definition.assert_called_with(step_type, string, func)

    def test_run_hook_runs_a_hook_that_exists(self):
        r = runner.Runner(None)
        r.hooks['before_lunch'] = hook = Mock()
        args = (runner.Context(Mock()), Mock(), Mock())
        r.run_hook('before_lunch', *args)

        hook.assert_called_with(*args)


class TestRunWithPaths(object):
    def setUp(self):
        self.config = Mock()
        self.runner = runner.Runner(self.config)
        self.load_hooks = self.runner.load_hooks = Mock()
        self.load_step_definitions = self.runner.load_step_definitions = Mock()
        self.run_hook = self.runner.run_hook = Mock()
        self.run_step = self.runner.run_step = Mock()
        self.feature_files = self.runner.feature_files = Mock()
        self.calculate_summaries = self.runner.calculate_summaries = Mock()

        self.parse_file_patch = patch('behave.runner.parser.parse_file')
        self.parse_file = self.parse_file_patch.start()
        self.abspath_patch = patch('os.path.abspath')
        self.abspath = self.abspath_patch.start()
        self.context_class = patch('behave.runner.Context')
        context_class = self.context_class.start()
        context_class.return_value = self.context = Mock()
        self.formatter_class = patch('behave.runner.PrettyFormatter')
        formatter_class = self.formatter_class.start()
        formatter_class.return_value = self.formatter = Mock()

    def tearDown(self):
        self.parse_file_patch.stop()
        self.abspath_patch.stop()
        self.context_class.stop()
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
        self.runner.run_with_paths()

        eq_(self.run_hook.call_args_list, [
            (('before_all', self.runner.context), {}),
            ((), {}),
            (('after_all', self.runner.context), {}),
        ])

    def test_parses_feature_files_and_appends_to_feature_list(self):
        feature_files = ['one', 'two', 'three']
        feature = Mock()
        feature.tags = []
        feature.__iter__ = Mock(return_value=iter([]))
        self.runner.feature_files.return_value = feature_files
        self.abspath.side_effect = lambda x: x.upper()
        self.config.lang = 'fritz'
        self.parse_file.return_value = feature

        self.runner.run_with_paths()

        expected_parse_file_args = \
            [((x.upper(),), {'language': 'fritz'}) for x in feature_files]
        eq_(self.parse_file.call_args_list, expected_parse_file_args)
        eq_(self.runner.features, [feature] * 3)

    def test_formatter_sequence_with_no_scenarios_or_background(self):
        feature_files = ['one']
        feature = Mock()
        feature.tags = []
        feature.background = None
        feature.__iter__ = Mock(return_value=iter([]))
        self.runner.feature_files.return_value = feature_files
        self.parse_file.return_value = feature

        self.runner.run_with_paths()

        self.formatter.uri.assert_called_with('one')
        self.formatter.feature.assert_called_with(feature)
        assert not self.formatter.background.called
        self.formatter.eof.assert_called_with()

    def test_formatter_background_called_when_feature_has_background(self):
        feature_files = ['one']
        feature = Mock()
        feature.tags = []
        feature.background = Mock()
        feature.__iter__ = Mock(return_value=iter([]))
        self.runner.feature_files.return_value = feature_files
        self.parse_file.return_value = feature

        self.runner.run_with_paths()

        self.formatter.uri.assert_called_with('one')
        self.formatter.feature.assert_called_with(feature)
        self.formatter.background.assert_called_with(feature.background)
        self.formatter.eof.assert_called_with()

    def test_invokes_formatter_and_runs_scenarios(self):
        self.config.stdout_capture = False
        self.config.log_capture = False
        feature_files = ['one']
        feature = Mock()
        feature.tags = []
        feature.background = None
        scenario1 = Mock()
        scenario1.tags = []
        steps1 = [Mock(), Mock()]
        scenario1.__iter__ = Mock(return_value=iter(steps1))
        scenario1.run.return_value = False
        scenario2 = Mock()
        scenario2.tags = []
        steps2 = [Mock(), Mock(), Mock()]
        scenario2.__iter__ = Mock(return_value=iter(steps2))
        scenario2.run.return_value = False
        scenarios = [scenario1, scenario2]
        feature.__iter__ = Mock(return_value=iter(scenarios))
        self.runner.feature_files.return_value = feature_files
        self.parse_file.return_value = feature

        self.runner.run_with_paths()

        self.formatter.uri.assert_called_with('one')
        self.formatter.feature.assert_called_with(feature)
        scenario1.run.assert_called_with(self.runner)
        scenario2.run.assert_called_with(self.runner)
        self.formatter.eof.assert_called_with()

    def test_feature_hooks_not_run_if_feature_not_being_run(self):
        self.config.stdout_capture = False
        self.config.log_capture = False
        self.config.tags.check.return_value = False

        feature_files = ['one']
        feature = Mock()
        feature.tags = ['feature_tag_one', 'feature_tag_two']
        feature.background = None
        feature.__iter__ = Mock(return_value=iter([]))

        self.runner.feature_files.return_value = feature_files
        self.parse_file.return_value = feature

        self.runner.run_with_paths()

        eq_(self.run_hook.call_args_list, [
            (('before_all', self.runner.context), {}),
            (('after_all', self.runner.context), {}),
        ])

    def test_scenario_hooks_not_run_if_scenario_not_being_run(self):
        self.config.stdout_capture = False
        self.config.log_capture = False

        def tags1(*args, **kwargs):
            def tags2(*args, **kwargs):
                return False
            self.config.tags.check.side_effect = tags2
            return True
        self.config.tags.check.side_effect = tags1

        feature_files = ['one']
        feature = Mock()
        feature.tags = ['feature_tag_one']
        feature.background = None
        scenario = Mock()
        scenario.tags = ['scenario_tag_one']
        steps = [Mock(), Mock()]
        scenario.__iter__ = Mock(return_value=iter(steps))
        feature.__iter__ = Mock(return_value=iter([scenario]))

        self.runner.feature_files.return_value = feature_files
        self.parse_file.return_value = feature

        self.runner.run_with_paths()

        eq_(self.run_hook.call_args_list, [
            (('before_all', self.runner.context), {}),
            (('before_tag', self.runner.context, 'feature_tag_one'), {}),
            (('before_feature', self.runner.context, feature), {}),
            (('after_feature', self.runner.context, feature), {}),
            (('after_tag', self.runner.context, 'feature_tag_one'), {}),
            (('after_all', self.runner.context), {}),
        ])


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


