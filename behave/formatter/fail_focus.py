"""FailFocusFormatter -- Only shows output for scenarios that have a failed step."""

from behave.formatter.base import Formatter
from behave.model_type import Status


class FailFocusFormatter(Formatter):
    """Only shows failing scenarios with error details."""

    name = "fail_focus"
    description = "Only shows failing scenarios with error details."

    def __init__(self, stream_opener, config, **kwargs):
        super(FailFocusFormatter, self).__init__(stream_opener, config)
        self.stream = self.open()
        self.current_feature = None
        self.current_scenario = None
        self.steps = []
        self._has_failure = False
        self._feature_printed = False

    def feature(self, feature):
        self.current_feature = feature
        self._feature_printed = False

    def scenario(self, scenario):
        self._flush()
        self.current_scenario = scenario
        self.steps = []
        self._has_failure = False

    def step(self, step):
        self.steps.append(step)

    def result(self, step):
        # Update the step in the buffer with its result
        for i, s in enumerate(self.steps):
            if s is step:
                self.steps[i] = step
                break

        if step.status.has_failed():
            self._has_failure = True

    def _flush(self):
        """Write buffered scenario output to stream."""
        if not self._has_failure:
            return

        feature = self.current_feature
        scenario = self.current_scenario

        if not self._feature_printed:
            self.stream.write("Feature: %s -- %s\n" % (feature.name, feature.filename))
            self.stream.write("\n")
            self._feature_printed = True

        self.stream.write("  Scenario: %s  -- %s:%s\n" % (
            scenario.name, scenario.location.filename, scenario.location.line))

        for step in self.steps:
            self.stream.write("    %s %s ... %s\n" % (
                step.keyword, step.name, step.status.name))

        # Write error messages
        for step in self.steps:
            if step.error_message:
                self.stream.write("%s\n" % step.error_message)

        self._has_failure = False
        self.steps = []

    def eof(self):
        self._flush()
        self.current_feature = None
        self.current_scenario = None
        self.steps = []

    def close(self):
        self.close_stream()
