"""
Formatter(s) if BAD_STEP_DEFINITIONS are found.

BAD_STEP_DEFINITION:

* A BAD STEP-DEFINITION occurs when the regular-expression compile step fails.
* A BAD STEP-DEFINITION is detected during ``StepRegistry.add_step_definition()``.

POTENTIAL REASONS:

* Regular expression for this step is wrong/bad.
* Regular expression of a type-converter is wrong/bad (in a parse-expression)

CAUSED BY:

* More strict Regular expression checks occur in newer Python versions (>= 3.11).
"""

from __future__ import absolute_import, print_function
from behave.formatter.base import Formatter
from behave.step_registry import (
    BadStepDefinitionCollector,
    registry as the_step_registry,
)


class BadStepsFormatter(Formatter):
    """
    Formatter that prints BAD_STEP_DEFINITIONS if any exist
    at the end of the test-run.
    """
    name = "steps.bad"
    description = "Shows BAD STEP-DEFINITION(s) (if any exist)."
    PRINTER_CLASS = BadStepDefinitionCollector

    def __init__(self, stream_opener, config):
        super(BadStepsFormatter, self).__init__(stream_opener, config)
        self.step_registry = None

    @property
    def bad_step_definitions(self):
        if not self.step_registry:
            return []
        return self.step_registry.error_handler.bad_step_definitions

    def reset(self):
        self.step_registry = None

    def discover_bad_step_definitions(self):
        if self.step_registry is None:
            self.step_registry = the_step_registry

    # -- FORMATTER API:
    def feature(self, feature):
        if not self.step_registry:
            self.discover_bad_step_definitions()

    def close(self):
        """Called at end of test run."""
        if not self.step_registry:
            self.discover_bad_step_definitions()

        if self.bad_step_definitions:
            # -- ENSURE: Output stream is open.
            self.stream = self.open()
            self.report()

        # -- FINALLY:
        self.close_stream()

    # -- REPORT SPECIFIC-API:
    def make_printer(self):
        return self.PRINTER_CLASS(self.bad_step_definitions,
                                  file=self.stream)

    def report(self):
        report_printer = self.make_printer()
        report_printer.print_all()
        print(file=self.stream)

