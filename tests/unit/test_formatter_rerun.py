# -*- coding: utf-8 -*-
"""
Test behave formatters:
  * behave.formatter.rerun.RerunFormatter
"""

from __future__ import absolute_import
from behave.model_core import Status
from .test_formatter import FormatterTests as FormatterTest, _tf
from .test_formatter import MultipleFormattersTests as MultipleFormattersTest


class TestRerunFormatter(FormatterTest):
    formatter_name = "rerun"

    def test_feature_with_two_passing_scenarios(self):
        p = self._formatter(_tf(), self.config)
        f = self._feature()
        scenarios = [ self._scenario(), self._scenario() ]
        for scenario in scenarios:
            f.add_scenario(scenario)

        # -- FORMATTER CALLBACKS:
        p.feature(f)
        for scenario in f.scenarios:
            p.scenario(scenario)
            assert scenario.status == Status.passed
        p.eof()
        assert [] == p.failed_scenarios
        # -- EMIT REPORT:
        p.close()

    def test_feature_with_one_passing_one_failing_scenario(self):
        p = self._formatter(_tf(), self.config)
        f = self._feature()
        passing_scenario = self._scenario()
        failing_scenario = self._scenario()
        failing_scenario.steps.append(self._step())
        scenarios = [ passing_scenario, failing_scenario ]
        for scenario in scenarios:
            f.add_scenario(scenario)

        # -- FORMATTER CALLBACKS:
        p.feature(f)
        for scenario in f.scenarios:
            p.scenario(scenario)

        failing_scenario.steps[0].status = Status.failed
        assert scenarios[0].status == Status.passed
        assert scenarios[1].status == Status.failed
        p.eof()
        assert [ failing_scenario ] == p.failed_scenarios
        # -- EMIT REPORT:
        p.close()

    def test_feature_with_one_passing_two_failing_scenario(self):
        p = self._formatter(_tf(), self.config)
        f = self._feature()
        passing_scenario = self._scenario()
        failing_scenario1 = self._scenario()
        failing_scenario1.steps.append(self._step())
        failing_scenario2 = self._scenario()
        failing_scenario2.steps.append(self._step())
        scenarios = [ failing_scenario1, passing_scenario, failing_scenario2 ]
        for scenario in scenarios:
            f.add_scenario(scenario)

        # -- FORMATTER CALLBACKS:
        p.feature(f)
        for scenario in f.scenarios:
            p.scenario(scenario)

        failing_scenario1.steps[0].status = Status.failed
        failing_scenario2.steps[0].status = Status.failed
        assert scenarios[0].status == Status.failed
        assert scenarios[1].status == Status.passed
        assert scenarios[2].status == Status.failed
        p.eof()
        assert [ failing_scenario1, failing_scenario2 ] == p.failed_scenarios
        # -- EMIT REPORT:
        p.close()


class TestRerunAndPrettyFormatters(MultipleFormattersTest):
    formatters = ["rerun", "pretty"]


class TestRerunAndPlainFormatters(MultipleFormattersTest):
    formatters = ["rerun", "plain"]


class TestRerunAndScenarioProgressFormatters(MultipleFormattersTest):
    formatters = ["rerun", "progress"]


class TestRerunAndStepProgressFormatters(MultipleFormattersTest):
    formatters = ["rerun", "progress2"]


class TestRerunAndJsonFormatter(MultipleFormattersTest):
    formatters = ["rerun", "json"]
