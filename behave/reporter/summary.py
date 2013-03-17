import sys

from behave.model import ScenarioOutline
from behave.reporter.base import Reporter


def format_summary(statement_type, summary):
    first = True
    parts = []
    for status in ('passed', 'failed', 'skipped', 'undefined'):
        if status not in summary:
            continue
        if first:
            label = statement_type
            if summary[status] != 1:
                label += 's'
            part = '%d %s %s' % (summary[status], label, status)
            first = False
        else:
            part = '%d %s' % (summary[status], status)
        parts.append(part)
    return ', '.join(parts) + '\n'


class SummaryReporter(Reporter):
    show_failed_scenarios = True

    def __init__(self, config):
        super(SummaryReporter, self).__init__(config)

        self.stream = sys.stderr

        self.feature_summary = {'passed': 0, 'failed': 0, 'skipped': 0,
                                'untested': 0}
        self.scenario_summary = {'passed': 0, 'failed': 0, 'skipped': 0,
                                 'untested': 0}
        self.step_summary = {'passed': 0, 'failed': 0, 'skipped': 0,
                             'undefined': 0, 'untested': 0}
        self.duration = 0.0
        self.failed_scenarios = []


    def feature(self, feature):
        self.feature_summary[feature.status or 'skipped'] += 1
        self.duration += feature.duration
        for scenario in feature:
            if isinstance(scenario, ScenarioOutline):
                self.process_scenario_outline(scenario)
            else:
                self.process_scenario(scenario)

    def end(self):
        # -- SHOW FAILED SCENARIOS (optional):
        if self.show_failed_scenarios and self.failed_scenarios:
            self.stream.write("\nFailing scenarios:\n")
            for scenario in self.failed_scenarios:
                self.stream.write("  %s  %s\n" % (
                    scenario.location, scenario.name))
            self.stream.write("\n")

        # -- SHOW SUMMARY COUNTS:
        self.stream.write(format_summary('feature', self.feature_summary))
        self.stream.write(format_summary('scenario', self.scenario_summary))
        self.stream.write(format_summary('step', self.step_summary))
        timings = int(self.duration / 60), self.duration % 60
        self.stream.write('Took %dm%02.1fs\n' % timings)

    def process_scenario(self, scenario):
        if scenario.status == 'failed':
            self.failed_scenarios.append(scenario)
        self.scenario_summary[scenario.status or 'skipped'] += 1
        for step in scenario:
            self.step_summary[step.status or 'skipped'] += 1

    def process_scenario_outline(self, scenario_outline):
        for scenario in scenario_outline.scenarios:
            self.process_scenario(scenario)
