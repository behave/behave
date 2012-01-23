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
    def __init__(self, config):
        super(SummaryReporter, self).__init__(config)

        self.stream = self.config.output

        self.feature_summary = {'passed': 0, 'failed': 0, 'skipped': 0,
                                'untested': 0}
        self.scenario_summary = {'passed': 0, 'failed': 0, 'skipped': 0,
                                 'untested': 0}
        self.step_summary = {'passed': 0, 'failed': 0, 'skipped': 0,
                             'undefined': 0, 'untested': 0}
        self.duration = 0.0

    def feature(self, feature):
        self.feature_summary[feature.status or 'skipped'] += 1
        self.duration += feature.duration
        for scenario in feature:
            self.scenario_summary[scenario.status or 'skipped'] += 1
            for step in scenario:
                self.step_summary[step.status or 'skipped'] += 1

    def end(self):
        self.stream.write(format_summary('feature', self.feature_summary))
        self.stream.write(format_summary('scenario', self.scenario_summary))
        self.stream.write(format_summary('step', self.step_summary))
        timings = int(self.duration / 60), self.duration % 60
        self.stream.write('Took %dm%02.1fs\n' % timings)
