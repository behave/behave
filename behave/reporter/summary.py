# -*- coding: UTF-8 -*-
"""
Provides a summary after each test run.
"""

from __future__ import absolute_import, division, print_function
import sys
from time import time as time_now
from behave.model import ScenarioOutline
from behave.model_core import Status
from behave.reporter.base import Reporter
from behave.formatter.base import StreamOpener


# -- DISABLED: optional_steps = ('untested', 'undefined')
optional_steps = (Status.untested,) # MAYBE: Status.undefined
status_order = (Status.passed, Status.failed, Status.skipped,
                Status.undefined, Status.untested)


def format_summary(statement_type, summary):
    parts = []
    for status in status_order:
        if status.name not in summary:
            continue
        counts = summary[status.name]
        if status in optional_steps and counts == 0:
            # -- SHOW-ONLY: For relevant counts, suppress: untested items, etc.
            continue

        if not parts:
            # -- FIRST ITEM: Add statement_type to counter.
            label = statement_type
            if counts != 1:
                label += 's'
            part = u"%d %s %s" % (counts, label, status.name)
        else:
            part = u"%d %s" % (counts, status.name)
        parts.append(part)
    return ", ".join(parts) + "\n"


def pluralize(word, count=1, suffix="s"):
    if count == 1:
        return word
    # -- OTHERWISE:
    return "{0}{1}".format(word, suffix)


# -- PREPARED:
def format_summary2(statement_type, summary, end="\n"):
    """Format the summary line for one statement type.

    .. code-block::

        6 scenarios (passed: 5, failed: 1, skipped: 0, untested: 0)

    :param statement_type:
    :param summary:
    :return:
    """
    parts = []
    counts_sum = 0
    for status in status_order:
        if status.name not in summary:
            continue
        counts = summary[status.name]
        if status in optional_steps and counts == 0:
            # -- SHOW-ONLY: For relevant counts, suppress: untested items, etc.
            continue

        counts_sum += counts
        parts.append((status.name, counts))

    statement = pluralize(statement_type, sum)
    parts_text = ", ".join(["{0}: {1}".format(name, value)
                            for name, value in parts])
    return "{count:4} {statement:<9} ({parts}){end}".format(
        count=counts_sum, statement=statement, parts=parts_text, end=end)


class SummaryReporter(Reporter):
    show_failed_scenarios = True
    output_stream_name = "stdout"

    def __init__(self, config):
        super(SummaryReporter, self).__init__(config)
        stream = getattr(sys, self.output_stream_name, sys.stderr)
        self.stream = StreamOpener.ensure_stream_with_encoder(stream)
        summary_zero_data = {
            Status.passed.name: 0,
            Status.failed.name: 0,
            Status.skipped.name: 0,
            Status.untested.name: 0
        }
        self.feature_summary = summary_zero_data.copy()
        self.rule_summary = summary_zero_data.copy()
        self.scenario_summary = summary_zero_data.copy()
        self.step_summary = {Status.undefined.name: 0}
        self.step_summary.update(summary_zero_data)
        self.duration = 0.0
        self.run_starttime = 0
        self.run_endtime = 0
        self.failed_scenarios = []
        self.show_rules = True

    def testrun_started(self, timestamp=None):
        if timestamp is None:
            timestamp = time_now()
        self.run_starttime = timestamp

    def testrun_finished(self, timestamp=None):
        if timestamp is None:
            timestamp = time_now()
        self.run_endtime = timestamp

    def print_failing_scenarios(self, stream=None):
        if stream is None:
            stream = self.stream

        stream.write("\nFailing scenarios:\n")
        for scenario in self.failed_scenarios:
            stream.write(u"  %s  %s\n" % (scenario.location, scenario.name))

    def print_summary(self, stream=None, with_duration=True):
        if stream is None:
            stream = self.stream

        stream.write(format_summary("feature", self.feature_summary))
        rules_summary = format_summary("rule", self.rule_summary)
        if self.show_rules and not rules_summary.strip().startswith("0"):
            # -- HINT: Show only rules, if any exists.
            self.stream.write(rules_summary)
        stream.write(format_summary("scenario", self.scenario_summary))
        stream.write(format_summary("step", self.step_summary))

        # -- DURATION:
        if with_duration:
            timings = (int(self.duration / 60.0), self.duration % 60)
            stream.write('Took %dm%02.3fs\n' % timings)

    # -- REPORTER-API:
    def feature(self, feature):
        if self.run_starttime == 0:
            # -- DISCOVER: TEST-RUN started.
            self.testrun_started()

        self.feature_summary[feature.status.name] += 1
        self.duration += feature.duration
        for scenario in feature:
            if isinstance(scenario, ScenarioOutline):
                self.process_scenario_outline(scenario)
            else:
                self.process_scenario(scenario)

    def end(self):
        self.testrun_finished()

        # -- SHOW FAILED SCENARIOS (optional):
        if self.show_failed_scenarios and self.failed_scenarios:
            self.print_failing_scenarios()
            self.stream.write("\n")

        # -- SHOW SUMMARY COUNTS:
        self.print_summary()

    def process_scenario(self, scenario):
        if scenario.status == Status.failed:
            self.failed_scenarios.append(scenario)

        self.scenario_summary[scenario.status.name] += 1
        for step in scenario:
            self.step_summary[step.status.name] += 1

    def process_scenario_outline(self, scenario_outline):
        for scenario in scenario_outline.scenarios:
            self.process_scenario(scenario)
