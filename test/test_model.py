from __future__ import with_statement

import re
import sys
from mock import Mock, patch
from nose.tools import *
from behave import model
from behave.compat.collections import OrderedDict
from behave import step_registry
from behave.configuration import Configuration


class TestFeatureRun(object):
    def setUp(self):
        self.runner = Mock()
        self.runner.feature.tags = []
        self.config = self.runner.config = Mock()
        self.context = self.runner.context = Mock()
        self.formatters = self.runner.formatters = [Mock()]
        self.run_hook = self.runner.run_hook = Mock()

    def test_formatter_feature_called(self):
        feature = model.Feature('foo.feature', 1, u'Feature', u'foo',
                                background=Mock())

        feature.run(self.runner)

        self.formatters[0].feature.assert_called_with(feature)

    def test_formatter_background_called_when_feature_has_background(self):
        feature = model.Feature('foo.feature', 1, u'Feature', u'foo',
                                background=Mock())

        feature.run(self.runner)

        self.formatters[0].background.assert_called_with(feature.background)

    def test_formatter_background_not_called_when_feature_has_no_background(self):
        feature = model.Feature('foo.feature', 1, u'Feature', u'foo')

        feature.run(self.runner)

        assert not self.formatters[0].background.called

    def test_run_runs_scenarios(self):
        scenarios = [Mock(), Mock()]
        for scenario in scenarios:
            scenario.tags = []
            scenario.run.return_value = False

        self.config.tags.check.return_value = True
        self.config.name = []

        feature = model.Feature('foo.feature', 1, u'Feature', u'foo',
                                scenarios=scenarios)

        feature.run(self.runner)

        for scenario in scenarios:
            scenario.run.assert_called_with(self.runner)

    def test_run_runs_named_scenarios(self):
        scenarios = [Mock(), Mock()]
        scenarios[0].name = 'first scenario'
        scenarios[1].name = 'second scenario'
        scenarios[0].tags = []
        scenarios[1].tags = []

        for scenario in scenarios:
            scenario.run.return_value = False

        self.config.tags.check.return_value = True
        self.config.name = ['first', 'third']
        self.config.name_re = Configuration.build_name_re(self.config.name)

        feature = model.Feature('foo.feature', 1, u'Feature', u'foo',
                                scenarios=scenarios)

        feature.run(self.runner)

        scenarios[0].run.assert_called_with(self.runner)
        assert not scenarios[1].run.called

    def test_run_runs_named_scenarios_with_regexp(self):
        scenarios = [Mock(), Mock()]
        scenarios[0].name = 'first scenario'
        scenarios[1].name = 'second scenario'
        scenarios[0].tags = []
        scenarios[1].tags = []

        for scenario in scenarios:
            scenario.run.return_value = False

        self.config.tags.check.return_value = True
        self.config.name = ['third .*', 'second .*']
        self.config.name_re = Configuration.build_name_re(self.config.name)

        feature = model.Feature('foo.feature', 1, u'Feature', u'foo',
                                scenarios=scenarios)

        feature.run(self.runner)

        assert not scenarios[0].run.called
        scenarios[1].run.assert_called_with(self.runner)

    def test_feature_hooks_not_run_if_feature_not_being_run(self):
        self.config.tags.check.return_value = False

        feature = model.Feature('foo.feature', 1, u'Feature', u'foo')

        feature.run(self.runner)

        assert not self.run_hook.called


class TestScenarioRun(object):
    def setUp(self):
        self.runner = Mock()
        self.runner.feature.tags = []
        self.config = self.runner.config = Mock()
        self.config.dry_run = False
        self.context = self.runner.context = Mock()
        self.formatters = self.runner.formatters = [Mock()]
        self.run_hook = self.runner.run_hook = Mock()

    def test_run_invokes_formatter_scenario_and_steps_correctly(self):
        self.config.stdout_capture = False
        self.config.log_capture = False
        self.config.tags.check.return_value = True
        steps = [Mock(), Mock()]
        scenario = model.Scenario('foo.feature', 17, u'Scenario', u'foo',
                                  steps=steps)

        scenario.run(self.runner)

        self.formatters[0].scenario.assert_called_with(scenario)
        [step.run.assert_called_with(self.runner) for step in steps]

    if sys.version_info[0] == 3:
        stringio_target = 'io.StringIO'
    else:
        stringio_target = 'StringIO.StringIO'

    def test_handles_stdout_and_log_capture(self):
        self.config.stdout_capture = True
        self.config.log_capture = True
        self.config.tags.check.return_value = True

        steps = [Mock(), Mock()]
        scenario = model.Scenario('foo.feature', 17, u'Scenario', u'foo',
                                  steps=steps)

        scenario.run(self.runner)

        self.runner.setup_capture.assert_called_with()
        self.runner.teardown_capture.assert_called_with()

    def test_failed_step_causes_remaining_steps_to_be_skipped(self):
        self.config.stdout_capture = False
        self.config.log_capture = False
        self.config.tags.check.return_value = True

        steps = [Mock(), Mock()]
        scenario = model.Scenario('foo.feature', 17, u'Scenario', u'foo',
                                  steps=steps)
        steps[0].run.return_value = False
        steps[1].step_type = "when"
        steps[1].name = "step1"

        def step1_function(context):
            pass
        my_step_registry = step_registry.StepRegistry()
        my_step_registry.add_step_definition("when", "step1", step1_function)

        with patch("behave.step_registry.registry", my_step_registry):
            assert scenario.run(self.runner)
            eq_(steps[1].status, 'skipped')

    def test_failed_step_causes_context_failure_to_be_set(self):
        self.config.stdout_capture = False
        self.config.log_capture = False
        self.config.tags.check.return_value = True

        steps = [
            Mock(step_type="given", name="step0"),
            Mock(step_type="then",  name="step1"),
        ]
        scenario = model.Scenario('foo.feature', 17, u'Scenario', u'foo',
                                  steps=steps)
        steps[0].run.return_value = False

        assert scenario.run(self.runner)
        self.context._set_root_attribute.assert_called_with('failed', True)

    def test_undefined_step_causes_failed_scenario_status(self):
        self.config.stdout_capture = False
        self.config.log_capture = False
        self.config.tags.check.return_value = True

        passed_step = Mock()
        undefined_step = Mock()

        steps = [passed_step, undefined_step]
        scenario = model.Scenario('foo.feature', 17, u'Scenario', u'foo',
                                  steps=steps)
        passed_step.run.return_value = True
        passed_step.status = 'passed'
        undefined_step.run.return_value = False
        undefined_step.status = 'undefined'

        assert scenario.run(self.runner)
        eq_(undefined_step.status, 'undefined')
        eq_(scenario.status, 'failed')
        self.context._set_root_attribute.assert_called_with('failed', True)

    def test_skipped_steps_set_step_status_and_scenario_status_if_not_set(self):
        self.config.stdout_capture = False
        self.config.log_capture = False
        self.config.tags.check.return_value = False

        steps = [Mock(), Mock()]
        scenario = model.Scenario('foo.feature', 17, u'Scenario', u'foo',
                                  steps=steps)

        scenario.run(self.runner)

        assert False not in [s.status == 'skipped' for s in steps]
        eq_(scenario.status, 'skipped')

    def test_scenario_hooks_not_run_if_scenario_not_being_run(self):
        self.config.tags.check.return_value = False

        scenario = model.Scenario('foo.feature', 17, u'Scenario', u'foo')

        scenario.run(self.runner)

        assert not self.run_hook.called


class TestScenarioOutline(object):
    def test_run_calls_run_on_each_generated_scenario(self):
        outline = model.ScenarioOutline('foo.feature', 17, u'Scenario Outline',
                                        u'foo')
        outline._scenarios = [Mock(), Mock()]
        for scenario in outline._scenarios:
            scenario.run.return_value = False

        runner = Mock()
        runner.context = Mock()

        outline.run(runner)

        [s.run.assert_called_with(runner) for s in outline._scenarios]

    def test_run_stops_on_first_failure_if_requested(self):
        outline = model.ScenarioOutline('foo.feature', 17, u'Scenario Outline',
                                        u'foo')
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
        outline = model.ScenarioOutline('foo.feature', 17, u'Scenario Outline',
                                        u'foo')
        outline._scenarios = [Mock(), Mock(), Mock()]
        for scenario in outline._scenarios:
            scenario.run.return_value = False

        runner = Mock()
        context = runner.context = Mock()
        config = runner.config = Mock()
        config.stop = True

        outline.run(runner)

        eq_(context._set_root_attribute.call_args_list, [
            (('active_outline', outline._scenarios[0]._row), {}),
            (('active_outline', outline._scenarios[1]._row), {}),
            (('active_outline', outline._scenarios[2]._row), {}),
            (('active_outline', None), {}),
        ])

    def test_run_should_pass_when_all_examples_pass(self):
        outline = model.ScenarioOutline('foo.feature', 17, u'Scenario Outline',
                                        u'foo')
        outline._scenarios = [Mock(), Mock(), Mock()]
        for scenario in outline._scenarios:
            scenario.run.return_value = False

        runner = Mock()
        context = runner.context = Mock()
        config = runner.config = Mock()
        config.stop = True

        resultFailed = outline.run(runner)
        eq_(resultFailed, False)

    def test_run_should_fail_when_first_examples_fails(self):
        outline = model.ScenarioOutline('foo.feature', 17, u'Scenario Outline',
                                        u'foo')
        failed = True
        outline._scenarios = [Mock(), Mock()]
        outline._scenarios[0].run.return_value = failed
        outline._scenarios[1].run.return_value = not failed

        runner = Mock()
        context = runner.context = Mock()
        config = runner.config = Mock()
        config.stop = True

        resultFailed = outline.run(runner)
        eq_(resultFailed, True)

    def test_run_should_fail_when_last_examples_fails(self):
        outline = model.ScenarioOutline('foo.feature', 17, u'Scenario Outline',
                                        u'foo')
        failed = True
        outline._scenarios = [Mock(), Mock()]
        outline._scenarios[0].run.return_value = not failed
        outline._scenarios[1].run.return_value = failed

        runner = Mock()
        context = runner.context = Mock()
        config = runner.config = Mock()
        config.stop = True

        resultFailed = outline.run(runner)
        eq_(resultFailed, True)

    def test_run_should_fail_when_middle_examples_fails(self):
        outline = model.ScenarioOutline('foo.feature', 17, u'Scenario Outline',
                                        u'foo')
        failed = True
        outline._scenarios = [Mock(), Mock(), Mock()]
        outline._scenarios[0].run.return_value = not failed
        outline._scenarios[1].run.return_value = failed
        outline._scenarios[2].run.return_value = not failed

        runner = Mock()
        context = runner.context = Mock()
        config = runner.config = Mock()
        config.stop = True

        resultFailed = outline.run(runner)
        eq_(resultFailed, True)


def raiser(exception):
    def func(*args, **kwargs):
        raise exception
    return func


class TestStepRun(object):
    def setUp(self):
        self.runner = Mock()
        self.config = self.runner.config = Mock()
        self.config.outputs = [None]
        self.context = self.runner.context = Mock()
        print ('context is', self.context)
        self.formatters = self.runner.formatters = [Mock()]
        self.step_registry = Mock()
        self.stdout_capture = self.runner.stdout_capture = Mock()
        self.stdout_capture.getvalue.return_value = ''
        self.stderr_capture = self.runner.stderr_capture = Mock()
        self.stderr_capture.getvalue.return_value = ''
        self.log_capture = self.runner.log_capture = Mock()
        self.log_capture.getvalue.return_value = ''
        self.run_hook = self.runner.run_hook = Mock()

    def test_run_appends_step_to_undefined_when_no_match_found(self):
        step = model.Step('foo.feature', 17, u'Given', 'given', u'foo')
        self.step_registry.find_match.return_value = None
        self.runner.undefined = []
        with patch('behave.step_registry.registry', self.step_registry):
            assert not step.run(self.runner)

        assert step in self.runner.undefined
        eq_(step.status, 'undefined')

    def test_run_reports_undefined_step_via_formatter_when_not_quiet(self):
        step = model.Step('foo.feature', 17, u'Given', 'given', u'foo')
        self.step_registry.find_match.return_value = None
        with patch('behave.step_registry.registry', self.step_registry):
            assert not step.run(self.runner)

        self.formatters[0].match.assert_called_with(model.NoMatch())
        self.formatters[0].result.assert_called_with(step)

    def test_run_with_no_match_does_not_touch_formatter_when_quiet(self):
        step = model.Step('foo.feature', 17, u'Given', 'given', u'foo')
        self.step_registry.find_match.return_value = None
        with patch('behave.step_registry.registry', self.step_registry):
            assert not step.run(self.runner, quiet=True)

        assert not self.formatters[0].match.called
        assert not self.formatters[0].result.called

    def test_run_when_not_quiet_reports_match_and_result(self):
        step = model.Step('foo.feature', 17, u'Given', 'given', u'foo')
        match = Mock()
        self.step_registry.find_match.return_value = match

        side_effects = (None, raiser(AssertionError('whee')),
                        raiser(Exception('whee')))
        for side_effect in side_effects:
            match.run.side_effect = side_effect
            with patch('behave.step_registry.registry', self.step_registry):
                step.run(self.runner)
            self.formatters[0].match.assert_called_with(match)
            self.formatters[0].result.assert_called_with(step)

    def test_run_when_quiet_reports_nothing(self):
        step = model.Step('foo.feature', 17, u'Given', 'given', u'foo')
        match = Mock()
        self.step_registry.find_match.return_value = match

        side_effects = (None, raiser(AssertionError('whee')),
                raiser(Exception('whee')))
        for side_effect in side_effects:
            match.run.side_effect = side_effect
            step.run(self.runner, quiet=True)
            assert not self.formatters[0].match.called
            assert not self.formatters[0].result.called

    def test_run_runs_before_hook_then_match_then_after_hook(self):
        step = model.Step('foo.feature', 17, u'Given', 'given', u'foo')
        match = Mock()
        self.step_registry.find_match.return_value = match

        side_effects = (None, AssertionError('whee'), Exception('whee'))
        for side_effect in side_effects:
            # Make match.run() and runner.run_hook() the same mock so
            # we can make sure things happen in the right order.
            self.runner.run_hook = match.run = Mock()

            def effect(thing):
                def raiser(*args, **kwargs):
                    match.run.side_effect = None
                    if thing:
                        raise thing

                def nonraiser(*args, **kwargs):
                    match.run.side_effect = raiser

                return nonraiser

            match.run.side_effect = effect(side_effect)
            with patch('behave.step_registry.registry', self.step_registry):
                step.run(self.runner)

            eq_(match.run.call_args_list, [
                (('before_step', self.context, step), {}),
                ((self.context,), {}),
                (('after_step', self.context, step), {}),
            ])

    def test_run_sets_table_if_present(self):
        step = model.Step('foo.feature', 17, u'Given', 'given', u'foo',
                          table=Mock())
        self.step_registry.find_match.return_value = Mock()

        with patch('behave.step_registry.registry', self.step_registry):
            step.run(self.runner)

        eq_(self.context.table, step.table)

    def test_run_sets_text_if_present(self):
        step = model.Step('foo.feature', 17, u'Given', 'given', u'foo',
                          text=Mock(name='text'))
        self.step_registry.find_match.return_value = Mock()

        with patch('behave.step_registry.registry', self.step_registry):
            step.run(self.runner)

        eq_(self.context.text, step.text)

    def test_run_sets_status_to_passed_if_nothing_goes_wrong(self):
        step = model.Step('foo.feature', 17, u'Given', 'given', u'foo')
        step.error_message = None
        self.step_registry.find_match.return_value = Mock()

        with patch('behave.step_registry.registry', self.step_registry):
            step.run(self.runner)

        eq_(step.status, 'passed')
        eq_(step.error_message, None)

    def test_run_sets_status_to_failed_on_assertion_error(self):
        step = model.Step('foo.feature', 17, u'Given', 'given', u'foo')
        step.error_message = None
        match = Mock()
        match.run.side_effect = raiser(AssertionError('whee'))
        self.step_registry.find_match.return_value = match

        with patch('behave.step_registry.registry', self.step_registry):
            step.run(self.runner)

        eq_(step.status, 'failed')
        assert step.error_message.startswith('Assertion Failed')

    @patch('traceback.format_exc')
    def test_run_sets_status_to_failed_on_exception(self, format_exc):
        step = model.Step('foo.feature', 17, u'Given', 'given', u'foo')
        step.error_message = None
        match = Mock()
        match.run.side_effect = raiser(Exception('whee'))
        self.step_registry.find_match.return_value = match
        format_exc.return_value = 'something to do with an exception'

        with patch('behave.step_registry.registry', self.step_registry):
            step.run(self.runner)

        eq_(step.status, 'failed')
        eq_(step.error_message, format_exc.return_value)

    @patch('time.time')
    def test_run_calculates_duration(self, time_time):
        step = model.Step('foo.feature', 17, u'Given', 'given', u'foo')
        match = Mock()
        self.step_registry.find_match.return_value = match

        def time_time_1():
            def time_time_2():
                return 23
            time_time.side_effect = time_time_2
            return 17

        side_effects = (None, raiser(AssertionError('whee')),
                raiser(Exception('whee')))
        for side_effect in side_effects:
            match.run.side_effect = side_effect
            time_time.side_effect = time_time_1

            with patch('behave.step_registry.registry', self.step_registry):
                step.run(self.runner)
            eq_(step.duration, 23 - 17)

    def test_run_captures_stdout_and_logging(self):
        step = model.Step('foo.feature', 17, u'Given', 'given', u'foo')
        match = Mock()
        self.step_registry.find_match.return_value = match

        with patch('behave.step_registry.registry', self.step_registry):
            assert step.run(self.runner)

        self.runner.start_capture.assert_called_with()
        self.runner.stop_capture.assert_called_with()

    def test_run_appends_any_captured_stdout_on_failure(self):
        step = model.Step('foo.feature', 17, u'Given', 'given', u'foo')
        match = Mock()
        self.step_registry.find_match.return_value = match
        self.stdout_capture.getvalue.return_value = 'frogs'
        match.run.side_effect = raiser(Exception('halibut'))

        with patch('behave.step_registry.registry', self.step_registry):
            assert not step.run(self.runner)

        assert 'Captured stdout:' in step.error_message
        assert 'frogs' in step.error_message

    def test_run_appends_any_captured_logging_on_failure(self):
        step = model.Step('foo.feature', 17, u'Given', 'given', u'foo')
        match = Mock()
        self.step_registry.find_match.return_value = match
        self.log_capture.getvalue.return_value = 'toads'
        match.run.side_effect = raiser(AssertionError('kipper'))

        with patch('behave.step_registry.registry', self.step_registry):
            assert not step.run(self.runner)

        assert 'Captured logging:' in step.error_message
        assert 'toads' in step.error_message


class TestTableModel(object):
    HEAD = [u'type of stuff', u'awesomeness', u'ridiculousness']
    DATA = [
        [u'fluffy', u'large', u'frequent'],
        [u'lint', u'low', u'high'],
        [u'green', u'variable', u'awkward'],
    ]

    def setUp(self):
        self.table = model.Table(self.HEAD, 0, self.DATA)

    def test_equivalence(self):
        t1 = self.table
        self.setUp()
        eq_(t1, self.table)

    def test_table_iteration(self):
        for i, row in enumerate(self.table):
            for j, cell in enumerate(row):
                eq_(cell, self.DATA[i][j])

    def test_table_row_by_index(self):
        for i in range(3):
            eq_(self.table[i], model.Row(self.HEAD, self.DATA[i], 0))

    def test_table_row_name(self):
        eq_(self.table[0]['type of stuff'], 'fluffy')
        eq_(self.table[1]['awesomeness'], 'low')
        eq_(self.table[2]['ridiculousness'], 'awkward')

    def test_table_row_index(self):
        eq_(self.table[0][0], 'fluffy')
        eq_(self.table[1][1], 'low')
        eq_(self.table[2][2], 'awkward')

    @raises(KeyError)
    def test_table_row_keyerror(self):
        self.table[0]['spam']

    def test_table_row_items(self):
        eq_(self.table[0].items(), zip(self.HEAD, self.DATA[0]))


class TestModelRow(object):
    HEAD = [u'name',  u'sex',    u'age']
    DATA = [u'Alice', u'female', u'12']

    def setUp(self):
        self.row = model.Row(self.HEAD, self.DATA, 0)

    def test_len(self):
        eq_(len(self.row), 3)

    def test_getitem_with_valid_colname(self):
        eq_(self.row['name'], u'Alice')
        eq_(self.row['sex'],  u'female')
        eq_(self.row['age'],  u'12')

    @raises(KeyError)
    def test_getitem_with_unknown_colname(self):
        self.row['__UNKNOWN_COLUMN__']

    def test_getitem_with_valid_index(self):
        eq_(self.row[0], u'Alice')
        eq_(self.row[1], u'female')
        eq_(self.row[2], u'12')

    @raises(IndexError)
    def test_getitem_with_invalid_index(self):
        colsize = len(self.row)
        eq_(colsize, 3)
        self.row[colsize]

    def test_get_with_valid_colname(self):
        eq_(self.row.get('name'), u'Alice')
        eq_(self.row.get('sex'),  u'female')
        eq_(self.row.get('age'),  u'12')

    def test_getitem_with_unknown_colname_should_return_default(self):
        eq_(self.row.get('__UNKNOWN_COLUMN__', 'XXX'), u'XXX')

    def test_as_dict(self):
        data1 = self.row.as_dict()
        data2 = dict(self.row.as_dict())
        assert isinstance(data1, dict)
        assert isinstance(data2, dict)
        assert isinstance(data1, OrderedDict)
        # -- REQUIRES: Python2.7 or ordereddict installed.
        # assert not isinstance(data2, OrderedDict)
        eq_(data1, data2)
        eq_(data1['name'], u'Alice')
        eq_(data1['sex'],  u'female')
        eq_(data1['age'],  u'12')


class TestFileLocation(object):
    ordered_locations1 = [
        model.FileLocation("features/alice.feature",   1),
        model.FileLocation("features/alice.feature",   5),
        model.FileLocation("features/alice.feature",  10),
        model.FileLocation("features/alice.feature",  11),
        model.FileLocation("features/alice.feature", 100),
    ]
    ordered_locations2 = [
        model.FileLocation("features/alice.feature",     1),
        model.FileLocation("features/alice.feature",    10),
        model.FileLocation("features/bob.feature",       5),
        model.FileLocation("features/charly.feature", None),
        model.FileLocation("features/charly.feature",    0),
        model.FileLocation("features/charly.feature",  100),
    ]
    same_locations = [
        ( model.FileLocation("alice.feature"),
          model.FileLocation("alice.feature", None),
        ),
        ( model.FileLocation("alice.feature", 10),
          model.FileLocation("alice.feature", 10),
        ),
        ( model.FileLocation("features/bob.feature", 11),
          model.FileLocation("features/bob.feature", 11),
        ),
    ]

    def test_compare_equal(self):
        for value1, value2 in self.same_locations:
            eq_(value1, value2)

    def test_compare_equal_with_string(self):
        for location in self.ordered_locations2:
            eq_(location, location.filename)
            eq_(location.filename, location)

    def test_compare_not_equal(self):
        for value1, value2 in self.same_locations:
            assert not(value1 != value2)

        for locations in [self.ordered_locations1, self.ordered_locations2]:
            for value1, value2 in zip(locations, locations[1:]):
                assert value1 != value2

    def test_compare_less_than(self):
        for locations in [self.ordered_locations1, self.ordered_locations2]:
            for value1, value2 in zip(locations, locations[1:]):
                assert value1  < value2, "FAILED: %s < %s" % (str(value1), str(value2))
                assert value1 != value2

    def test_compare_less_than_with_string(self):
        locations = self.ordered_locations2
        for value1, value2 in zip(locations, locations[1:]):
            if value1.filename == value2.filename:
                continue
            assert value1  < value2.filename, "FAILED: %s < %s" % (str(value1), str(value2.filename))
            assert value1.filename < value2,  "FAILED: %s < %s" % (str(value1.filename), str(value2))

    def test_compare_greater_than(self):
        for locations in [self.ordered_locations1, self.ordered_locations2]:
            for value1, value2 in zip(locations, locations[1:]):
                assert value2  > value1, "FAILED: %s > %s" % (str(value2), str(value1))
                assert value2 != value1

    def test_compare_less_or_equal(self):
        for value1, value2 in self.same_locations:
            assert value1 <= value2, "FAILED: %s <= %s" % (str(value1), str(value2))
            assert value1 == value2

        for locations in [self.ordered_locations1, self.ordered_locations2]:
            for value1, value2 in zip(locations, locations[1:]):
                assert value1 <= value2, "FAILED: %s <= %s" % (str(value1), str(value2))
                assert value1 != value2

    def test_compare_greater_or_equal(self):
        for value1, value2 in self.same_locations:
            assert value2 >= value1, "FAILED: %s >= %s" % (str(value2), str(value1))
            assert value2 == value1

        for locations in [self.ordered_locations1, self.ordered_locations2]:
            for value1, value2 in zip(locations, locations[1:]):
                assert value2 >= value1, "FAILED: %s >= %s" % (str(value2), str(value1))
                assert value2 != value1

    def test_filename_should_be_same_as_self(self):
        for location in self.ordered_locations2:
            assert location == location.filename
            assert location.filename == location

    def test_string_conversion(self):
        for location in self.ordered_locations2:
            expected = u"%s:%s" % (location.filename, location.line)
            if location.line is None:
                expected = location.filename
            assert str(location) == expected

    def test_repr_conversion(self):
        for location in self.ordered_locations2:
            expected = u'<FileLocation: filename="%s", line=%s>' % \
                       (location.filename, location.line)
            actual = repr(location)
            assert actual == expected, "FAILED: %s == %s" % (actual, expected)
