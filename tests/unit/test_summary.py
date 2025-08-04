# -*- coding: UTF -*-
"""
Unit tests for :mod:`behave.summary` module.
"""

from __future__ import absolute_import, print_function
from behave.model_type import Status, ScenarioStatus
from behave.summary import StatusCounts, SummaryCounts, SummaryCollector
from .model_builder import FeatureBuilder, ScenarioBuilder
import pytest


# -----------------------------------------------------------------------------
# TEST SUPPORT
# -----------------------------------------------------------------------------
#     .. code-block::
#
#         builder = FeatureBuilder()
#         feature = builder.with_amount(10).passed_scenarios()
#             .and_amount(3).failed_scenarios()
#             .and_amount(5).scenarios().
#                 .each_with_steps(3)
#                 .each_with_steps(passed=3)
#
#         builder.add_scenario_template(xxx)
#             .with_steps(3)
#             .commit()
#             .add_scenarios(10
#         builder
#             .use_scenario_template().with_steps(10)
#             .add_rule()
#             .add_scenarios(10).with_status(Status.failed)
#                 .each_with_steps(3, passed=2)
#             .add_rule
#             .build()
#         builder.add_background().with_steps(10)
#             .add_scenarios(10).with_steps
#         feature = builder.add_scenario()
#             .with_steps(10, status=Status.failed)
#             .with_steps(10, passed=3)
#             .use_steps_per_scenario(4)
#             .and_amount(3).failed_scenarios()
#             .and_amount(5).scenarios().
#                 .each_with_steps(3)
#                 .each_with_steps(passed=3)


# class ScenarioStatus(object):
#     """Computes ``scenario.status`` from ``step.status``."""
#     @staticmethod
#     def from_step_status(status, dry_run=False):
#         return ScenarioStatus.compute_status_from_step_status(status,
#                                                                   dry_run=dry_run)
#         # scenario_status = status
#         # if status == Status.undefined:
#         #     scenario_status = Status.failed
#         # return scenario_status


def assert_counts_are_zero(counts, excluded=None):
    excluded = set(excluded or [])
    values = [value for status, value in counts.items()
              if status not in excluded]
    expected = [0] * len(values)
    assert values == expected


# -----------------------------------------------------------------------------
# TEST SUITE
# -----------------------------------------------------------------------------
class TestStatusCounts(object):
    def test_ctor_all_counts_are_zero(self):
        status_counts = StatusCounts()
        assert_counts_are_zero(status_counts)

    def test_from__has_counter_values(self):
        status_counts = StatusCounts.from_counts(
            passed=1, failed=2, skipped=4, untested=8)
        assert status_counts[Status.passed] == 1
        assert status_counts[Status.failed] == 2
        assert status_counts[Status.skipped] == 4
        assert status_counts[Status.untested] == 8
        assert_counts_are_zero(status_counts,
                               excluded=[Status.passed, Status.failed,
                                         Status.skipped, Status.untested])

    @pytest.mark.parametrize("status, value", [
        (Status.passed, 1),
        (Status.failed, 2),
        (Status.skipped, 3),
        (Status.untested, 4),
        (Status.undefined, 5),
    ])
    def test_from__has_one_nonzero_value(self, status, value):
        kwargs = {status.name: value}
        counts = StatusCounts.from_counts(**kwargs)
        assert counts[status] == value
        assert_counts_are_zero(counts, excluded=[status])

    @pytest.mark.parametrize("status, value", [
        (Status.passed, 1),
        (Status.failed, 2),
        (Status.skipped, 3),
        (Status.untested, 4),
        (Status.undefined, 5),
    ])
    def test_all__computes_sum_for_one_nonzero_counter(self, status, value):
        data = {status.name: value}
        counts = StatusCounts(data)
        assert counts[status] == value
        assert counts.all == value
        assert_counts_are_zero(counts, excluded=[status])

    @pytest.mark.parametrize("counts", [
        (1,  2, 3, 4),
        (10, 0, 12, 0),
        (4, 3, 10, 5),
    ])
    def test_all__computes_sum_for_many_nonzero_counters(self, counts):
        data = {
            Status.passed: counts[0],
            Status.failed: counts[1],
            Status.skipped: counts[2],
            Status.untested: counts[3],
        }
        the_counts = StatusCounts(data)
        expected = sum(counts)
        assert the_counts.all == expected


class TestSummaryCollector(object):

    def test_process_feature_with_one_passed_scenario(self):
        builder = FeatureBuilder()
        builder.add_scenario(name=u"One").with_many_steps(2, status=Status.passed)
        builder.add_many_scenarios(3, name=u"XFail").with_many_steps(4, outcomes=[
            Status.passed, Status.failed, Status.untested])
        feature = builder.feature

        summary_counts = SummaryCounts()
        collector = SummaryCollector(summary_counts)
        collector.visit_feature(feature)
        expected_feature_counts = StatusCounts.from_counts(failed=1)
        expected_scenario_counts = StatusCounts.from_counts(passed=1, failed=3)
        expected_step_counts = StatusCounts.from_counts(passed=5, failed=3, untested=6)
        print(summary_counts)
        print(expected_scenario_counts)
        print(expected_feature_counts)
        assert summary_counts.scenarios == expected_scenario_counts
        assert summary_counts.features == expected_feature_counts
        assert summary_counts.steps == expected_step_counts

    @pytest.mark.parametrize("status", StatusCounts.ORDER)
    def test_process_one_scenario(self, status):
        # status = Status.from_name(status_name)
        needs_dry_run = status in (Status.untested_pending, Status.undefined)
        steps_count = 2
        builder = ScenarioBuilder(dry_run=needs_dry_run) \
            .add_many_steps(steps_count).with_status(status)
        this_scenario = builder.scenario
        assert this_scenario.was_dry_run == needs_dry_run, "%s == needs_dry_run=%s" % (
            this_scenario.was_dry_run, needs_dry_run)
        collector = SummaryCollector()
        collector.visit(this_scenario)
        print("scenario.status: %s" % this_scenario.status)

        summary_counts = collector.summary_counts
        expected_step_counts = StatusCounts()
        expected_step_counts[status] = steps_count

        scenario_status = ScenarioStatus.from_step_status(status)
        expected_scenario_counts = StatusCounts()
        expected_scenario_counts.increment(scenario_status)
        expected_summary_counts = SummaryCounts.from_counts(
            scenarios=expected_scenario_counts,
            steps=expected_step_counts)
        print("ACTUAL:\n  %s" % summary_counts)
        print("EXPECTED SCENARIOS: %s" % expected_scenario_counts)
        print("EXPECTED STEPS:     %s" % expected_step_counts)
        assert summary_counts.steps == expected_step_counts
        assert summary_counts == expected_summary_counts
