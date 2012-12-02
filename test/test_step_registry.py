from __future__ import with_statement

from mock import Mock, patch
from nose.tools import *
from behave import step_registry

class TestStepRegistry(object):
    def test_add_definition_adds_to_lowercased_keyword(self):
        registry = step_registry.StepRegistry()
        with patch('behave.matchers.get_matcher') as get_matcher:
            func = lambda x: -x
            string = 'just a test string'
            magic_object = object()
            get_matcher.return_value = magic_object

            for step_type in registry.steps.keys():
                l = []
                registry.steps[step_type] = l

                registry.add_definition(step_type.upper(), string, func)

                get_matcher.assert_called_with(func, string)
                eq_(l, [magic_object])

    def test_find_match_with_specific_step_type_also_searches_generic(self):
        registry = step_registry.StepRegistry()

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
        registry = step_registry.StepRegistry()

        step_defs = [Mock() for x in range(0, 10)]
        for mock in step_defs:
            mock.match.return_value = None

        registry.steps['when'] = step_defs

        step = Mock()
        step.step_type = 'when'
        step.name = 'just a test step'

        assert registry.find_match(step) is None

    def test_find_match_with_a_match_returns_match(self):
        registry = step_registry.StepRegistry()

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

    @patch.object(step_registry.registry, 'add_definition')
    def test_make_step_decorator_ends_up_adding_a_step_definition(self, add_definition):
        step_type = object()
        string = object()
        func = object()

        decorator = step_registry.registry.make_decorator(step_type)
        wrapper = decorator(string)
        assert wrapper(func) is func
        add_definition.assert_called_with(step_type, string, func)

