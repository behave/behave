# -*- coding: utf-8 -*-
"""
Provides a formatter that provides an overview of available step definitions
(step implementations).
"""

from behave.formatter.base import Formatter
from behave.step_registry import StepRegistry, registry


# -----------------------------------------------------------------------------
# CLASS: StepsFormatter
# -----------------------------------------------------------------------------
class StepsFormatter(Formatter):
    """
    Provides formatter class that provides an overview
    which step definitions are available.

    EXAMPLE:
        behave --dry-run -f steps features/
    """
    name = "steps"
    description = "Show existing step definitions (step implementations)"
    step_types = ("given", "when", "then", "step")

    def __init__(self, stream_opener, config):
        super(StepsFormatter, self).__init__(stream_opener, config)
        self.step_registry = None
        self.current_feature = None

    def reset(self):
        self.step_registry = None
        self.current_feature = None

    def discover_step_implementations(self):
        if not self.step_registry:
            self.step_registry = StepRegistry()

        for step_type in registry.steps.keys():
            steps = tuple(registry.steps[step_type])
            self.step_registry.steps[step_type] = steps

    # -- FORMATTER API:
    def feature(self, feature):
        self.current_feature = feature
        if not self.step_registry:
            # -- ONLY-ONCE:
            self.discover_step_implementations()

    def eof(self):
        """Called at end of a feature."""
        if self.current_feature:
            # -- COLLECT STEPS FROM FEATURE:
            pass

        # -- RESET:
        self.current_feature = None
        assert self.current_feature is None

    def close(self):
        """Called at end of test run."""
        if not self.step_registry:
            self.discover_step_implementations()

        if self.step_registry:
            # -- ENSURE: Output stream is open.
            self.stream = self.open()
            self.report()

        # -- FINALLY:
        self.close_stream()

    # -- REPORT SPECIFIC-API:
    def report(self):
        self.report_steps_by_type()

    def report_steps_by_type(self):
        """
        Show an overview of the existing step implementations per step type.
        """
        for step_type in self.step_types:
            steps = list(self.step_registry.steps[step_type])
            if step_type != "step":
                steps.extend(self.step_registry.steps["step"])

            # -- PREPARE REPORT: For a step-type.
            if step_type == "step":
                step_keyword = "*"
            else:
                step_keyword = step_type.capitalize()
            if step_type == "step":
                step_type = "GENERIC"

            # -- REPORT:
            message = "%s STEPS[%s]:\n"
            self.stream.write(message % (step_type.upper(), len(steps)))
            for step in steps:
                step_pattern = u"%s %s" % (step_keyword, step.string)
                self.stream.write(u"  %s\n" % step_pattern)
            self.stream.write("\n")
