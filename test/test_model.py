from __future__ import with_statement

import sys

from mock import Mock, patch
from nose.tools import *

from behave import model


class TestFeatureRun(object):
    def setUp(self):
        self.runner = Mock()
        self.runner.feature.tags = []
        self.config = self.runner.config = Mock()
        self.context = self.runner.context = Mock()
        self.formatter = self.runner.formatter = Mock()
        self.run_hook = self.runner.run_hook = Mock()

    def test_formatter_feature_called(self):
        feature = model.Feature('foo.feature', 1, u'Feature', u'foo',
                                background=Mock())

        feature.run(self.runner)

        self.formatter.feature.assert_called_with(feature)

    def test_formatter_background_called_when_feature_has_background(self):
        feature = model.Feature('foo.feature', 1, u'Feature', u'foo',
                                background=Mock())

        feature.run(self.runner)

        self.formatter.background.assert_called_with(feature.background)

    def test_formatter_background_not_called_when_feature_has_no_background(self):
        feature = model.Feature('foo.feature', 1, u'Feature', u'foo')

        feature.run(self.runner)

        assert not self.formatter.background.called

    def test_run_runs_scenarios(self):
        scenarios = [Mock(), Mock()]
        for scenario in scenarios:
            scenario.run.return_value = False

        self.config.tags.check.return_value = True

        feature = model.Feature('foo.feature', 1, u'Feature', u'foo',
                                scenarios=scenarios)

        feature.run(self.runner)

        for scenario in scenarios:
            scenario.run.assert_called_with(self.runner)

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
        self.formatter = self.runner.formatter = Mock()
        self.run_hook = self.runner.run_hook = Mock()

    def test_run_invokes_formatter_scenario_and_steps_correctly(self):
        self.config.stdout_capture = False
        self.config.log_capture = False
        self.config.tags.check.return_value = True
        steps = [Mock(), Mock()]
        scenario = model.Scenario('foo.feature', 17, u'Scenario', u'foo',
                                  steps=steps)

        scenario.run(self.runner)

        self.formatter.scenario.assert_called_with(scenario)
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

        assert scenario.run(self.runner)

        eq_(steps[1].status, 'skipped')

    def test_failed_step_causes_context_failure_to_be_set(self):
        self.config.stdout_capture = False
        self.config.log_capture = False
        self.config.tags.check.return_value = True

        steps = [Mock(), Mock()]
        scenario = model.Scenario('foo.feature', 17, u'Scenario', u'foo',
                                  steps=steps)
        steps[0].run.return_value = False

        assert scenario.run(self.runner)

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
        outline = model.ScenarioOutline('foo.featuer', 17, u'Scenario Outline',
                                        u'foo')
        outline._scenarios = [Mock(), Mock()]
        for scenario in outline._scenarios:
            scenario.run.return_value = False

        runner = Mock()
        context = runner.context = Mock()

        outline.run(runner)

        [s.run.assert_called_with(runner) for s in outline._scenarios]

    def test_run_stops_on_first_failure_if_requested(self):
        outline = model.ScenarioOutline('foo.featuer', 17, u'Scenario Outline',
                                        u'foo')
        outline._scenarios = [Mock(), Mock()]
        outline._scenarios[0].run.return_value = True

        runner = Mock()
        context = runner.context = Mock()
        config = runner.config = Mock()
        config.stop = True

        outline.run(runner)

        outline._scenarios[0].run.assert_called_with(runner)
        assert not outline._scenarios[1].run.called

    def test_run_sets_context_variable_for_outline(self):
        outline = model.ScenarioOutline('foo.featuer', 17, u'Scenario Outline',
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


def raiser(exception):
    def func(*args, **kwargs):
        raise exception
    return func


class TestStepRun(object):
    def setUp(self):
        self.runner = Mock()
        self.config = self.runner.config = Mock()
        self.context = self.runner.context = Mock()
        print ('context is', self.context)
        self.formatter = self.runner.formatter = Mock()
        self.step_registry = Mock()
        self.stdout_capture = self.runner.stdout_capture = Mock()
        self.stdout_capture.getvalue.return_value = ''
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

        self.formatter.match.assert_called_with(model.NoMatch())
        self.formatter.result.assert_called_with(step)

    def test_run_with_no_match_does_not_touch_formatter_when_quiet(self):
        step = model.Step('foo.feature', 17, u'Given', 'given', u'foo')
        self.step_registry.find_match.return_value = None
        with patch('behave.step_registry.registry', self.step_registry):
            assert not step.run(self.runner, quiet=True)

        assert not self.formatter.match.called
        assert not self.formatter.result.called

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
            self.formatter.match.assert_called_with(match)
            self.formatter.result.assert_called_with(step)

    def test_run_when_quiet_reports_nothing(self):
        step = model.Step('foo.feature', 17, u'Given', 'given', u'foo')
        match = Mock()
        self.step_registry.find_match.return_value = match

        side_effects = (None, raiser(AssertionError('whee')),
                raiser(Exception('whee')))
        for side_effect in side_effects:
            match.run.side_effect = side_effect
            step.run(self.runner, quiet=True)
            assert not self.formatter.match.called
            assert not self.formatter.result.called

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
        last = None
        for i, row in enumerate(self.table):
            for j, cell in enumerate(row):
                eq_(cell, self.DATA[i][j])

    def test_table_row_by_index(self):
        for i in range(3):
            eq_(self.table[i], model.Row(self.HEAD, None, self.DATA[i], 0))

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
