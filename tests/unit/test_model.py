# -*- coding: utf-8 -*-
# pylint: disable=no-self-use, line-too-long

from __future__ import absolute_import, print_function, with_statement
import unittest
import pytest
from mock import Mock, patch
import six
from six.moves import range     # pylint: disable=redefined-builtin
from six.moves import zip       # pylint: disable=redefined-builtin

from behave._stepimport import use_step_import_modules
from behave.capture import CaptureController
from behave.compat.collections import OrderedDict
from behave.configuration import Configuration
from behave.matchers import NoMatch
from behave.model_type import Status
from behave.model import Examples, Feature, Scenario, ScenarioOutline, Step
from behave.model import Table, Row
from behave.parser import parse_scenario
from behave.runner import ModelRunner, Context
from behave._stepimport import SimpleStepContainer


traceback_modname = "traceback"  # pylint: disable=unused-import
if six.PY2:
    # pylint: disable=unused-import
    traceback_modname = "traceback2"


# -----------------------------------------------------------------------------
# TEST SUPPORT
# -----------------------------------------------------------------------------
def raiser(exception):
    def func(*args, **kwargs):    # pylint: disable=unused-argument
        raise exception
    return func


# -----------------------------------------------------------------------------
# TEST SUITE
# -----------------------------------------------------------------------------
class TestFeatureRun(unittest.TestCase):
    # pylint: disable=invalid-name

    def setUp(self):
        config = Mock()
        config.tag_expression.check.return_value = True
        runner = Mock()
        self.runner = runner
        self.runner.aborted = False
        self.runner.feature.tags = []
        self.config = self.runner.config = config
        context = Context(runner=runner)
        self.context = self.runner.context = context
        self.formatters = self.runner.formatters = [Mock()]
        self.run_hook = self.runner.run_hook = Mock()

    def test_formatter_feature_called(self):
        feature = Feature("foo.feature", 1, u"Feature", u"foo",
                          background=Mock())

        feature.run(self.runner)
        self.formatters[0].feature.assert_called_with(feature)

    def test_formatter_background_called_when_feature_has_background(self):
        feature = Feature("foo.feature", 1, u"Feature", u"foo",
                          background=Mock())

        feature.run(self.runner)
        self.formatters[0].background.assert_called_with(feature.background)

    def test_formatter_background_not_called_when_feature_has_no_background(self):
        feature = Feature("foo.feature", 1, u"Feature", u"foo")

        feature.run(self.runner)
        assert not self.formatters[0].background.called

    def test_run_runs_scenarios(self):
        scenarios = [Mock(), Mock()]
        for scenario in scenarios:
            scenario.tags = []
            scenario.run.return_value = False

        self.config.tag_expression.check.return_value = True  # pylint: disable=no-member
        self.config.name = []

        feature = Feature("foo.feature", 1, u"Feature", u"foo",
                          scenarios=scenarios)

        feature.run(self.runner)

        for scenario in scenarios:
            scenario.run.assert_called_once_with(self.runner)

    def test_run_runs_named_scenarios(self):
        scenarios = [Mock(Scenario), Mock(Scenario)]
        scenarios[0].name = "first scenario"
        scenarios[1].name = "second scenario"
        scenarios[0].tags = []
        scenarios[1].tags = []
        # -- FAKE-CHECK:
        scenarios[0].should_run_with_name_select.return_value = True
        scenarios[1].should_run_with_name_select.return_value = False

        for scenario in scenarios:
            scenario.run.return_value = False

        self.config.tag_expression.check.return_value = True  # pylint: disable=no-member
        self.config.name = ["first", "third"]
        self.config.name_re = Configuration.build_name_re(self.config.name)

        feature = Feature("foo.feature", 1, u"Feature", u"foo",
                          scenarios=scenarios)

        feature.run(self.runner)

        scenarios[0].run.assert_called_with(self.runner)
        assert not scenarios[1].run.called
        scenarios[0].should_run_with_name_select.assert_called_with(self.config)
        scenarios[1].should_run_with_name_select.assert_called_with(self.config)

    def test_run_runs_named_scenarios_with_regexp(self):
        scenarios = [Mock(), Mock()]
        scenarios[0].name = "first scenario"
        scenarios[1].name = "second scenario"
        scenarios[0].tags = []
        scenarios[1].tags = []
        # -- FAKE-CHECK:
        scenarios[0].should_run_with_name_select.return_value = False
        scenarios[1].should_run_with_name_select.return_value = True

        for scenario in scenarios:
            scenario.run.return_value = False

        self.config.tag_expression.check.return_value = True  # pylint: disable=no-member
        self.config.name = ["third .*", "second .*"]
        self.config.name_re = Configuration.build_name_re(self.config.name)

        feature = Feature("foo.feature", 1, u"Feature", u"foo",
                          scenarios=scenarios)

        feature.run(self.runner)

        assert not scenarios[0].run.called
        scenarios[1].run.assert_called_with(self.runner)
        scenarios[0].should_run_with_name_select.assert_called_with(self.config)
        scenarios[1].should_run_with_name_select.assert_called_with(self.config)

    # @prepared
    def test_run_exclude_named_scenarios_with_regexp(self):
        # -- NOTE: Works here only because it is run against Mocks.
        scenarios = [Mock(), Mock(), Mock()]
        scenarios[0].name = "Alice in Florida"
        scenarios[1].name = "Alice and Bob"
        scenarios[2].name = "Bob in Paris"
        scenarios[0].tags = []
        scenarios[1].tags = []
        scenarios[2].tags = []
        # -- FAKE-CHECK:
        scenarios[0].should_run_with_name_select.return_value = False
        scenarios[1].should_run_with_name_select.return_value = False
        scenarios[2].should_run_with_name_select.return_value = True

        for scenario in scenarios:
            scenario.run.return_value = False

        self.config.tag_expression.check.return_value = True  # pylint: disable=no-member
        self.config.name = ["(?!Alice)"]    # Exclude all scenarios with "Alice"
        self.config.name_re = Configuration.build_name_re(self.config.name)

        feature = Feature("foo.feature", 1, u"Feature", u"foo",
                          scenarios=scenarios)

        feature.run(self.runner)

        assert not scenarios[0].run.called
        scenarios[0].should_run_with_name_select.assert_called_with(self.config)
        scenarios[1].should_run_with_name_select.assert_called_with(self.config)
        scenarios[2].should_run_with_name_select.assert_called_with(self.config)
        scenarios[0].run.assert_not_called()
        scenarios[1].run.assert_not_called()
        scenarios[2].run.assert_called_with(self.runner)

    def test_feature_hooks_not_run_if_feature_not_being_run(self):
        self.config.tag_expression.check.return_value = False  # pylint: disable=no-member

        feature = Feature("foo.feature", 1, u"Feature", u"foo")
        feature.run(self.runner)
        assert not self.run_hook.called


class TestScenarioRun(unittest.TestCase):
    # pylint: disable=invalid-name

    def setUp(self):
        config = Mock()
        config.dry_run = False
        config.should_capture.return_value = False

        formatters = [Mock()]
        run_hook = Mock()

        runner = Mock()
        runner.config = config
        runner.capture_controller = CaptureController(config)
        runner.aborted = False
        runner.feature.tags = []
        runner.formatters = formatters
        runner.run_hook = run_hook

        context = Mock()
        runner.context = context

        self.config = config
        self.context = context
        self.formatters = formatters
        self.runner = runner
        self.run_hook = run_hook

    def test_run_invokes_formatter_scenario_and_steps_correctly(self):
        self.config.capture_stdout = False
        self.config.capture_log = False
        self.config.tag_expression.check.return_value = True  # pylint: disable=no-member
        steps = [Mock(), Mock()]
        scenario = Scenario("foo.feature", 17, u"Scenario", u"foo",
                            steps=steps)

        scenario.run(self.runner)

        self.formatters[0].scenario.assert_called_with(scenario)
        for step in steps:
            step.run.assert_called_with(self.runner)

    def test_handles_capture_stdout_and_log(self):
        self.config.capture_stdout = True
        self.config.capture_log = True
        self.config.tag_expression.check.return_value = True  # pylint: disable=no-member

        steps = [Mock(), Mock()]
        scenario = Scenario("foo.feature", 17, u"Scenario", u"foo",
                            steps=steps)

        scenario.run(self.runner)
        self.runner.setup_capture.assert_called_with(name="scenario")
        self.runner.teardown_capture.assert_called_with()


    def test_undefined_step_causes_errored_scenario_status(self):
        self.config.capture_stdout = False
        self.config.capture_log = False
        self.config.tag_expression.check.return_value = True  # pylint: disable=no-member
        self.config.dry_run = False

        passed_step = Mock()
        undefined_step = Mock()

        steps = [passed_step, undefined_step]
        scenario = Scenario("foo.feature", 17, u"Scenario", u"foo",
                            steps=steps)
        passed_step.run.return_value = True
        passed_step.status = Status.passed
        undefined_step.run.return_value = False
        undefined_step.status = Status.undefined

        runFailed = scenario.run(self.runner)
        assert runFailed is True
        assert undefined_step.status == Status.undefined
        assert scenario.status == Status.error
        # pylint: disable=protected-access
        self.context._set_root_attribute.assert_called_with("failed", True)

    def test_skipped_steps_set_step_status_and_scenario_status_if_not_set(self):
        self.config.capture_stdout = False
        self.config.capture_log = False
        self.config.tag_expression.check.return_value = False  # pylint: disable=no-member

        steps = [Mock(), Mock()]
        scenario = Scenario("foo.feature", 17, u"Scenario", u"foo",
                            steps=steps)

        scenario.run(self.runner)

        assert all([step.status == Status.skipped for step in steps])
        assert scenario.status == Status.skipped

    def test_scenario_hooks_not_run_if_scenario_not_being_run(self):
        self.config.tag_expression.check.return_value = False  # pylint: disable=no-member

        scenario = Scenario("foo.feature", 17, u"Scenario", u"foo")
        scenario.run(self.runner)
        assert not self.run_hook.called

    def test_should_run_with_name_select(self):
        scenario_name = u"first scenario"
        scenario = Scenario("foo.feature", 17, u"Scenario", scenario_name)

        self.config.name = ["first .*", "second .*"]
        self.config.name_re = Configuration.build_name_re(self.config.name)
        assert scenario.should_run_with_name_select(self.config)


class TestScenarioRun2(object):
    """Some additional tests for "Scenario.run()" using pytest."""
    @classmethod
    def make_runner(cls):
        # XXX config = Mock()
        config_data = dict(
            dry_run=False,
            capture_stdout=False,
            capture_log=False,
        )
        config = Configuration(load_config=False, **config_data)
        # XXX config.tag_expression.check.return_value = True  # pylint: disable=no-member

        runner = ModelRunner(config)
        runner.context = Context(runner)
        runner.aborted = False
        runner.feature = Mock()
        runner.feature.tags = []
        runner.formatters = [Mock()]
        runner.run_hook = Mock()
        return runner

    @classmethod
    def make_mock_runner(cls):
        config = Mock()
        config.dry_run = False
        config.capture = False
        config.capture_stdout = False
        config.capture_stderr = False
        config.capture_log = False
        config.tag_expression.check.return_value = True  # pylint: disable=no-member
        config.should_capture.return_value = False

        runner = Mock(config=config)
        runner.capture_controller = CaptureController(config)
        runner.context = Mock(runner=runner)
        # runner.step_registry = xxx
        runner.aborted = False
        runner.feature = Mock()
        runner.feature.tags = []
        runner.formatters = [Mock()]
        runner.run_hook = Mock()
        return runner

    def test_failed_step_causes_context_failure_to_be_set(self):
        # XXX runner = self.make_runner()
        runner = self.make_mock_runner()
        steps = [
            Mock(step_type="given", name="step0", status=Status.failed),
            Mock(step_type="then", name="step1", status=Status.passed),
        ]
        scenario = Scenario("foo.feature", 17, u"Scenario", u"foo", steps=steps)
        steps[0].run.return_value = False

        # pylint: disable=protected-access
        has_run_failed = scenario.run(runner)
        assert has_run_failed
        runner.context._set_root_attribute.assert_called_with("failed", True)

    @pytest.mark.parametrize("failed_status", [Status.error, Status.failed])
    def test_failed_step_causes_remaining_steps_to_be_skipped(self, failed_status):
        runner = self.make_runner()
        scenario_text = u"""
            Scenario: Fails in step0
              Given step0
              When step1
        """
        scenario = parse_scenario(scenario_text)

        # -- REGISTER STEPS:
        step_container = SimpleStepContainer()
        with use_step_import_modules(step_container):
            from behave import given, when
            @when(u'step1')
            def step_for_step1(ctx):
                print("CALLED: step1")
                pass

            if failed_status == Status.failed:
                # -- VARIANT 1: AssertionError is raised (or: assert fails)
                @given(u'step0')
                def step_for_step0A(ctx):
                    print("CALLED: step0-A")
                    raise AssertionError("FAILED-OOPS")
            else:
                # -- VARIANT 2: Any other Exception is raised
                @given(u'step0')
                def step_for_step0E(ctx):
                    print("CALLED: step0-E")
                    raise Exception("ERROR-OOPS")

        runner.step_registry = step_container.step_registry
        run_scenario_failed = scenario.run(runner)
        assert run_scenario_failed
        assert scenario.steps[0].status == failed_status
        assert scenario.steps[1].status == Status.skipped
        assert scenario.status == failed_status


class TestScenarioOutline(unittest.TestCase):
    # pylint: disable=invalid-name

    @staticmethod
    def make_scenario_outline(**kwargs):
        filename = kwargs.pop("filename", "foo.feature")
        line_number = kwargs.pop("line", 17)
        keyword = kwargs.pop("keyword", u"Scenario Outline")
        name = kwargs.pop("name", u"foo")
        outline = ScenarioOutline(filename=filename, line=line_number,
                                  keyword=keyword, name=name, **kwargs)
        return outline

    @classmethod
    def make_scenario_outline_with_table(cls, table_headings, table_data, **kwargs):
        outline = cls.make_scenario_outline(**kwargs)
        exanple = Examples(outline.filename, outline.line+10, u"Examples", u"")
        exanple.table = Table.from_data([u"column1"], [
            [u"cell_1_1"],
            [u"cell_2_1"],
        ])
        outline.examples.append(exanple)
        return outline

    def test_run_calls_run_on_each_generated_scenario(self):
        # pylint: disable=protected-access
        outline = self.make_scenario_outline()
        # -- OVERRIDE: outline._scenarios
        outline._scenarios = [Mock(), Mock()]
        for scenario in outline._scenarios:
            scenario.run.return_value = False

        runner = Mock()
        runner.context = Mock()

        outline.run(runner)

        for s in outline._scenarios:
            s.run.assert_called_with(runner)

    def test_run_stops_on_first_failure_if_requested(self):
        # pylint: disable=protected-access
        outline = self.make_scenario_outline_with_table(["column1"], [
            ["cell_1_1"],
            ["cell_2_1"],
        ])
        _generate_scenarios = outline.scenarios
        # -- OVERRIDE: outline._scenarios
        outline._scenarios = [Mock(), Mock()]
        outline._scenarios[0].run.return_value = True

        runner = Mock()
        runner.context = Mock()
        config = runner.config = Mock()
        config.stop = True

        outline.run(runner)

        outline._scenarios[0].run.assert_called_with(runner)
        assert not outline._scenarios[1].run.called

    def test_run_sets_context_variable_for_outline(self):
        # pylint: disable=protected-access
        outline = self.make_scenario_outline_with_table([u"column1"], [
            [u"one"],
            [u"two"],
            [u"three"],
        ])
        _generate_scenarios = outline.scenarios

        # -- OVERRIDE: outline._scenarios
        outline._scenarios = [Mock(), Mock(), Mock()]
        for scenario in outline._scenarios:
            scenario.run.return_value = False

        runner = Mock()
        context = runner.context = Mock()
        config = runner.config = Mock()
        config.stop = True

        outline.run(runner)

        assert context._set_root_attribute.call_args_list == [
            (("active_outline", outline._scenarios[0]._row), {}),
            (("active_outline", outline._scenarios[1]._row), {}),
            (("active_outline", outline._scenarios[2]._row), {}),
            (("active_outline", None), {}),
        ]

    def test_run_should_pass_when_all_examples_pass(self):
        # pylint: disable=protected-access
        outline = self.make_scenario_outline_with_table([u"column1"], [
            [u"one"],
            [u"two"],
            [u"three"],
        ])
        _generate_scenarios = outline.scenarios

        # -- OVERRIDE: outline._scenarios
        outline._scenarios = [Mock(), Mock(), Mock()]
        for scenario in outline._scenarios:
            scenario.run.return_value = False

        runner = Mock()
        runner.context = Mock()
        config = runner.config = Mock()
        config.stop = True

        result_failed = outline.run(runner)
        assert result_failed is False

    def test_run_should_fail_when_first_examples_fails(self):
        outline = self.make_scenario_outline_with_table([u"column1"], [
            [u"one"],
            [u"two"],
        ])
        _generate_scenarios = outline.scenarios
        failed = True

        # -- OVERRIDE: outline._scenarios
        # pylint: disable=protected-access
        outline._scenarios = [Mock(), Mock()]
        outline._scenarios[0].run.return_value = failed
        outline._scenarios[1].run.return_value = not failed

        runner = Mock()
        runner.context = Mock()
        config = runner.config = Mock()
        config.stop = True

        result_failed = outline.run(runner)
        assert result_failed is True

    def test_run_should_fail_when_last_examples_fails(self):
        outline = self.make_scenario_outline_with_table([u"column1"], [
            [u"one"],
            [u"two"],
        ])
        _generate_scenarios = outline.scenarios
        failed = True

        # -- OVERRIDE: outline._scenarios
        # pylint: disable=protected-access
        outline._scenarios = [Mock(), Mock()]
        outline._scenarios[0].run.return_value = not failed
        outline._scenarios[1].run.return_value = failed

        runner = Mock()
        runner.context = Mock()
        config = runner.config = Mock()
        config.stop = True

        result_failed = outline.run(runner)
        assert result_failed is True

    def test_run_should_fail_when_middle_examples_fails(self):
        outline = self.make_scenario_outline_with_table([u"column1"], [
            [u"one"],
            [u"two"],
            [u"three"],
        ])
        _generate_scenarios = outline.scenarios
        failed = True

        # -- OVERRIDE: outline._scenarios
        # pylint: disable=protected-access
        outline._scenarios = [Mock(), Mock(), Mock()]
        outline._scenarios[0].run.return_value = not failed
        outline._scenarios[1].run.return_value = failed
        outline._scenarios[2].run.return_value = not failed

        runner = Mock()
        runner.context = Mock()
        config = runner.config = Mock()
        config.stop = True

        result_failed = outline.run(runner)
        assert result_failed is True


class TestStepRun(unittest.TestCase):
    # pylint: disable=invalid-name

    def setUp(self):
        step_registry = Mock()
        config = Mock()
        config.verbose = False
        config.outputs = [None]

        capture_controller = CaptureController(config)
        runner = Mock(config=config)
        runner.capture_controller = capture_controller
        runner.run_hook = Mock()
        runner.step_registry = step_registry

        context = Context(runner)
        runner.context = context

        current_scenario = Mock()
        current_scenario.tags = []
        current_scenario.effective_tags = []

        self.capture_controller = capture_controller
        self.runner = runner
        # self.capture_controller = self.runner.capture_controller = Mock()
        self.step_registry = step_registry
        self.config = config
        self.context = context  # WAS: Mock()
        self.context.scenario = current_scenario
        print("context is %s" % self.context)
        self.formatters = self.runner.formatters = [Mock()]
        self.capture_stdout = self.capture_controller.capture_stdout = Mock()
        self.capture_stdout.getvalue.return_value = ''
        self.capture_stderr = self.capture_controller.capture_stderr = Mock()
        self.capture_stderr.getvalue.return_value = ''
        self.capture_log = self.capture_controller.capture_log = Mock()
        self.capture_log.getvalue.return_value = ''
        self.run_hook = runner.run_hook

    def test_run_appends_step_to_undefined_when_no_match_found(self):
        step = Step("foo.feature", 17, u"Given", "given", u"foo")
        self.runner.step_registry.find_match.return_value = None
        self.runner.undefined_steps = []
        self.runner.config.dry_run = False
        assert not step.run(self.runner)

        assert step in self.runner.undefined_steps
        assert step.status == Status.undefined

    def test_run_appends_step_to_undefined_when_no_match_found_in_dry_run_mode(self):
        step = Step("foo.feature", 17, u"Given", "given", u"foo")
        self.runner.step_registry.find_match.return_value = None
        self.runner.undefined_steps = []
        self.runner.config.dry_run = True
        assert not step.run(self.runner)

        assert step in self.runner.undefined_steps
        assert step.status == Status.untested_undefined

    def test_run_reports_undefined_step_via_formatter_when_not_quiet(self):
        step = Step("foo.feature", 17, u"Given", "given", u"foo")
        self.runner.step_registry.find_match.return_value = None
        assert not step.run(self.runner)

        self.formatters[0].match.assert_called_with(NoMatch())
        self.formatters[0].result.assert_called_with(step)

    def test_run_with_no_match_does_not_touch_formatter_when_quiet(self):
        step = Step("foo.feature", 17, u"Given", "given", u"foo")
        self.runner.step_registry.find_match.return_value = None
        assert not step.run(self.runner, quiet=True)

        assert not self.formatters[0].match.called
        assert not self.formatters[0].result.called

    def test_run_when_not_quiet_reports_match_and_result(self):
        step = Step("foo.feature", 17, u"Given", "given", u"foo")
        match = Mock()
        self.runner.step_registry.find_match.return_value = match

        side_effects = (None, raiser(AssertionError("whee")),
                        raiser(Exception("whee")))
        for side_effect in side_effects:
            match.run.side_effect = side_effect
            step.run(self.runner)
            self.formatters[0].match.assert_called_with(match)
            self.formatters[0].result.assert_called_with(step)

    def test_run_when_quiet_reports_nothing(self):
        step = Step("foo.feature", 17, u"Given", "given", u"foo")
        match = Mock()
        self.runner.step_registry.find_match.return_value = match

        side_effects = (None, raiser(AssertionError("whee")),
                        raiser(Exception("whee")))
        for side_effect in side_effects:
            match.run.side_effect = side_effect
            step.run(self.runner, quiet=True)
            assert not self.formatters[0].match.called
            assert not self.formatters[0].result.called

    def test_run_runs_before_hook_then_match_then_after_hook(self):
        step = Step("foo.feature", 17, u"Given", "given", u"foo")
        match = Mock()
        self.runner.step_registry.find_match.return_value = match

        side_effects = (None, AssertionError("whee"), Exception("whee"))
        for side_effect in side_effects:
            # Make match.run() and runner.run_hook() the same mock so
            # we can make sure things happen in the right order.
            self.runner.run_hook = match.run = Mock()

            def effect(thing):
                # pylint: disable=unused-argument
                def raiser_(*args, **kwargs):
                    match.run.side_effect = None
                    if thing:
                        raise thing

                def nonraiser(*args, **kwargs):
                    match.run.side_effect = raiser_

                return nonraiser

            match.run.side_effect = effect(side_effect)
            step.run(self.runner)

            assert match.run.call_args_list == [
                (("before_step", step), {}),
                ((self.context,), {}),
                (("after_step", step), {}),
            ]

    def test_run_sets_table_if_present(self):
        step = Step("foo.feature", 17, u"Given", "given", u"foo",
                    table=Mock())
        self.runner.step_registry.find_match.return_value = Mock()
        step.run(self.runner)
        assert self.context.table == step.table

    def test_run_sets_text_if_present(self):
        step = Step("foo.feature", 17, u"Given", "given", u"foo",
                    text=Mock(name="text"))
        self.runner.step_registry.find_match.return_value = Mock()
        step.run(self.runner)

        assert self.context.text == step.text

    def test_run_sets_status_to_passed_if_nothing_goes_wrong(self):
        step = Step("foo.feature", 17, u"Given", "given", u"foo")
        step.error_message = None
        self.runner.step_registry.find_match.return_value = Mock()
        step.run(self.runner)

        assert step.status == Status.passed
        assert step.error_message is None

    def test_run_sets_status_to_failed_on_assertion_error_with_capture(self):
        self.runner.context = Context(self.runner)
        current_scenario = Mock()
        current_scenario.tags = []
        current_scenario.effective_tags = []
        self.runner.context.scenario = current_scenario
        self.runner.config.capture_stdout = True
        self.runner.config.capture_log = False
        self.runner.capture_controller = CaptureController(self.runner.config)
        self.runner.capture_controller.setup_capture()

        step = Step("foo.feature", 17, u"Given", "given", u"foo")
        step.error_message = None
        match = Mock()
        match.run.side_effect = raiser(AssertionError("whee"))
        self.runner.step_registry.find_match.return_value = match
        step.run(self.runner)

        assert step.status == Status.failed
        assert step.error_message.startswith("ASSERT FAILED")

    @patch("%s.format_exc" % traceback_modname)
    def test_run_sets_status_to_failed_on_assertion_error(self, format_exc):
        step = Step("foo.feature", 17, u"Given", "given", u"foo")
        step.error_message = None
        match = Mock()
        match.run.side_effect = raiser(AssertionError("whee"))
        self.runner.step_registry.find_match.return_value = match
        format_exc.return_value = "ASSERT FAILED: whee"

        step.run(self.runner)
        assert step.status == Status.failed
        assert step.error_message == format_exc.return_value

    @patch("%s.format_exc" % traceback_modname)
    def test_run_sets_status_to_error_on_exception(self, format_exc):
        step = Step("foo.feature", 17, u"Given", "given", u"foo")
        step.error_message = None
        match = Mock()
        match.run.side_effect = raiser(Exception("whee"))
        self.runner.step_registry.find_match.return_value = match
        format_exc.return_value = "something to do with an exception"

        step.run(self.runner)
        assert step.status == Status.error
        assert step.error_message == format_exc.return_value

    @patch("time.time")
    def test_run_calculates_duration(self, time_time):
        step = Step("foo.feature", 17, u"Given", "given", u"foo")
        match = Mock()
        self.runner.step_registry.find_match.return_value = match

        def time_time_1():
            def time_time_2():
                return 23
            time_time.side_effect = time_time_2
            return 17

        side_effects = (None, raiser(AssertionError("whee")),
                        raiser(Exception("whee")))
        for side_effect in side_effects:
            match.run.side_effect = side_effect
            time_time.side_effect = time_time_1

            step.run(self.runner)
            assert step.duration == (23 - 17)

    def test_run_captures_stdout_and_logging(self):
        step = Step("foo.feature", 17, u"Given", "given", u"foo")
        match = Mock()
        self.runner.step_registry.find_match.return_value = match

        assert step.run(self.runner)

        self.runner.start_capture.assert_called_with()
        self.runner.stop_capture.assert_called_with()

    def test_run_appends_any_captured_stdout_on_failure(self):
        step = Step("foo.feature", 17, u"Given", "given", u"foo")
        match = Mock()
        self.runner.step_registry.find_match.return_value = match
        self.capture_stdout.getvalue.return_value = "frogs"
        match.run.side_effect = raiser(AssertionError("halibut"))

        run_step_failed = step.run(self.runner)
        assert not run_step_failed
        assert "frogs" not in step.error_message

        # -- CAPTURED-OUTPUT: Stored in step
        captured = step.captured
        captured_output = captured.make_simple_report()
        assert "frogs" in captured_output
        assert "CAPTURED STDOUT:" in captured_output

    def test_run_appends_any_captured_logging_on_failure(self):
        step = Step("foo.feature", 17, u"Given", "given", u"foo")
        match = Mock()
        self.runner.step_registry.find_match.return_value = match
        self.capture_log.getvalue.return_value = "toads"
        match.run.side_effect = raiser(AssertionError("kipper"))

        run_step_failed = not step.run(self.runner)
        assert run_step_failed
        assert "toads" not in step.error_message

        # -- CAPTURED-OUTPUT: Stored in step
        captured_output = step.captured.make_simple_report()
        assert "CAPTURED LOG:" in captured_output
        assert "toads" in captured_output

    def test_run_appends_any_captured_stdout_on_error(self):
        step = Step("foo.feature", 17, u"Given", "given", u"foo")
        match = Mock()
        self.runner.step_registry.find_match.return_value = match
        self.capture_stdout.getvalue.return_value = "frogs"
        match.run.side_effect = raiser(Exception("halibut"))

        run_step_failed = not step.run(self.runner)
        assert run_step_failed
        assert "frogs" not in step.error_message

        # -- CAPTURED-OUTPUT: Stored in step
        captured_output = step.captured.make_simple_report()
        assert "CAPTURED STDOUT:" in captured_output
        assert "frogs" in captured_output

    def test_run_appends_any_captured_logging_on_error(self):
        step = Step("foo.feature", 17, u"Given", "given", u"foo")
        match = Mock()
        self.runner.step_registry.find_match.return_value = match
        self.capture_log.getvalue.return_value = "toads"
        match.run.side_effect = raiser(RuntimeError("kipper"))

        run_step_failed = not step.run(self.runner)
        assert run_step_failed
        assert "toads" not in step.error_message

        # -- CAPTURED-OUTPUT: Stored in step
        captured_output = step.captured.make_simple_report()
        assert "CAPTURED LOG:" in captured_output
        assert "toads" in captured_output


class TestTableModel(object):
    # pylint: disable=invalid-name
    HEADINGS = [u"type of stuff", u"awesomeness", u"ridiculousness"]
    TABLE_DATA = [
        [u"fluffy", u"large", u"frequent"],
        [u"lint", u"low", u"high"],
        [u"green", u"variable", u"awkward"],
    ]

    @classmethod
    def make_table(cls):
        return Table(cls.HEADINGS, rows=cls.TABLE_DATA, line=0)

    def test_equivalence(self):
        table_1 = self.make_table()
        table_2 = self.make_table()
        assert table_1 == table_2

    def test_table_iteration(self):
        table = self.make_table()
        for i, row in enumerate(table):
            for j, cell in enumerate(row):
                assert cell == self.TABLE_DATA[i][j]

    def test_table_row_by_index(self):
        table = self.make_table()
        for i in range(3):
            assert table[i] == Row(self.HEADINGS, self.TABLE_DATA[i], 0)

    def test_table_row_name(self):
        table = self.make_table()
        assert table[0]["type of stuff"] == "fluffy"
        assert table[1]["awesomeness"] == "low"
        assert table[2]["ridiculousness"] == "awkward"

    def test_table_row_index(self):
        table = self.make_table()
        assert table[0][0] == "fluffy"
        assert table[1][1] == "low"
        assert table[2][2] == "awkward"

    def test_table_row_keyerror(self):
        table = self.make_table()
        with pytest.raises(KeyError):
            # pylint: disable=pointless-statement
            table[0]["spam"]

    def test_table_row_items(self):
        table = self.make_table()
        assert list(table[0].items()) == list(zip(self.HEADINGS, self.TABLE_DATA[0]))


class TestModelRow(object):
    # pylint: disable=invalid-name, bad-whitespace
    HEADINGS = [u"name",  u"sex",   u"age"]
    ROW_DATA = [u"Alice", u"female", u"12"]

    @classmethod
    def make_row(cls):
        return Row(cls.HEADINGS, cls.ROW_DATA, 0)

    def test_len(self):
        row = self.make_row()
        assert len(row) == 3

    def test_getitem_with_valid_colname(self):
        # pylint: disable=bad-whitespace
        row = self.make_row()
        assert row["name"] == u"Alice"
        assert row["sex"] == u"female"
        assert row["age"] == u"12"

    def test_getitem_with_unknown_colname(self):
        row = self.make_row()
        with pytest.raises(KeyError):
            # pylint: disable=pointless-statement
            row["__UNKNOWN_COLUMN__"]

    def test_getitem_with_valid_index(self):
        row = self.make_row()
        assert row[0] == u"Alice"
        assert row[1] == u"female"
        assert row[2] == u"12"

    def test_getitem_with_invalid_index(self):
        row = self.make_row()
        columns_size = len(row)
        assert columns_size == 3
        with pytest.raises(IndexError):
            row[columns_size]   # pylint: disable=pointless-statement

    def test_get_with_valid_colname(self):
        # pylint: disable=bad-whitespace
        row = self.make_row()
        assert row.get("name") == u"Alice"
        assert row.get("sex") ==  u"female"
        assert row.get("age") ==  u"12"

    def test_getitem_with_unknown_colname_should_return_default(self):
        row = self.make_row()
        assert row.get("__UNKNOWN_COLUMN__", "XXX") == u"XXX"

    def test_as_dict(self):
        row = self.make_row()
        data1 = row.as_dict()
        data2 = dict(row.as_dict())
        assert isinstance(data1, dict)
        assert isinstance(data2, dict)
        assert isinstance(data1, OrderedDict)
        # -- REQUIRES: Python2.7 or ordereddict installed.
        # assert not isinstance(data2, OrderedDict)
        assert data1 == data2
        # pylint: disable=bad-whitespace
        assert data1["name"] == u"Alice"
        assert data1["sex"] == u"female"
        assert data1["age"] == u"12"

    def test_contains(self):
        row = self.make_row()
        assert "name" in row
        assert "sex" in row
        assert "age" in row
        assert "non-existent-header" not in row
