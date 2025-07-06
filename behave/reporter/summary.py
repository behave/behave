# -*- coding: UTF-8 -*-
"""
Provides a summary after each test run.
"""
# pylint: disable=consider-using-f-string, redundant-u-string-prefix, super-with-arguments

from __future__ import absolute_import, division, print_function
import sys
from time import time as time_now

from behave.model import Rule, ScenarioOutline
from behave.model_type import Status
from behave.reporter.base import Reporter
from behave.formatter.base import StreamOpener
from behave.summary import SummaryCounts, SummaryCollector, STATUS_ORDER
from behave.userdata import UserDataNamespace


# ---------------------------------------------------------------------------
# CONSTANTS:
# ---------------------------------------------------------------------------
# STATUS_ORDER_V1 = (
#     Status.passed, Status.failed, Status.error,
#     Status.skipped, Status.undefined, Status.untested
# )
OPTIONAL_STATUS_PARTS_V1 = (Status.error,
                            Status.hook_error, Status.cleanup_error,
                            # -- EXCLUDE: Status.skipped,
                            Status.pending, Status.pending_warn,
                            Status.undefined, Status.untested,
                            Status.untested_pending, Status.untested_undefined)
OPTIONAL_STATUS_PARTS_V2 = (Status.error, Status.skipped,
                            Status.hook_error, Status.cleanup_error,
                            Status.pending, Status.pending_warn,
                            Status.undefined, Status.untested,
                            Status.untested_pending, Status.untested_undefined)

OUTPUT_FORMAT_V1_SCHEMA = "{count} {statement}{suffix}, {parts}{end}"
OUTPUT_FORMAT_V2_SCHEMA = "{count} {statement}{suffix} ({parts}){end}"
OUTPUT_FORMAT_V3_SCHEMA = "{count:4} {statement:<9}{suffix} ({parts}){end}"


# ---------------------------------------------------------------------------
# UTILITY FUNCTIONS:
# ---------------------------------------------------------------------------
def pluralize(word, count=1, suffix="s"):
    if count == 1:
        return word
    # -- OTHERWISE:
    return "{0}{1}".format(word, suffix)


def number_width(value):
    """Computes width of a number."""
    text = str(value)
    return len(text)


def compute_summary_sum(summary_counts):
    """Compute sum of all summary counts (except: all)

    :param summary: Summary counts (as dict).
    :return: Sum of all counts (as integer).
    """
    counts_sum = 0
    for name, count in summary_counts.items():
        if name == "all":
            continue    # IGNORE IT.
        counts_sum += count
    return counts_sum


def format_summary_with_schema(statement_type, status_counts,
                               schema=None, item_schema=None,
                               use_passed_for_all=False,
                               end="\n"):
    """Format the summary line for one statement type.

    .. code-block::

        6 scenarios (passed: 5, failed: 1, skipped: 0, untested: 0)

    :param statement_type:
    :param status_counts:
    :return:
    """
    # -- HINT: OUTPUT_FORMAT_V2_SCHEMA = "{count} {statement} ({parts}){end}"
    if use_passed_for_all and item_schema is None:
        item_schema = "{value} {name}"
    schema = schema or OUTPUT_FORMAT_V2_SCHEMA
    item_schema = item_schema or "{name}: {value}"
    suffix = ""
    parts = []
    for status in STATUS_ORDER:
        if status.name not in status_counts:  # MAYBE: or (status not in status_counts)
            continue
        counts = status_counts.get(status.name, 0)
        if status in OPTIONAL_STATUS_PARTS_V2 and counts == 0:
            # -- SHOW-ONLY: For relevant counts, suppress: untested items, etc.
            continue
        parts.append((status.name, counts))

    if use_passed_for_all:
        counts_total = status_counts.get(Status.passed, 0)
        suffix = " passed"
    else:
        counts_total = status_counts.get("all", None)
        if counts_total is None:
            # MAYBE: compute_summary_sum
            counts_total = sum([part[1] for part in parts])

    statement = pluralize(statement_type, counts_total)
    parts_text = ", ".join([item_schema.format(name=name, value=value)
                            for name, value in parts
                            if not use_passed_for_all or (name != "passed")])
    text = schema.format(count=counts_total, statement=statement,
                         suffix=suffix, parts=parts_text, end=end)
    # print("DIAG_SUMMARY: %s" % text)
    return text

# -- DISABLED:
# def format_summary_v0(statement_type, summary):
#     parts = []
#     for status in STATUS_ORDER:
#         if status.name not in summary:
#             continue
#         counts = summary[status.name]
#         if status in OPTIONAL_STATUS_PARTS_V1 and counts == 0:
#             # -- SHOW-ONLY: For relevant counts, suppress: untested items, etc.
#             continue
#
#         if not parts:
#             # -- FIRST ITEM: Add statement_type to counter.
#             label = statement_type
#             if counts != 1:
#                 label += 's'
#             part = u"%d %s %s" % (counts, label, status.name)
#         else:
#             part = u"%d %s" % (counts, status.name)
#         parts.append(part)
#     return ", ".join(parts) + "\n"


def format_summary_v1(statement_type, summary):
    parts = []
    for status in STATUS_ORDER:
        if status.name not in summary:
            continue
        counts = summary[status.name]
        if status in OPTIONAL_STATUS_PARTS_V1 and counts == 0:
            # -- SHOW-ONLY: For relevant counts, suppress: untested items, etc.
            continue

        name = status.name
        if status.name == "passed":
            statement = pluralize(statement_type, counts)
            name = u"%s passed" % statement
        part = u"%d %s" % (counts, name)
        parts.append(part)
    return ", ".join(parts) + "\n"



def format_summary_v2(statement_type, summary):
    return format_summary_with_schema(statement_type, summary,
                                      schema=OUTPUT_FORMAT_V2_SCHEMA)


def format_summary_v3(statement_type, summary):
    return format_summary_with_schema(statement_type, summary,
                                      schema=OUTPUT_FORMAT_V3_SCHEMA)

def format_summary_v1A(statement_type, summary):
    return format_summary_with_schema(statement_type, summary,
                                      schema=OUTPUT_FORMAT_V1_SCHEMA,
                                      item_schema="{value} {name}")

def format_summary_v1B(statement_type, summary):
    return format_summary_with_schema(statement_type, summary,
                                      schema=OUTPUT_FORMAT_V1_SCHEMA,
                                      item_schema="{value} {name}",
                                      use_passed_for_all=True)

# -- DISABLED:
# def format_summary(statement_type, summary):
#     return format_summary_v2(statement_type, summary)


OUTPUT_FORMAT_DEFAULT = "v3"
OUTPUT_FORMAT_MAP = {
    "v1": format_summary_v1,
    "v2": format_summary_v2,
    "v3": format_summary_v3,
    "v1A": format_summary_v1A,
    "v1B": format_summary_v1B,
}


def select_format_summary_by_name(name):
    # func_name = "format_summary_{0}".format(name)
    # func = getattr(globals(), func_name, None)
    func = OUTPUT_FORMAT_MAP.get(name, None)
    if func is None:
        # -- UNKNOWN NAME: Use default format.
        print("UNKNOWN SUMMARY.OUTPUT_FORMAT: %s" % name)
        func = OUTPUT_FORMAT_MAP[OUTPUT_FORMAT_DEFAULT]
    return func


# ---------------------------------------------------------------------------
# REPORTERS:
# ---------------------------------------------------------------------------
class AbstractSummaryReporter(Reporter):
    userdata_scope = "behave.reporter.summary"
    show_failed_scenarios = True
    show_duration = True
    output_stream_name = "stdout"
    output_format = "v1"

    def __init__(self, config):
        super(AbstractSummaryReporter, self).__init__(config)
        stream = getattr(sys, self.output_stream_name, sys.stdout)  # WAS: sys.stderr
        self.stream = StreamOpener.ensure_stream_with_encoder(stream)
        self.output_format = self.__class__.output_format
        self.show_rules = True
        self.setup_with_userdata(config.userdata)

        # -- RELATED TO: TEST-RUN
        self._duration = None
        self.testrun_start_time = 0
        self.testrun_end_time = None
        self._failed_scenarios = []
        self._errored_scenarios = []

    @property
    def failed_scenarios(self):
        return self._failed_scenarios

    @property
    def errored_scenarios(self):
        return self._errored_scenarios

    @property
    def duration(self):
        duration = self._duration
        if duration is None:
            current_time = self.testrun_end_time or time_now()
            testrun_finished = (current_time is not None)
            duration = current_time - self.testrun_start_time
            if testrun_finished:
                self._duration = duration
        return duration

    @duration.setter
    def duration(self, value):
        # -- ONLY FOR: Test support
        self._duration = float(value)

    def setup_with_userdata(self, userdata):
        """Setup summary reporter with userdata information.
        A user can now tweak the output format of this reporter.

        EXAMPLE:
        .. code-block:: ini

            # -- FILE: behave.ini
            [behave.userdata]
            behave.reporter.summary.output_format = v1
        """
        # -- EXPERIMENTAL:
        config = UserDataNamespace(self.userdata_scope, userdata)
        output_format = config.get("output_format", self.__class__.output_format)
        if output_format == "passed_first":
            output_format = "v1"
        elif output_format == "entity_first":
            output_format = "v2"
        self.output_format = output_format

    def testrun_started(self, timestamp=None):
        if timestamp is None:
            timestamp = time_now()
        self.testrun_start_time = timestamp

    def testrun_finished(self, timestamp=None):
        if timestamp is None:
            timestamp = time_now()
        self.testrun_end_time = timestamp

    def _do_print_problematic_scenarios(self, kind, scenarios, stream=None):
        if not scenarios:
            return
        if stream is None:
            stream = self.stream

        stream.write("\n{kind} scenarios:\n".format(kind=kind))
        for scenario in scenarios:
            stream.write(u"  %s  %s\n" % (scenario.location, scenario.name))

    def print_failing_scenarios(self, stream=None):
        self._do_print_problematic_scenarios("Failing", self.failed_scenarios,
                                          stream=stream)

    def print_errored_scenarios(self, stream=None):
        self._do_print_problematic_scenarios("Errored", self.errored_scenarios,
                                          stream=stream)

    def print_problematic_scenarios(self, stream=None):
        self.print_failing_scenarios(stream=stream)
        self.print_errored_scenarios(stream=stream)

    def print_duration(self, stream=None):
        stream = stream or self.stream
        timings = (int(self.duration / 60.0), self.duration % 60)
        stream.write("Took %dmin %.3fs\n" % timings)

    # -- INTERFACE FOR: SUMMARY-REPORTER
    def on_feature(self, feature):
        raise NotImplementedError()

    def on_scenario(self, scenario):
        if scenario.status.is_failure():
            self.failed_scenarios.append(scenario)
        elif scenario.status.is_error():
            self.errored_scenarios.append(scenario)

    def print_summary(self, stream=None, with_duration=None):
        raise NotImplementedError()

    # -- REPORTER-API:
    def feature(self, feature):
        if self.testrun_start_time == 0:
            # -- DISCOVER: TEST-RUN started.
            self.testrun_started()
        self.on_feature(feature)

    def end(self):
        self.testrun_finished()

        # -- SHOW FAILED SCENARIOS (optional):
        if (self.show_failed_scenarios and
            (self.failed_scenarios or self.errored_scenarios)):
            # OLD: self.print_failing_scenarios()
            self.print_problematic_scenarios()
            self.stream.write("\n")

        # -- SHOW SUMMARY COUNTS:
        self.print_summary()


class SummaryReporterV1(AbstractSummaryReporter):
    """Old implementation of SummaryReporter."""
    output_format = "v1"

    def __init__(self, config):
        super(SummaryReporterV1, self).__init__(config)
        summary_zero_data = {
            "all": 0,
            Status.passed.name: 0,
            Status.failed.name: 0,
            Status.error.name: 0,
            Status.hook_error.name: 0,
            Status.cleanup_error.name: 0,
            Status.skipped.name: 0,
            Status.untested.name: 0
        }
        self.feature_summary = summary_zero_data.copy()
        self.rule_summary = summary_zero_data.copy()
        self.scenario_summary = summary_zero_data.copy()
        self.step_summary = {
            Status.undefined.name: 0,
            Status.untested_undefined.name: 0,
            Status.pending.name: 0,
            Status.pending_warn.name: 0,
            Status.untested_pending.name: 0,
        }
        self.step_summary.update(summary_zero_data)

    def compute_summary_sums(self):
        """(Re)Compute summary sum of all counts (except: all)."""
        summaries = [
            self.feature_summary,
            self.rule_summary,
            self.scenario_summary,
            self.step_summary
        ]
        for summary in summaries:
            summary["all"] = compute_summary_sum(summary)

    # -- INTERFACE FOR: SUMMARY-REPORTER
    def print_summary(self, stream=None, with_duration=None):
        if stream is None:
            stream = self.stream
        if with_duration is None:
            with_duration = self.show_duration

        self.compute_summary_sums()
        has_rules = (self.rule_summary["all"] > 0)
        format_summary = select_format_summary_by_name(self.output_format)

        stream.write(format_summary("feature", self.feature_summary))
        if self.show_rules and has_rules:
            # -- HINT: Show only rules, if any exists.
            self.stream.write(format_summary("rule", self.rule_summary))
        stream.write(format_summary("scenario", self.scenario_summary))
        stream.write(format_summary("step", self.step_summary))

        # -- DURATION:
        if with_duration:
            self.print_duration(stream)

    def on_feature(self, feature):
        self.process_feature(feature)

    # -- INTERNAL PROCESSING:
    def process_run_items_for(self, parent):
        for run_item in parent:
            if isinstance(run_item, Rule):
                self.process_rule(run_item)
            elif isinstance(run_item, ScenarioOutline):
                self.process_scenario_outline(run_item)
            else:
                # assert isinstance(run_item, Scenario)
                self.process_scenario(run_item)

    def process_feature(self, feature):
        self.duration += feature.duration
        self.feature_summary[feature.status.name] += 1
        self.process_run_items_for(feature)

    def process_rule(self, rule):
        self.rule_summary[rule.status.name] += 1
        self.process_run_items_for(rule)

    def process_scenario(self, scenario):
        self.on_scenario(scenario)
        # if scenario.status == Status.failed:
        #     self.failed_scenarios.append(scenario)

        self.scenario_summary[scenario.status.name] += 1
        for step in scenario:
            self.step_summary[step.status.name] += 1

    def process_scenario_outline(self, scenario_outline):
        for scenario in scenario_outline.scenarios:
            self.process_scenario(scenario)


class SummaryReporterV2(AbstractSummaryReporter):  # pylint: disable=invalid-name
    output_format = "v1B"

    def __init__(self, config):
        super(SummaryReporterV2, self).__init__(config)
        self.summary_counts = SummaryCounts()
        self.summary_collector = SummaryCollector(self.summary_counts)

    @property
    def failed_features(self):
        return self.summary_collector.failed_features

    @property
    def failed_scenarios(self):
        return self.summary_collector.failed_scenarios

    @property
    def errored_features(self):
        return self.summary_collector.errored_features

    @property
    def errored_scenarios(self):
        return self.summary_collector.errored_scenarios

    # -- INTERFACE FOR: SUMMARY-REPORTER
    def print_summary(self, stream=None, with_duration=None):
        if stream is None:
            stream = self.stream
        if with_duration is None:
            with_duration = self.show_duration

        # pylint: disable=redefined-outer-name
        # self.compute_summary_sums()
        has_rules = (self.summary_counts.rules.all > 0)
        format_summary = select_format_summary_by_name(self.output_format)

        stream.write(format_summary("feature", self.summary_counts.features))
        if self.show_rules and has_rules:
            # -- HINT: Show only rules, if any exists.
            self.stream.write(format_summary("rule", self.summary_counts.rules))
        stream.write(format_summary("scenario", self.summary_counts.scenarios))
        stream.write(format_summary("step", self.summary_counts.steps))

        has_hook_errors = (self.summary_counts.hook_errors.all > 0)
        has_hook_failed = (self.summary_counts.hook_failed.all > 0)
        if has_hook_errors:
            stream.write(format_summary("hook.errors", self.summary_counts.hook_errors))
        if has_hook_failed:
            stream.write(format_summary("hook.failed", self.summary_counts.hook_failed))

        # -- DURATION:
        if with_duration:
            self.print_duration(stream)

    def on_feature(self, feature):
        self.summary_collector.visit_feature(feature)


# -- ALIAS: Use SummaryReporterV2
SummaryReporter = SummaryReporterV1
