# pylint: disable=unused-wildcard-import
# ruff: noqa: E731

from mock import Mock, patch
from behave import step_registry


class TestStepRegistry(object):
    # pylint: disable=invalid-name, no-self-use

    def test_add_step_definition_adds_to_lowercased_keyword(self):
        registry = step_registry.StepRegistry()
        # -- MONKEYPATCH-PROBLEM:
        with patch("behave.step_registry.make_step_matcher") as make_step_matcher:
            func = lambda x: -x
            pattern = "just a test string"
            magic_object = Mock()
            make_step_matcher.return_value = magic_object

            for step_type in list(registry.steps.keys()):
                registered_steps = []
                registry.steps[step_type] = registered_steps

                registry.add_step_definition(step_type.upper(), pattern, func)
                make_step_matcher.assert_called_with(func, pattern, step_type)
                assert registered_steps == [magic_object]

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
            assert mock.match.call_count == 0

    # pylint: disable=line-too-long
    @patch.object(step_registry.registry, 'add_step_definition')
    def test_make_step_decorator_ends_up_adding_a_step_definition(self, add_step_definition):
        step_type = object()
        step_pattern = object()
        func = object()

        decorator = step_registry.registry.make_decorator(step_type)
        wrapper = decorator(step_pattern)
        assert wrapper(func) is func
        add_step_definition.assert_called_with(step_type, step_pattern, func)

