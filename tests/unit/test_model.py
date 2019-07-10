# -*- coding: utf-8 -*-
# pylint: disable=no-self-use, line-too-long

from __future__ import absolute_import, print_function, with_statement
import unittest
import pytest
from mock import Mock, patch
import six
from six.moves import range     # pylint: disable=redefined-builtin
from six.moves import zip       # pylint: disable=redefined-builtin
from behave.model_core import Status
from behave.model import Feature, Scenario, ScenarioOutline, Step
from behave.model import Table, Row
from behave.matchers import NoMatch
from behave.runner import Context
from behave.capture import CaptureController
from behave.configuration import Configuration
from behave.compat.collections import OrderedDict
from behave import step_registry

if six.PY2:
    # pylint: disable=unused-import
    traceback_modname = "traceback2"
else:
    # pylint: disable=unused-import
    traceback_modname = "traceback"


class TestFeatureRun(unittest.TestCase):
    # pylint: disable=invalid-name

    def setUp(self):
        config = Mock()
        config.tag_expression.check.return_value = True
        self.runner = Mock()
        self.runner.aborted = False
        self.runner.feature.tags = []
        self.config = self.runner.config = config
        self.context = self.runner.context = Mock()
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
        self.runner = Mock()
        self.runner.aborted = False
        self.runner.feature.tags = []
        self.config = self.runner.config = Mock()
        self.config.dry_run = False
        self.context = self.runner.context = Mock()
        self.formatters = self.runner.formatters = [Mock()]
        self.run_hook = self.runner.run_hook = Mock()

    def test_run_invokes_formatter_scenario_and_steps_correctly(self):
        self.config.stdout_capture = False
        self.config.log_capture = False
        self.config.tag_expression.check.return_value = True  # pylint: disable=no-member
        steps = [Mock(), Mock()]
        scenario = Scenario("foo.feature", 17, u"Scenario", u"foo",
                            steps=steps)

        scenario.run(self.runner)

        self.formatters[0].scenario.assert_called_with(scenario)
        for step in steps:
            step.run.assert_called_with(self.runner)

    if six.PY3:
        stringio_target = "io.StringIO"
    else:
        stringio_target = "StringIO.StringIO"

    def test_handles_stdout_and_log_capture(self):
        self.config.stdout_capture = True
        self.config.log_capture = True
        self.config.tag_expression.check.return_value = True  # pylint: disable=no-member

        steps = [Mock(), Mock()]
        scenario = Scenario("foo.feature", 17, u"Scenario", u"foo",
                            steps=steps)

        scenario.run(self.runner)

        self.runner.setup_capture.assert_called_with()
        self.runner.teardown_capture.assert_called_with()

    def test_failed_step_causes_remaining_steps_to_be_skipped(self):
        self.config.stdout_capture = False
        self.config.log_capture = False
        self.config.tag_expression.check.return_value = True  # pylint: disable=no-member

        steps = [Mock(), Mock()]
        scenario = Scenario("foo.feature", 17, u"Scenario", u"foo",
                            steps=steps)
        steps[0].run.return_value = False
        steps[1].step_type = "when"
        steps[1].name = "step1"

        def step1_function(context):    # pylint: disable=unused-argument
            pass
        my_step_registry = step_registry.StepRegistry()
        my_step_registry.add_step_definition("when", "step1", step1_function)

        with patch("behave.step_registry.registry", my_step_registry):
            assert scenario.run(self.runner)
            assert steps[1].status == Status.skipped

    def test_failed_step_causes_context_failure_to_be_set(self):
        self.config.stdout_capture = False
        self.config.log_capture = False
        self.config.tag_expression.check.return_value = True  # pylint: disable=no-member

        steps = [
            Mock(step_type="given", name="step0"),
            Mock(step_type="then", name="step1"),
        ]
        scenario = Scenario("foo.feature", 17, u"Scenario", u"foo",
                            steps=steps)
        steps[0].run.return_value = False

        assert scenario.run(self.runner)
        # pylint: disable=protected-access
        self.context._set_root_attribute.assert_called_with("failed", True)

    def test_undefined_step_causes_failed_scenario_status(self):
        self.config.stdout_capture = False
        self.config.log_capture = False
        self.config.tag_expression.check.return_value = True  # pylint: disable=no-member

        passed_step = Mock()
        undefined_step = Mock()

        steps = [passed_step, undefined_step]
        scenario = Scenario("foo.feature", 17, u"Scenario", u"foo",
                            steps=steps)
        passed_step.run.return_value = True
        passed_step.status = Status.passed
        undefined_step.run.return_value = False
        undefined_step.status = Status.undefined

        assert scenario.run(self.runner)
        assert undefined_step.status == Status.undefined
        assert scenario.status == Status.failed
        # pylint: disable=protected-access
        self.context._set_root_attribute.assert_called_with("failed", True)

    def test_skipped_steps_set_step_status_and_scenario_status_if_not_set(self):
        self.config.stdout_capture = False
        self.config.log_capture = False
        self.config.tag_expression.check.return_value = False  # pylint: disable=no-member

        steps = [Mock(), Mock()]
        scenario = Scenario("foo.feature", 17, u"Scenario", u"foo",
                            steps=steps)

        scenario.run(self.runner)

        assert False not in [s.status == Status.skipped for s in steps]
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

class TestScenarioOutline(unittest.TestCase):
    # pylint: disable=invalid-name

    def test_run_calls_run_on_each_generated_scenario(self):
        # pylint: disable=protected-access
        outline = ScenarioOutline("foo.feature", 17, u"Scenario Outline",
                                  u"foo")
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
        outline = ScenarioOutline("foo.feature", 17, u"Scenario Outline",
                                  u"foo")
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
        outline = ScenarioOutline("foo.feature", 17, u"Scenario Outline",
                                  u"foo")
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
        outline = ScenarioOutline("foo.feature", 17, u"Scenario Outline",
                                  u"foo")
        outline._scenarios = [Mock(), Mock(), Mock()]
        for scenario in outline._scenarios:
            scenario.run.return_value = False

        runner = Mock()
        context = runner.context = Mock()
        config = runner.config = Mock()
        config.stop = True

        resultFailed = outline.run(runner)
        assert resultFailed is False

    def test_run_should_fail_when_first_examples_fails(self):
        outline = ScenarioOutline("foo.feature", 17, u"Scenario Outline",
                                  u"foo")
        failed = True
        # pylint: disable=protected-access
        outline._scenarios = [Mock(), Mock()]
        outline._scenarios[0].run.return_value = failed
        outline._scenarios[1].run.return_value = not failed

        runner = Mock()
        context = runner.context = Mock()
        config = runner.config = Mock()
        config.stop = True

        resultFailed = outline.run(runner)
        assert resultFailed is True

    def test_run_should_fail_when_last_examples_fails(self):
        outline = ScenarioOutline("foo.feature", 17, u"Scenario Outline",
                                  u"foo")
        failed = True
        # pylint: disable=protected-access
        outline._scenarios = [Mock(), Mock()]
        outline._scenarios[0].run.return_value = not failed
        outline._scenarios[1].run.return_value = failed

        runner = Mock()
        context = runner.context = Mock()
        config = runner.config = Mock()
        config.stop = True

        resultFailed = outline.run(runner)
        assert resultFailed is True

    def test_run_should_fail_when_middle_examples_fails(self):
        outline = ScenarioOutline("foo.feature", 17, u"Scenario Outline",
                                  u"foo")
        failed = True
        # pylint: disable=protected-access
        outline._scenarios = [Mock(), Mock(), Mock()]
        outline._scenarios[0].run.return_value = not failed
        outline._scenarios[1].run.return_value = failed
        outline._scenarios[2].run.return_value = not failed

        runner = Mock()
        context = runner.context = Mock()
        config = runner.config = Mock()
        config.stop = True

        resultFailed = outline.run(runner)
        assert resultFailed is True


def raiser(exception):
    def func(*args, **kwargs):    # pylint: disable=unused-argument
        raise exception
    return func


class TestStepRun(unittest.TestCase):
    # pylint: disable=invalid-name

    def setUp(self):
        self.step_registry = Mock()
        self.runner = Mock()
        # self.capture_controller = self.runner.capture_controller = Mock()
        self.capture_controller = CaptureController(self.runner.config)
        self.runner.capture_controller = self.capture_controller
        self.runner.step_registry = self.step_registry
        self.config = self.runner.config = Mock()
        self.config.outputs = [None]
        self.context = self.runner.context = Mock()
        print("context is %s" % self.context)
        self.formatters = self.runner.formatters = [Mock()]
        self.stdout_capture = self.capture_controller.stdout_capture = Mock()
        self.stdout_capture.getvalue.return_value = ''
        self.stderr_capture = self.capture_controller.stderr_capture = Mock()
        self.stderr_capture.getvalue.return_value = ''
        self.log_capture = self.capture_controller.log_capture = Mock()
        self.log_capture.getvalue.return_value = ''
        self.run_hook = self.runner.run_hook = Mock()

    def test_run_appends_step_to_undefined_when_no_match_found(self):
        step = Step("foo.feature", 17, u"Given", "given", u"foo")
        self.runner.step_registry.find_match.return_value = None
        self.runner.undefined_steps = []
        assert not step.run(self.runner)

        assert step in self.runner.undefined_steps
        assert step.status == Status.undefined

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
                (("before_step", self.context, step), {}),
                ((self.context,), {}),
                (("after_step", self.context, step), {}),
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

    def test_run_sets_status_to_failed_on_assertion_error(self):
        step = Step("foo.feature", 17, u"Given", "given", u"foo")
        self.runner.context = Context(self.runner)
        self.runner.config.stdout_capture = True
        self.runner.config.log_capture = False
        self.runner.capture_controller = CaptureController(self.runner.config)
        self.runner.capture_controller.setup_capture(self.runner.context)
        step.error_message = None
        match = Mock()
        match.run.side_effect = raiser(AssertionError("whee"))
        self.runner.step_registry.find_match.return_value = match
        step.run(self.runner)

        assert step.status == Status.failed
        assert step.error_message.startswith("Assertion Failed")

    @patch("%s.format_exc" % traceback_modname)
    def test_run_sets_status_to_failed_on_exception(self, format_exc):
        step = Step("foo.feature", 17, u"Given", "given", u"foo")
        step.error_message = None
        match = Mock()
        match.run.side_effect = raiser(Exception("whee"))
        self.runner.step_registry.find_match.return_value = match
        format_exc.return_value = "something to do with an exception"

        step.run(self.runner)
        assert step.status == Status.failed
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
        self.stdout_capture.getvalue.return_value = "frogs"
        match.run.side_effect = raiser(Exception("halibut"))

        assert not step.run(self.runner)
        assert "Captured stdout:" in step.error_message
        assert "frogs" in step.error_message

    def test_run_appends_any_captured_logging_on_failure(self):
        step = Step("foo.feature", 17, u"Given", "given", u"foo")
        match = Mock()
        self.runner.step_registry.find_match.return_value = match
        self.log_capture.getvalue.return_value = "toads"
        match.run.side_effect = raiser(AssertionError("kipper"))

        assert not step.run(self.runner)
        assert "Captured logging:" in step.error_message
        assert "toads" in step.error_message


class TestTableModel(unittest.TestCase):
    # pylint: disable=invalid-name
    HEAD = [u"type of stuff", u"awesomeness", u"ridiculousness"]
    DATA = [
        [u"fluffy", u"large", u"frequent"],
        [u"lint", u"low", u"high"],
        [u"green", u"variable", u"awkward"],
    ]

    def setUp(self):
        self.table = Table(self.HEAD, 0, self.DATA)

    def test_equivalence(self):
        t1 = self.table
        self.setUp()
        assert t1 == self.table

    def test_table_iteration(self):
        for i, row in enumerate(self.table):
            for j, cell in enumerate(row):
                assert cell == self.DATA[i][j]

    def test_table_row_by_index(self):
        for i in range(3):
            assert self.table[i] == Row(self.HEAD, self.DATA[i], 0)

    def test_table_row_name(self):
        assert self.table[0]["type of stuff"] == "fluffy"
        assert self.table[1]["awesomeness"] == "low"
        assert self.table[2]["ridiculousness"] == "awkward"

    def test_table_row_index(self):
        assert self.table[0][0] == "fluffy"
        assert self.table[1][1] == "low"
        assert self.table[2][2] == "awkward"

    def test_table_row_keyerror(self):
        with pytest.raises(KeyError):
            # pylint: disable=pointless-statement
            self.table[0]["spam"]

    def test_table_row_items(self):
        assert list(self.table[0].items()) == list(zip(self.HEAD, self.DATA[0]))


class TestModelRow(unittest.TestCase):
    # pylint: disable=invalid-name, bad-whitespace
    HEAD = [u"name",  u"sex",   u"age"]
    DATA = [u"Alice", u"female", u"12"]

    def setUp(self):
        self.row = Row(self.HEAD, self.DATA, 0)

    def test_len(self):
        assert len(self.row) == 3

    def test_getitem_with_valid_colname(self):
        # pylint: disable=bad-whitespace
        assert self.row["name"] == u"Alice"
        assert self.row["sex"] == u"female"
        assert self.row["age"] == u"12"

    def test_getitem_with_unknown_colname(self):
        with pytest.raises(KeyError):
            # pylint: disable=pointless-statement
            self.row["__UNKNOWN_COLUMN__"]

    def test_getitem_with_valid_index(self):
        assert self.row[0] == u"Alice"
        assert self.row[1] == u"female"
        assert self.row[2] == u"12"

    def test_getitem_with_invalid_index(self):
        colsize = len(self.row)
        assert colsize == 3
        with pytest.raises(IndexError):
            self.row[colsize]   # pylint: disable=pointless-statement

    def test_get_with_valid_colname(self):
        # pylint: disable=bad-whitespace
        assert self.row.get("name") == u"Alice"
        assert self.row.get("sex") ==  u"female"
        assert self.row.get("age") ==  u"12"

    def test_getitem_with_unknown_colname_should_return_default(self):
        assert self.row.get("__UNKNOWN_COLUMN__", "XXX") == u"XXX"

    def test_as_dict(self):
        data1 = self.row.as_dict()
        data2 = dict(self.row.as_dict())
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
