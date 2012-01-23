from mock import Mock, patch
from nose.tools import *

from behave.reporter.summary import SummaryReporter, format_summary

class TestFormatStatus(object):
    def test_passed_entry_contains_label(self):
        summary = {
            'passed': 1,
            'skipped': 0,
            'failed': 0,
            'undefined': 0,
        }

        assert format_summary('fnord', summary).startswith('1 fnord passed')

    def test_passed_entry_is_pluralised(self):
        summary = {
            'passed': 10,
            'skipped': 0,
            'failed': 0,
            'undefined': 0,
        }

        assert format_summary('fnord', summary).startswith('10 fnords passed')

    def test_remaining_fields_are_present(self):
        summary = {
            'passed': 10,
            'skipped': 1,
            'failed': 2,
            'undefined': 3,
        }

        output = format_summary('fnord', summary)

        assert '1 skipped' in output
        assert '2 failed' in output
        assert '3 undefined' in output

    def test_missing_fields_are_not_present(self):
        summary = {
            'passed': 10,
            'skipped': 1,
            'failed': 2,
        }

        output = format_summary('fnord', summary)

        assert '1 skipped' in output
        assert '2 failed' in output
        assert 'undefined' not in output

class TestSummaryReporter(object):
    def test_duration_is_totalled_up_and_outputted(self):
        features = [Mock(), Mock(), Mock(), Mock()]
        features[0].duration = 1.9
        features[0].status = 'passed'
        features[0].__iter__ = Mock(return_value=iter([]))
        features[1].duration = 2.7
        features[1].status = 'passed'
        features[1].__iter__ = Mock(return_value=iter([]))
        features[2].duration = 3.5
        features[2].status = 'passed'
        features[2].__iter__ = Mock(return_value=iter([]))
        features[3].duration = 4.3
        features[3].status = 'passed'
        features[3].__iter__ = Mock(return_value=iter([]))

        config = Mock()
        reporter = SummaryReporter(config)

        [reporter.feature(f) for f in features]
        eq_(round(reporter.duration, 3), 12.400)

        reporter.end()
        output = config.output.write.call_args_list[-1][0][0]
        minutes = int(reporter.duration / 60)
        seconds = reporter.duration % 60

        assert '%dm' % (minutes,) in output
        assert '%02.1f' % (seconds,) in output

    @patch('behave.reporter.summary.format_summary')
    def test_feature_status_is_collected_and_reported(self, format_summary):
        features = [Mock(), Mock(), Mock(), Mock(), Mock()]
        features[0].duration = 1.9
        features[0].status = 'passed'
        features[0].__iter__ = Mock(return_value=iter([]))
        features[1].duration = 2.7
        features[1].status = 'failed'
        features[1].__iter__ = Mock(return_value=iter([]))
        features[2].duration = 3.5
        features[2].status = 'skipped'
        features[2].__iter__ = Mock(return_value=iter([]))
        features[3].duration = 4.3
        features[3].status = 'passed'
        features[3].__iter__ = Mock(return_value=iter([]))
        features[4].duration = 5.1
        features[4].status = None
        features[4].__iter__ = Mock(return_value=iter([]))

        config = Mock()
        reporter = SummaryReporter(config)

        [reporter.feature(f) for f in features]
        reporter.end()

        expected = {
            'passed': 2,
            'failed': 1,
            'skipped': 2,
            'untested': 0,
        }

        eq_(format_summary.call_args_list[0][0], ('feature', expected))

    @patch('behave.reporter.summary.format_summary')
    def test_scenario_status_is_collected_and_reported(self, format_summary):
        feature = Mock()
        scenarios = [Mock(), Mock(), Mock(), Mock(), Mock()]
        scenarios[0].status = 'failed'
        scenarios[0].__iter__ = Mock(return_value=iter([]))
        scenarios[1].status = 'failed'
        scenarios[1].__iter__ = Mock(return_value=iter([]))
        scenarios[2].status = 'skipped'
        scenarios[2].__iter__ = Mock(return_value=iter([]))
        scenarios[3].status = 'passed'
        scenarios[3].__iter__ = Mock(return_value=iter([]))
        scenarios[4].status = None
        scenarios[4].__iter__ = Mock(return_value=iter([]))
        feature.status = 'failed'
        feature.duration = 12.3
        feature.__iter__ = Mock(return_value=iter(scenarios))

        config = Mock()
        reporter = SummaryReporter(config)

        reporter.feature(feature)
        reporter.end()

        expected = {
            'passed': 1,
            'failed': 2,
            'skipped': 2,
            'untested': 0,
        }

        eq_(format_summary.call_args_list[1][0], ('scenario', expected))

    @patch('behave.reporter.summary.format_summary')
    def test_step_status_is_collected_and_reported(self, format_summary):
        feature = Mock()
        scenario = Mock()
        steps = [Mock(), Mock(), Mock(), Mock(), Mock()]
        steps[0].status = 'failed'
        steps[0].__iter__ = Mock(return_value=iter([]))
        steps[1].status = 'undefined'
        steps[1].__iter__ = Mock(return_value=iter([]))
        steps[2].status = 'passed'
        steps[2].__iter__ = Mock(return_value=iter([]))
        steps[3].status = 'passed'
        steps[3].__iter__ = Mock(return_value=iter([]))
        steps[4].status = None
        steps[4].__iter__ = Mock(return_value=iter([]))
        feature.status = 'failed'
        feature.duration = 12.3
        feature.__iter__ = Mock(return_value=iter([scenario]))
        scenario.status = 'failed'
        scenario.__iter__ = Mock(return_value=iter(steps))

        config = Mock()
        reporter = SummaryReporter(config)

        reporter.feature(feature)
        reporter.end()

        expected = {
            'passed': 2,
            'failed': 1,
            'skipped': 1,
            'untested': 0,
            'undefined': 1,
        }

        eq_(format_summary.call_args_list[2][0], ('step', expected))
