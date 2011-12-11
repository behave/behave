from behave.reporter.junit import JUnitReporter
from behave.reporter.summary import SummaryReporter

def get_reporters(config):
    reporters = []

    if config.junit:
        reporters.append(JUnitReporter(config))
    if config.summary:
        reporters.append(SummaryReporter(config))

    return reporters
