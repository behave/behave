import os.path

from mock import Mock, patch
from nose.tools import *

from behave import runner
from behave.configuration import ConfigError

class TestContext(object):
    def setUp(self):
        self.context = runner.Context()

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

class TestFeatureDirectory(object):
    def test_default_path_no_steps(self):
        config = Mock()
        config.paths = []
        config.verbose = False
        r = runner.Runner(config)

        with patch('os.path.isdir') as opd:
            opd.return_value = False
            assert_raises(ConfigError, r.setup_paths)

    def test_default_path_no_features(self):
        config = Mock()
        config.paths = []
        config.verbose = False
        r = runner.Runner(config)

        with patch('os.path.isdir') as opd:
            with patch('os.listdir') as ld:
                opd.return_value = True
                ld.return_value = ['foo']
                assert_raises(ConfigError, r.setup_paths)

    def test_default_path(self):
        config = Mock()
        config.paths = []
        config.verbose = True
        r = runner.Runner(config)

        with patch('os.path.isdir') as opd:
            with patch('os.listdir') as ld:
                opd.return_value = True
                ld.return_value = ['foo.feature']
                with r.path_manager:
                    r.setup_paths()

        eq_(r.base_dir, os.path.abspath('features'))

    def test_supplied_feature_file(self):
        config = Mock()
        config.paths = ['foo.feature']
        config.verbose = True
        r = runner.Runner(config)

        p = os.path.abspath('.')

        with patch('os.path.isdir') as opd:
            with patch('os.path.isfile') as opf:
                with patch('os.listdir') as ld:
                    opd.return_value = True
                    opf.return_value = True
                    ld.return_value = ['foo.feature']
                    with r.path_manager:
                        r.setup_paths()
                    opd.assert_called_with(os.path.join(p, 'steps'))
                    opf.assert_called_with(os.path.join(p, 'foo.feature'))

        eq_(r.base_dir, p)

    def test_supplied_feature_file_no_steps(self):
        config = Mock()
        config.paths = ['foo.feature']
        config.verbose = True
        r = runner.Runner(config)

        p = os.path.abspath('.')

        with patch('os.path.isdir') as opd:
            with patch('os.path.isfile') as opf:
                with patch('os.listdir') as ld:
                    opd.return_value = False
                    opf.return_value = True
                    ld.return_value = ['foo.feature']
                    assert_raises(ConfigError, r.setup_paths)
                    opd.assert_called_with(os.path.join(p, 'steps'))

    def test_supplied_feature_directory(self):
        config = Mock()
        config.paths = ['features']
        config.verbose = True
        r = runner.Runner(config)

        p = os.path.abspath('features')

        with patch('os.path.isdir') as opd:
            with patch('os.path.isfile') as opf:
                with patch('os.listdir') as ld:
                    opd.return_value = True
                    opf.return_value = False
                    ld.return_value = ['foo.feature']
                    with r.path_manager:
                        r.setup_paths()
                    opd.assert_called_with(os.path.join(p, 'steps'))

        eq_(r.base_dir, p)

    def test_supplied_feature_directory_no_steps(self):
        config = Mock()
        config.paths = ['features']
        config.verbose = True
        r = runner.Runner(config)

        p = os.path.abspath('features')

        with patch('os.path.isdir') as opd:
            with patch('os.path.isfile') as opf:
                with patch('os.listdir') as ld:
                    opd.return_value = False
                    opf.return_value = False
                    ld.return_value = ['foo.feature']
                    assert_raises(ConfigError, r.setup_paths)
                    opd.assert_called_with(os.path.join(p, 'steps'))

