# -*- coding: UTF-8 -*-

from __future__ import absolute_import, print_function, division
from mock import Mock, patch
from behave.model import ScenarioOutline
from behave.model_type import Status
from behave.reporter.summary import (
    SummaryReporter, OUTPUT_FORMAT_MAP,
    format_summary_v2,
    # NOT_USED: format_summary_v0, format_summary_v1,
    # NOT_USED: format_summary_v3,
)
import pytest


class TestFormatStatus(object):
    def test_passed_entry_contains_label(self):
        format_summary = format_summary_v2
        summary = {
            Status.passed.name: 1,
            Status.skipped.name: 0,
            Status.failed.name: 0,
            Status.undefined.name: 0,
        }
        expected_prefix = "1 fnord (passed: 1"
        actual_output = format_summary("fnord", summary)
        assert actual_output.startswith(expected_prefix)

    def test_passed_entry_is_not_pluralised_in_case_of_one(self):
        passed_count = 1
        format_summary = format_summary_v2
        summary = {
            Status.passed.name: passed_count,
            Status.skipped.name: 0,
            Status.failed.name: 0,
            Status.undefined.name: 0,
        }
        expected_prefix = "{count} fnord (passed: {count}".format(count=passed_count)
        actual_output = format_summary("fnord", summary)
        assert actual_output.startswith(expected_prefix)

    @pytest.mark.parametrize("passed_count", [0, 2, 5])
    def test_passed_entry_is_pluralised(self, passed_count):
        format_summary = format_summary_v2
        summary = {
            Status.passed.name: passed_count,
            Status.skipped.name: 0,
            Status.failed.name: 0,
            Status.undefined.name: 0,
        }

        expected_prefix = "{count} fnords (passed: {count}".format(count=passed_count)
        actual_output = format_summary("fnord", summary)
        assert actual_output.startswith(expected_prefix)

    def test_remaining_fields_are_present(self):
        format_summary = format_summary_v2
        summary = {
            Status.passed.name: 10,
            Status.skipped.name: 1,
            Status.failed.name: 2,
            Status.undefined.name: 3,
        }

        output = format_summary("fnord", summary)
        assert "passed: 10" in output
        assert "skipped: 1" in output
        assert "failed: 2" in output
        assert "undefined: 3" in output

    def test_missing_fields_are_not_present(self):
        format_summary = format_summary_v2
        summary = {
            Status.passed.name: 10,
            Status.skipped.name: 1,
            Status.failed.name: 2,
        }

        output = format_summary("fnord", summary)
        assert "skipped: 1" in output
        assert "failed: 2" in output
        assert Status.undefined.name not in output


class TestSummaryReporter(object):
    OUTPUT_FORMATS = list(OUTPUT_FORMAT_MAP.keys())

    @staticmethod
    def make_many_model_mocks(count, **kwargs):
        status = kwargs.pop("status", Status.untested)
        duration = kwargs.pop("duration", 0.1)
        model_items = []
        for index in range(count):
            model_item = Mock()
            model_item.__iter__ = Mock(return_value = iter([]))
            model_item.duration = float(duration)
            model_item.status = status
            model_items.append(model_item)
        return model_items

    @classmethod
    def make_many_feature_mocks(cls, count, **kwargs):
        return cls.make_many_model_mocks(count, **kwargs)

    @classmethod
    def make_many_scenario_mocks(cls, count, **kwargs):
        return cls.make_many_model_mocks(count, **kwargs)

    @classmethod
    def make_many_step_mocks(cls, count, **kwargs):
        return cls.make_many_model_mocks(count, **kwargs)

    @staticmethod
    def make_config_mock(userdata=None, output_format=None, **kwargs):
        if userdata is None:
            userdata = {}
        if output_format:
            userdata["behave.reporter.summary.output_format"] = output_format
        return Mock(userdata=userdata, **kwargs)

    @staticmethod
    def make_format_summary_spy(output_format="v2"):
        format_summary = OUTPUT_FORMAT_MAP[output_format]
        format_summary_spy = Mock(wraps=format_summary)
        new_format_map = {"v2": format_summary_spy}
        return format_summary_spy, new_format_map

    # -- TESTSUITE:
    @patch("sys.stdout")
    def test_duration_is_totalled_up_and_outputted(self, stdout):
        features = self.make_many_feature_mocks(4, status=Status.passed)
        features[0].duration = 1.9
        features[1].duration = 2.7
        features[2].duration = 3.5
        features[3].duration = 4.3

        stdout.encoding = "UTF-8"
        config = self.make_config_mock()
        reporter = SummaryReporter(config)

        [reporter.feature(f) for f in features]
        assert round(reporter.duration, 3) == 12.400

        reporter.end()
        output = stdout.write.call_args_list[-1][0][0]
        minutes = int(reporter.duration / 60.0)
        seconds = reporter.duration % 60
        assert "%dm" % (minutes,) in output
        assert "%02.1f" % (seconds,) in output

    # @patch("sys.stdout")
    @pytest.mark.parametrize("output_format", OUTPUT_FORMATS)
    def test_feature_status_is_collected_and_reported(self, output_format):
        features = self.make_many_feature_mocks(5)
        status_values = [
            Status.passed, Status.failed, Status.skipped,
            Status.passed, Status.untested
        ]
        durations = [1.9, 2.7, 3.5, 4.3, 5.1]
        for index, feature in enumerate(features):
            feature.status = status_values[index]
            feature.duration = durations[index]

        format_summary_spy, this_map = self.make_format_summary_spy(output_format)
        with patch("behave.reporter.summary.OUTPUT_FORMAT_MAP", this_map):
            config = self.make_config_mock(output_format="v2")
            # sys.stdout.encoding = "UTF-8"
            reporter = SummaryReporter(config)

            [reporter.feature(f) for f in features]
            reporter.end()

        expected = {
            "all": 5,
            Status.passed.name: 2,
            Status.failed.name: 1,
            Status.error.name: 0,
            Status.hook_error.name: 0,
            Status.cleanup_error.name: 0,
            Status.skipped.name: 1,
            Status.untested.name: 1,
        }
        expected_parts = ("feature", expected)
        print(format_summary_spy.call_args_list)
        assert format_summary_spy.call_args_list[0][0] == expected_parts


    # @patch("sys.stdout")
    @pytest.mark.parametrize("output_format", OUTPUT_FORMATS)
    # @pytest.mark.parametrize("output_format", ["v2"])
    def test_scenario_status_is_collected_and_reported(self, output_format):  # , stdout):
        scenarios = self.make_many_scenario_mocks(5)
        scenarios[0].status = Status.failed
        scenarios[1].status = Status.failed
        scenarios[2].status = Status.skipped
        scenarios[3].status = Status.passed
        scenarios[4].status = Status.untested
        feature = Mock()
        feature.status = Status.failed
        feature.duration = 12.3
        feature.__iter__ = Mock(return_value = iter(scenarios))

        format_summary_spy, this_map = self.make_format_summary_spy(output_format)
        with patch("behave.reporter.summary.OUTPUT_FORMAT_MAP", this_map):
            config = self.make_config_mock(output_format="v2")
            # XXX stdout.encoding = "UTF-8"
            reporter = SummaryReporter(config)

            reporter.feature(feature)
            reporter.end()

        expected = {
            "all": 5,
            Status.passed.name: 1,
            Status.failed.name: 2,
            Status.skipped.name: 1,
            Status.untested.name: 1,
            Status.error.name: 0,
            Status.hook_error.name: 0,
            Status.cleanup_error.name: 0,
        }

        call_index4scenario = 1  # -- HINT: Index for scenarios if no Rules are used.
        expected_parts = ("scenario", expected)
        assert format_summary_spy.call_args_list[call_index4scenario][0] == expected_parts

    # @patch("sys.stdout")
    @pytest.mark.parametrize("output_format", OUTPUT_FORMATS)
    def test_scenario_outline_status_is_collected_and_reported(self, output_format):   # , stdout):
        scenarios = [ ScenarioOutline(u"<string>", 0, u"scenario_outline", u"name")]
        scenarios.extend(self.make_many_scenario_mocks(3))
        subscenarios = self.make_many_scenario_mocks(4)
        subscenarios[0].status = Status.passed
        subscenarios[1].status = Status.failed
        subscenarios[2].status = Status.failed
        subscenarios[3].status = Status.skipped
        scenarios[0]._scenarios = subscenarios
        scenarios[1].status = Status.failed
        scenarios[2].status = Status.skipped
        scenarios[3].status = Status.passed
        feature = Mock()
        feature.status = Status.failed
        feature.duration = 12.4
        feature.__iter__ = Mock(return_value = iter(scenarios))

        format_summary_spy, this_map = self.make_format_summary_spy(output_format)
        with patch("behave.reporter.summary.OUTPUT_FORMAT_MAP", this_map):
            config = self.make_config_mock(output_format="v2")
            # XXX sys.stdout.encoding = "UTF-8"
            reporter = SummaryReporter(config)

            reporter.feature(feature)
            reporter.end()

        expected = {
            "all": 7,
            Status.passed.name: 2,
            Status.failed.name: 3,
            Status.skipped.name: 2,
            Status.error.name: 0,
            Status.hook_error.name: 0,
            Status.cleanup_error.name: 0,
            Status.untested.name: 0,
        }
        call_index4scenario = 1  # -- HINT: Index for scenarios if no Rules are used.
        expected_parts = ("scenario", expected)
        print("format_summary_spy.call_args: %r" % format_summary_spy.call_args_list)
        assert format_summary_spy.call_args_list[call_index4scenario][0] == expected_parts

    # @patch("sys.stdout")
    @pytest.mark.parametrize("output_format", OUTPUT_FORMATS)
    def test_step_status_is_collected_and_reported(self, output_format): # XXX , stdout):
        feature = Mock()
        scenario = Mock()
        steps = self.make_many_step_mocks(5)
        steps[0].status = Status.failed
        steps[1].status = Status.passed
        steps[2].status = Status.passed
        steps[3].status = Status.skipped
        steps[4].status = Status.undefined
        feature.status = Status.failed
        feature.duration = 12.3
        feature.__iter__ = Mock(return_value = iter([scenario]))
        scenario.status = Status.failed
        scenario.__iter__ = Mock(return_value = iter(steps))

        # format_summary_spy = Mock(wraps=format_summary_v2)
        # new_format_map = {"v2": format_summary_spy}
        format_summary_spy, this_map = self.make_format_summary_spy(output_format)
        with patch("behave.reporter.summary.OUTPUT_FORMAT_MAP", this_map):
            config = self.make_config_mock(output_format="v2")
            # XXX sys.stdout.encoding = "UTF-8"
            # XXX stdout.encoding = "UTF-8"
            reporter = SummaryReporter(config)

            reporter.feature(feature)
            reporter.end()

        expected = {
            "all": 5,
            Status.passed.name: 2,
            Status.failed.name: 1,
            Status.skipped.name: 1,
            Status.undefined.name: 1,
            Status.error.name: 0,
            Status.hook_error.name: 0,
            Status.cleanup_error.name: 0,
            Status.untested.name: 0,
            Status.untested_undefined.name: 0,
            Status.untested_pending.name: 0,
            Status.pending.name: 0,
            Status.pending_warn.name: 0,
        }

        call_index4steps = 2  # HINT: Index for steps if not rules are used.
        expected_parts = ("step", expected)
        print("format_summary_spy.call_args: %r" % format_summary_spy.call_args_list)
        assert format_summary_spy.call_args_list[call_index4steps][0] == expected_parts
