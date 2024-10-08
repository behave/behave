# -*- coding: utf-8 -*-
"""
Provides 2 dotted progress formatters:

  * ScenarioProgressFormatter (scope: scenario)
  * StepProgressFormatter (scope: step)

A "dot" character that represents the result status is printed after
executing a scope item.
"""

from __future__ import absolute_import
import six
from behave.formatter.base import Formatter
from behave.model_core import Status
from behave.textutil import text as _text


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
        Status.passed:    ".",
        Status.failed:    "F",  # AssertionError was raised: assert-failed
        Status.error:     "E",  # Exception was raised: unexpected (not assert-failed)
        Status.hook_error: "H", # Exception/AssertionError was rasied by a hook.
        Status.skipped:   "S",
        Status.untested:  "_",
        # -- STEP SPECIFIC:
        Status.untested_pending:  "p",
        Status.untested_undefined:  "u",
        Status.undefined: "U",
        Status.pending: "P",
        Status.pending_warn: "p",
    }
    show_timings = False

    def __init__(self, stream_opener, config):
        super(ProgressFormatterBase, self).__init__(stream_opener, config)
        # -- ENSURE: Output stream is open.
        self.stream = self.open()
        self.steps = []
        self.failed_steps = []
        self.error_steps = []
        self.current_feature = None
        self.current_rule = None
        self.current_scenario = None
        self.show_timings = config.show_timings and self.show_timings

    def reset(self):
        self.steps = []
        self.failed_steps = []
        self.error_steps = []
        self.current_feature = None
        self.current_rule = None
        self.current_scenario = None

    # -- FORMATTER API:
    def feature(self, feature):
        self.current_rule = None
        self.current_feature = feature
        self.stream.write("%s  " % six.text_type(feature.filename))
        self.stream.flush()

    def rule(self, rule):
        self.current_rule = rule

    def background(self, background):
        pass

    def scenario(self, scenario):
        """
        Process the next scenario.
        But first allow to report the status on the last scenario.
        """
        self.report_scenario_completed()
        self.current_scenario = scenario

    def step(self, step):
        self.steps.append(step)

    def result(self, step):
        self.steps.pop(0)
        self.report_step_progress(step)

    def eof(self):
        """
        Called at end of a feature.
        It would be better to have a hook that is called after all features.
        """
        self.report_scenario_completed()
        self.report_feature_completed()
        self.report_failures()
        self.stream.flush()
        self.reset()

    # -- SPECIFIC PART:
    def report_step_progress(self, step):
        """Report the progress on the current step.
        The default implementation is empty.
        It should be override by a concrete class.
        """
        pass

    def report_scenario_progress(self):
        """Report the progress for the current/last scenario.
        The default implementation is empty.
        It should be override by a concrete class.
        """
        pass

    def report_feature_completed(self):
        """Hook called when a feature is completed to perform the last tasks.
        """
        pass

    def report_scenario_completed(self):
        """Hook called when a scenario is completed to perform the last tasks.
        """
        self.report_scenario_progress()

    def report_feature_duration(self):
        if self.show_timings and self.current_feature:
            self.stream.write(u"  # %.3fs" % self.current_feature.duration)
        self.stream.write("\n")

    def report_scenario_duration(self):
        if self.show_timings and self.current_scenario:
            self.stream.write(u"  # %.3fs" % self.current_scenario.duration)
        self.stream.write("\n")

    def _report_problem_steps(self, problem, steps):
        if not steps:
            return

        # -- NORMAL CASE:
        separator = "-" * 80
        self.stream.write(u"%s\n" % separator)
        for step in steps:
            self.stream.write(u"%s in step '%s':\n" % (problem, step.name))
            self.stream.write(u"  Feature:  %s\n" % step.feature.name)
            self.stream.write(u"  Scenario: %s\n" % step.scenario.name)
            self.stream.write(u"%s\n" % step.error_message)
            if step.exception:
                self.stream.write(u"exception: %s\n" % step.exception)
        self.stream.write(u"%s\n" % separator)

    def report_failures(self):
        self._report_problem_steps("FAILURE", self.failed_steps)
        self._report_problem_steps("ERROR", self.error_steps)
        self.stream.flush()


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
        status = self.current_scenario.status
        dot_status_char = self.dot_status[status]
        self.stream.write(dot_status_char)
        self.stream.flush()

    def report_feature_completed(self):
        self.report_feature_duration()


# -----------------------------------------------------------------------------
# CLASS: StepProgressFormatter
# -----------------------------------------------------------------------------
class StepProgressFormatter(ProgressFormatterBase):
    """
    Report dotted progress for each step similar to unittest.
    """
    name = "progress2"
    description = "Shows dotted progress for each executed step."

    def report_step_progress(self, step):
        """Report the progress for each step."""
        dot_status_char = self.dot_status[step.status]
        if step.status.has_failed():
            step.feature = self.current_feature
            step.scenario = self.current_scenario
            if step.status.is_error():
                self.error_steps.append(step)
            else:
                self.failed_steps.append(step)
        self.stream.write(dot_status_char)
        self.stream.flush()

    def report_feature_completed(self):
        self.report_feature_duration()


# -----------------------------------------------------------------------------
# CLASS: ScenarioStepProgressFormatter
# -----------------------------------------------------------------------------
class ScenarioStepProgressFormatter(StepProgressFormatter):
    """
    Shows detailed dotted progress for both each step of a scenario.
    Differs from StepProgressFormatter by:

      * showing scenario names (as prefix scenario step progress)
      * showing failures after each scenario (if necessary)

    EXAMPLE:
        $ behave -f progress3 features
        Feature with failing scenario    # features/failing_scenario.feature
            Simple scenario with last failing step  ....F
        -----------------------------------------------------------------------
        FAILURE in step 'last step fails' (features/failing_scenario.feature:7):
        Assertion Failed: xxx
        -----------------------------------------------------------------------
    """
    name = "progress3"
    description = "Shows detailed progress for each step of a scenario."
    indent_size = 2
    scenario_prefix = " " * indent_size

    # -- FORMATTER API:
    def feature(self, feature):
        self.current_rule = None
        self.current_feature = feature
        self.stream.write(u"%s    # %s" % (feature.name, feature.filename))

    def rule(self, rule):
        self.current_rule = rule
        self.stream.write(u"\n\n  %s: %s    # %s" %
                          (rule.keyword, rule.name, rule.location))
        self.stream.flush()

    def scenario(self, scenario):
        """Process the next scenario."""
        # -- LAST SCENARIO: Report failures (if any).
        self.report_scenario_completed()

        # -- NEW SCENARIO:
        assert not self.failed_steps
        self.current_scenario = scenario
        scenario_name = scenario.name
        prefix = self.scenario_prefix
        if self.current_rule:
            prefix += u"  "
        if scenario_name:
            scenario_name += " "
        self.stream.write(u"%s%s " % (prefix, scenario_name))
        self.stream.flush()

    # -- DISABLED:
    # def eof(self):
    #     has_scenarios = self.current_feature and self.current_scenario
    #     super(ScenarioStepProgressFormatter, self).eof()
    #     if has_scenarios:
    #         # -- EMPTY-LINE between 2 features.
    #         self.stream.write("\n")

    # -- PROGRESS FORMATTER DETAILS:
    # @override
    def report_feature_completed(self):
        # -- SKIP: self.report_feature_duration()
        has_scenarios = self.current_feature and self.current_scenario
        if has_scenarios:
            # -- EMPTY-LINE between 2 features.
            self.stream.write("\n")

    def report_scenario_completed(self):
        self.report_scenario_progress()
        self.report_scenario_duration()
        self.report_failures()

        # -- RESET DATA:
        self.failed_steps = []
        self.error_steps = []

    def _report_problem_steps(self, problem, problem_steps):
        if not problem_steps:
            return

        # -- NORMAL CASE:
        separator = "-" * 80
        self.stream.write(u"%s\n" % separator)
        unicode_errors = 0
        for step in problem_steps:
            try:
                self.stream.write(u"%s in step '%s' (%s):\n" % \
                                  (problem, step.name, step.location))
                self.stream.write(u"%s\n" % step.error_message)
                self.stream.write(u"%s\n" % separator)
            except UnicodeError as e:
                self.stream.write(u"%s while reporting failure in %s\n" % \
                                  (e.__class__.__name__, step.location))
                self.stream.write(u"ERROR: %s\n" % \
                                  _text(e, encoding=self.stream.encoding))
                unicode_errors += 1

        if unicode_errors:
            msg = u"HINT: %d unicode errors occurred during failure reporting.\n"
            self.stream.write(msg % unicode_errors)

    def report_failures(self):
        self._report_problem_steps("FAILURE", self.failed_steps)
        self._report_problem_steps("ERROR", self.error_steps)
        self.stream.flush()
