# -*- coding: utf-8 -*-
"""
Provides 2 dotted progress formatters:

  * ScenarioProgressFormatter (scope: scenario)
  * StepProgressFormatter (scope: step)

A "dot" character that represents the result status is printed after
executing a scope item.
"""

from behave.formatter.base import Formatter
from behave.compat.os_path import relpath
import os

# -----------------------------------------------------------------------------
# CLASS: ProgressFormatterBase
# -----------------------------------------------------------------------------
class ProgressFormatterBase(Formatter):
    """
    Provides formatter base class for different variants of progress formatters.
    A progress formatter show an abbreviated, compact dotted progress bar,
    similar to unittest output (in terse mode).
    """
    # -- MAP: step.status to short dot_status representation.
    dot_status = {
        "passed":    ".",
        "failed":    "F",
        "error":     "E",   # Caught exception, but not an AssertionError
        "skipped":   "S",
        "untested":  "_",
        "undefined": "U",
    }

    def __init__(self, stream_opener, config):
        super(ProgressFormatterBase, self).__init__(stream_opener, config)
        # -- ENSURE: Output stream is open.
        self.stream = self.open()
        self.steps = []
        self.failures = []
        self.current_feature  = None
        self.current_scenario = None

    def reset(self):
        self.steps = []
        self.failures = []
        self.current_feature  = None
        self.current_scenario = None

    # -- FORMATTER API:
    def feature(self, feature):
        self.current_feature = feature
        short_filename = relpath(feature.filename, os.getcwd())
        self.stream.write("%s  " % short_filename)
        self.stream.flush()

    def background(self, background):
        pass

    def scenario(self, scenario):
        """
        Process the next scenario.
        But first allow to report the status on the last scenario.
        """
        self.report_scenario_progress()
        self.current_scenario = scenario

    def scenario_outline(self, outline):
        self.current_scenario = outline

    def step(self, step):
        self.steps.append(step)

    def result(self, result):
        self.steps.pop(0)
        self.report_step_progress(result)

    def eof(self):
        """
        Called at end of a feature.
        It would be better to have a hook that is called after all features.
        """
        feature = self.current_feature
        self.report_scenario_progress()
        if ( self.config.show_skipped or
            (feature and feature.status != "skipped")):
            self.stream.write('\n')
        self.report_failures()
        self.stream.flush()
        self.reset()

    # -- SPECIFIC PART:
    def report_step_progress(self, result):
        """
        Report the progress on the current step.
        The default implementation is empty.
        It should be override by a concrete class.
        """
        pass

    def report_scenario_progress(self):
        """
        Report the progress for the current/last scenario.
        The default implementation is empty.
        It should be override by a concrete class.
        """
        pass

    def report_failures(self):
        if self.failures:
            self.stream.write(u"\n{seperator}\n".format(seperator="-" * 80))
            for result in self.failures:
                self.stream.write(u"FAILURE in step '%s':\n" % result.name)
                self.stream.write(u"  Feature:  %s\n" % result.feature.name)
                self.stream.write(u"  Scenario: %s\n" % result.scenario.name)
                self.stream.write(u"%s\n" % result.error_message)
                if result.exception:
                    self.stream.write(u"exception: %s\n" % result.exception)
            self.stream.write(u"{seperator}\n".format(seperator="-" * 80))


# -----------------------------------------------------------------------------
# CLASS: ScenarioProgressFormatter
# -----------------------------------------------------------------------------
class ScenarioProgressFormatter(ProgressFormatterBase):
    """
    Report dotted progress for each scenario similar to unittest.
    """
    name = "progress"
    description = "Shows dotted progress for each executed scenario."

    def report_scenario_progress(self):
        """
        Report the progress for the current/last scenario.
        """
        if not self.current_scenario:
            return  # SKIP: No results to report for first scenario.
        # -- NORMAL-CASE:
        # XXX-JE-TODO
        status = self.current_scenario.status
        dot_status = self.dot_status[status]
        if status == "failed":
            # XXX-JE-TODO: self.failures.append(result)
            pass
        self.stream.write(dot_status)
        self.stream.flush()


# -----------------------------------------------------------------------------
# CLASS: StepProgressFormatter
# -----------------------------------------------------------------------------
class StepProgressFormatter(ProgressFormatterBase):
    """
    Report dotted progress for each step similar to unittest.
    """
    name = "progress2"
    description = "Shows dotted progress for each executed step."

    def report_step_progress(self, result):
        """
        Report the progress for each step.
        """
        dot_status = self.dot_status[result.status]
        if result.status == "failed":
            if (result.exception and
                not isinstance(result.exception, AssertionError)):
                # -- ISA-ERROR: Some Exception
                dot_status = self.dot_status["error"]
            result.feature  = self.current_feature
            result.scenario = self.current_scenario
            self.failures.append(result)
        self.stream.write(dot_status)
        self.stream.flush()
