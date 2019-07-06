# -*- coding: UTF-8 -*-

from __future__ import absolute_import, division
import sys
import pytest
from mock import Mock, patch
from behave.model import ScenarioOutline, Scenario
from behave.model_core import Status
from behave.reporter.summary import SummaryReporter, format_summary


class TestFormatStatus(object):
    def test_passed_entry_contains_label(self):
        summary = {
            Status.passed.name: 1,
            Status.skipped.name: 0,
            Status.failed.name: 0,
            Status.undefined.name: 0,
        }

        assert format_summary('fnord', summary).startswith('1 fnord passed')

    def test_passed_entry_is_pluralised(self):
        summary = {
            Status.passed.name: 10,
            Status.skipped.name: 0,
            Status.failed.name: 0,
            Status.undefined.name: 0,
        }

        assert format_summary('fnord', summary).startswith('10 fnords passed')

    def test_remaining_fields_are_present(self):
        summary = {
            Status.passed.name: 10,
            Status.skipped.name: 1,
            Status.failed.name: 2,
            Status.undefined.name: 3,
        }

        output = format_summary('fnord', summary)

        assert '1 skipped' in output
        assert '2 failed' in output
        assert '3 undefined' in output

    def test_missing_fields_are_not_present(self):
        summary = {
            Status.passed.name: 10,
            Status.skipped.name: 1,
            Status.failed.name: 2,
        }

        output = format_summary('fnord', summary)

        assert '1 skipped' in output
        assert '2 failed' in output
        assert Status.undefined.name not in output

class TestSummaryReporter(object):
    @patch('sys.stdout')
    def test_duration_is_totalled_up_and_outputted(self, stdout):
        features = [Mock(), Mock(), Mock(), Mock()]
        features[0].duration = 1.9
        features[0].status = Status.passed
        features[0].__iter__ = Mock(return_value=iter([]))
        features[1].duration = 2.7
        features[1].status = Status.passed
        features[1].__iter__ = Mock(return_value=iter([]))
        features[2].duration = 3.5
        features[2].status = Status.passed
        features[2].__iter__ = Mock(return_value=iter([]))
        features[3].duration = 4.3
        features[3].status = Status.passed
        features[3].__iter__ = Mock(return_value=iter([]))

        config = Mock()
        sys.stdout.encoding = "UTF-8"
        reporter = SummaryReporter(config)

        [reporter.feature(f) for f in features]
        assert round(reporter.duration, 3) == 12.400

        reporter.end()
        output = stdout.write.call_args_list[-1][0][0]
        minutes = int(reporter.duration / 60.0)
        seconds = reporter.duration % 60

        assert '%dm' % (minutes,) in output
        assert '%02.1f' % (seconds,) in output

    @patch('sys.stdout')
    @patch('behave.reporter.summary.format_summary')
    def test_feature_status_is_collected_and_reported(self, format_summary,
                                                      stdout):
        features = [Mock(), Mock(), Mock(), Mock(), Mock()]
        features[0].duration = 1.9
        features[0].status = Status.passed
        features[0].__iter__ = Mock(return_value=iter([]))
        features[1].duration = 2.7
        features[1].status = Status.failed
        features[1].__iter__ = Mock(return_value=iter([]))
        features[2].duration = 3.5
        features[2].status = Status.skipped
        features[2].__iter__ = Mock(return_value=iter([]))
        features[3].duration = 4.3
        features[3].status = Status.passed
        features[3].__iter__ = Mock(return_value=iter([]))
        features[4].duration = 5.1
        features[4].status = Status.untested
        features[4].__iter__ = Mock(return_value=iter([]))

        config = Mock()
        sys.stdout.encoding = "UTF-8"
        reporter = SummaryReporter(config)

        [reporter.feature(f) for f in features]
        reporter.end()

        expected = {
            "all": 5,
            Status.passed.name: 2,
            Status.failed.name: 1,
            Status.skipped.name: 1,
            Status.untested.name: 1,
        }
        expected_parts = ("feature", expected)
        assert format_summary.call_args_list[0][0] == expected_parts

    @patch('sys.stdout')
    @patch('behave.reporter.summary.format_summary')
    def test_scenario_status_is_collected_and_reported(self, format_summary,
                                                       stdout):
        feature = Mock()
        scenarios = [Mock(), Mock(), Mock(), Mock(), Mock()]
        scenarios[0].status = Status.failed
        scenarios[0].__iter__ = Mock(return_value=iter([]))
        scenarios[1].status = Status.failed
        scenarios[1].__iter__ = Mock(return_value=iter([]))
        scenarios[2].status = Status.skipped
        scenarios[2].__iter__ = Mock(return_value=iter([]))
        scenarios[3].status = Status.passed
        scenarios[3].__iter__ = Mock(return_value=iter([]))
        scenarios[4].status = Status.untested
        scenarios[4].__iter__ = Mock(return_value=iter([]))
        feature.status = Status.failed
        feature.duration = 12.3
        feature.__iter__ = Mock(return_value=iter(scenarios))

        config = Mock()
        sys.stdout.encoding = "UTF-8"
        reporter = SummaryReporter(config)

        reporter.feature(feature)
        reporter.end()

        expected = {
            "all": 5,
            Status.passed.name: 1,
            Status.failed.name: 2,
            Status.skipped.name: 1,
            Status.untested.name: 1,
        }

        scenario_index = 1  # -- HINT: Index for scenarios if no Rules are used.
        expected_parts = ("scenario", expected)
        assert format_summary.call_args_list[scenario_index][0] == expected_parts

    @patch('behave.reporter.summary.format_summary')
    @patch('sys.stdout')
    def test_scenario_outline_status_is_collected_and_reported(self, stdout,
                                                               format_summary):
        feature = Mock()
        scenarios = [ ScenarioOutline(u"<string>", 0, u"scenario_outline", u"name"),
                      Mock(), Mock(), Mock() ]
        subscenarios = [ Mock(), Mock(), Mock(), Mock() ]
        subscenarios[0].status = Status.passed
        subscenarios[0].__iter__ = Mock(return_value=iter([]))
        subscenarios[1].status = Status.failed
        subscenarios[1].__iter__ = Mock(return_value=iter([]))
        subscenarios[2].status = Status.failed
        subscenarios[2].__iter__ = Mock(return_value=iter([]))
        subscenarios[3].status = Status.skipped
        subscenarios[3].__iter__ = Mock(return_value=iter([]))
        scenarios[0]._scenarios = subscenarios
        scenarios[1].status = Status.failed
        scenarios[1].__iter__ = Mock(return_value=iter([]))
        scenarios[2].status = Status.skipped
        scenarios[2].__iter__ = Mock(return_value=iter([]))
        scenarios[3].status = Status.passed
        scenarios[3].__iter__ = Mock(return_value=iter([]))
        feature.status = Status.failed
        feature.duration = 12.4
        feature.__iter__ = Mock(return_value=iter(scenarios))

        config = Mock()
        sys.stdout.encoding = "UTF-8"
        reporter = SummaryReporter(config)

        reporter.feature(feature)
        reporter.end()

        expected = {
            "all": 7,
            Status.passed.name: 2,
            Status.failed.name: 3,
            Status.skipped.name: 2,
            Status.untested.name: 0,
        }
        scenario_index = 1  # -- HINT: Index for scenarios if no Rules are used.
        expected_parts = ("scenario", expected)
        assert format_summary.call_args_list[scenario_index][0] == expected_parts

    @patch('sys.stdout')
    @patch('behave.reporter.summary.format_summary')
    def test_step_status_is_collected_and_reported(self, format_summary,
                                                   stdout):
        feature = Mock()
        scenario = Mock()
        steps = [Mock(), Mock(), Mock(), Mock(), Mock()]
        steps[0].status = Status.failed
        steps[0].__iter__ = Mock(return_value=iter([]))
        steps[1].status = Status.passed
        steps[1].__iter__ = Mock(return_value=iter([]))
        steps[2].status = Status.passed
        steps[2].__iter__ = Mock(return_value=iter([]))
        steps[3].status = Status.skipped
        steps[4].__iter__ = Mock(return_value=iter([]))
        steps[4].status = Status.undefined
        steps[4].__iter__ = Mock(return_value=iter([]))
        feature.status = Status.failed
        feature.duration = 12.3
        feature.__iter__ = Mock(return_value=iter([scenario]))
        scenario.status = Status.failed
        scenario.__iter__ = Mock(return_value=iter(steps))

        config = Mock()
        sys.stdout.encoding = "UTF-8"
        reporter = SummaryReporter(config)

        reporter.feature(feature)
        reporter.end()

        expected = {
            "all": 5,
            Status.passed.name: 2,
            Status.failed.name: 1,
            Status.skipped.name: 1,
            Status.untested.name: 0,
            Status.undefined.name: 1,
        }

        step_index = 2  # HINT: Index for steps if not rules are used.
        expected_parts = ("step", expected)
        assert format_summary.call_args_list[step_index][0] == expected_parts
