from mock import Mock, patch
from nose.tools import *

from behave import model

def raiser(exception):
    def func(*args, **kwargs):
        raise exception
    return func


class TestStepRun(object):
    def setUp(self):
        self.runner = Mock()
        self.config = self.runner.config = Mock()
        self.context = self.runner.context = Mock()
        self.formatter = self.runner.formatter = Mock()
        self.steps = self.runner.steps = Mock()
        self.stdout_capture = self.runner.stdout_capture = Mock()
        self.stdout_capture.getvalue.return_value = ''
        self.log_capture = self.runner.log_capture = Mock()
        self.log_capture.getvalue.return_value = ''
        self.run_hook = self.runner.run_hook = Mock()

    def test_run_resets_text_and_table_before_step(self):
        self.steps.find_match.return_value = None
        step = model.Step('foo.feature', 17, u'Given', 'given', u'foo')
        assert not step.run(self.runner)

        call_args_list = self.context._set_root_attribute.call_args_list
        call_args_list = [x[0] for x in call_args_list]
        assert ('text', None) in call_args_list
        assert ('table', None) in call_args_list

    def test_run_appends_step_to_undefined_when_no_match_found(self):
        step = model.Step('foo.feature', 17, u'Given', 'given', u'foo')
        self.steps.find_match.return_value = None
        self.runner.undefined = []
        assert not step.run(self.runner)

        assert step in self.runner.undefined
        eq_(step.status, 'undefined')

    def test_run_reports_undefined_step_via_formatter_when_not_quiet(self):
        step = model.Step('foo.feature', 17, u'Given', 'given', u'foo')
        self.steps.find_match.return_value = None
        assert not step.run(self.runner)

        self.formatter.match.assert_called_with(model.NoMatch())
        self.formatter.result.assert_called_with(step)

    def test_run_with_no_match_does_not_touch_formatter_when_quiet(self):
        step = model.Step('foo.feature', 17, u'Given', 'given', u'foo')
        self.steps.find_match.return_value = None
        assert not step.run(self.runner, quiet=True)

        assert not self.formatter.match.called
        assert not self.formatter.result.called

    def test_run_when_not_quiet_reports_match_and_result(self):
        step = model.Step('foo.feature', 17, u'Given', 'given', u'foo')
        match = Mock()
        self.steps.find_match.return_value = match

        side_effects = (None, raiser(AssertionError('whee')),
                        raiser(Exception('whee')))
        for side_effect in side_effects:
            match.run.side_effect = side_effect
            step.run(self.runner)
            self.formatter.match.assert_called_with(match)
            self.formatter.result.assert_called_with(step)

    def test_run_when_quiet_reports_nothing(self):
        step = model.Step('foo.feature', 17, u'Given', 'given', u'foo')
        match = Mock()
        self.steps.find_match.return_value = match

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
        self.steps.find_match.return_value = match

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
            step.run(self.runner)

            eq_(match.run.call_args_list, [
                (('before_step', self.context, step), {}),
                ((self.context,), {}),
                (('after_step', self.context, step), {}),
            ])

    def test_run_sets_table_if_present(self):
        step = model.Step('foo.feature', 17, u'Given', 'given', u'foo',
                          table=Mock())
        self.steps.find_match.return_value = Mock()

        step.run(self.runner)

        self.context._set_root_attribute.assert_called_with('table', step.table)

    def test_run_sets_text_if_present(self):
        step = model.Step('foo.feature', 17, u'Given', 'given', u'foo',
                          text=Mock())
        self.steps.find_match.return_value = Mock()

        step.run(self.runner)

        self.context._set_root_attribute.assert_called_with('text', step.text)

    def test_run_sets_status_to_passed_if_nothing_goes_wrong(self):
        step = model.Step('foo.feature', 17, u'Given', 'given', u'foo')
        step.error_message = None
        self.steps.find_match.return_value = Mock()

        step.run(self.runner)

        eq_(step.status, 'passed')
        eq_(step.error_message, None)

    def test_run_sets_status_to_failed_on_assertion_error(self):
        step = model.Step('foo.feature', 17, u'Given', 'given', u'foo')
        step.error_message = None
        match = Mock()
        match.run.side_effect = raiser(AssertionError('whee'))
        self.steps.find_match.return_value = match

        step.run(self.runner)

        eq_(step.status, 'failed')
        assert step.error_message.startswith('Assertion Failed')

    @patch('traceback.format_exc')
    def test_run_sets_status_to_failed_on_exception(self, format_exc):
        step = model.Step('foo.feature', 17, u'Given', 'given', u'foo')
        step.error_message = None
        match = Mock()
        match.run.side_effect = raiser(Exception('whee'))
        self.steps.find_match.return_value = match
        format_exc.return_value = 'something to do with an exception'

        step.run(self.runner)

        eq_(step.status, 'failed')
        eq_(step.error_message, format_exc.return_value)

    @patch('time.time')
    def test_run_calculates_duration(self, time_time):
        step = model.Step('foo.feature', 17, u'Given', 'given', u'foo')
        match = Mock()
        self.steps.find_match.return_value = match

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

            step.run(self.runner)
            eq_(step.duration, 23 - 17)

    def test_run_captures_stdout_if_requested(self):
        step = model.Step('foo.feature', 17, u'Given', 'given', u'foo')
        match = Mock()
        self.steps.find_match.return_value = match

        def printer(*args, **kwargs):
            print 'carrots'

        match.run.side_effect = printer

        assert step.run(self.runner)

        call_args_list = self.stdout_capture.write.call_args_list
        stdout = ''.join(a[0][0] for a in call_args_list)
        eq_(stdout.strip(), 'carrots')

    def test_run_does_not_capture_stdout_if_requested(self):
        step = model.Step('foo.feature', 17, u'Given', 'given', u'foo')
        match = Mock()
        self.steps.find_match.return_value = match
        self.config.stdout_capture = False

        def printer(*args, **kwargs):
            print 'carrots'

        match.run.side_effect = printer

        assert step.run(self.runner)

        assert not self.stdout_capture.write.called

    def test_run_appends_any_captured_stdout_on_failure(self):
        step = model.Step('foo.feature', 17, u'Given', 'given', u'foo')
        match = Mock()
        self.steps.find_match.return_value = match
        self.stdout_capture.getvalue.return_value = 'frogs'
        match.run.side_effect = raiser(Exception('halibut'))

        assert not step.run(self.runner)

        assert 'Captured stdout:' in step.error_message
        assert 'frogs' in step.error_message

    def test_run_appends_any_captured_logging_on_failure(self):
        step = model.Step('foo.feature', 17, u'Given', 'given', u'foo')
        match = Mock()
        self.steps.find_match.return_value = match
        self.log_capture.getvalue.return_value = 'toads'
        match.run.side_effect = raiser(AssertionError('kipper'))

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
