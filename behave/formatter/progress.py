# -*- coding: utf-8 -*-
"""
Provides 2 dotted progress formatters:

  * ScenarioProgressFormatter (scope: scenario)
  * StepProgressFormatter (scope: step)

A "dot" character that represents the result status is printed after
executing a scope item.
"""

from __future__ import absolute_import
from behave.textutil import indent
import six
from behave.formatter.base import Formatter
from behave.model_type import Status
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
        Status.hook_error: "H", # Exception/AssertionError was raised by a hook.
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
        self.current_feature_scenario_counts = 0
        self.current_rule_scenario_counts = 0
        self.show_timings = config.show_timings and self.show_timings

    def reset(self):
        self.steps = []
        self.failed_steps = []
        self.error_steps = []
        self.current_feature = None
        self.current_rule = None
        self.current_scenario = None
        self.current_feature_scenario_counts = 0
        self.current_rule_scenario_counts = 0

    # -- FORMATTER API:
    def feature(self, feature):
        self.report_current_feature_completed()

        self.current_feature = feature
        self.current_feature_scenario_counts = 0
        self.stream.write("%s  " % six.text_type(feature.filename))
        self.stream.flush()

    def rule(self, rule):
        self.report_current_rule_completed()

        self.current_rule = rule
        self.current_rule_scenario_counts = 0

    def background(self, background):
        pass

    def scenario(self, scenario):
        """
        Process the next scenario.
        But first allow to report the status on the last scenario.
        """
        self.report_current_scenario_completed()

        self.current_scenario = scenario
        self.current_feature_scenario_counts += 1
        if self.current_rule:
            self.current_rule_scenario_counts += 1

    def step(self, step):
        self.steps.append(step)

    def result(self, step):
        self.steps.pop(0)
        self.report_current_step_progress(step)

    def eof(self):
        """
        Called at end of a feature.
        It would be better to have a hook that is called after all features.
        """
        self.report_current_scenario_completed()
        self.report_current_rule_completed()
        self.report_current_feature_completed()
        self.report_current_scenario_failures()
        self.stream.flush()
        self.reset()

    def close(self):
        self.stream.write(u"\n")
        self.close_stream()


    # -- SPECIFIC PART:
    def report_current_step_progress(self, step):
        """Report the progress on the current step.
        The default implementation is empty.
        It should be overridden by a concrete class.
        """
        pass

    def report_current_scenario_progress(self):
        """Report the progress for the current/last scenario.
        The default implementation is empty.
        It should be overridden by a concrete class.
        """
        pass

    def report_current_feature_completed(self):
        """
        Hook called when a feature is completed to perform the last tasks.
        """
        self.report_current_rule_completed()
        self.current_feature = None
        self.current_feature_scenario_counts = 0

    def report_current_rule_completed(self):
        self.report_current_scenario_completed()
        self.current_rule = None
        self.current_rule_scenario_counts = 0

    def report_current_scenario_completed(self):
        """Hook called when a scenario is completed to perform the last tasks.
        """
        if not self.current_scenario:
            return

        self.report_current_scenario_progress()
        self.current_scenario = None

    def report_current_feature_duration(self):
        if self.show_timings and self.current_feature:
            self.stream.write(u"  # %.3fs" % self.current_feature.duration)
        self.stream.write("\n")

    def report_current_scenario_duration(self):
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

    def report_current_scenario_failures(self):
        self._report_problem_steps("FAILURE", self.failed_steps)
        self._report_problem_steps("ERROR", self.error_steps)


# -----------------------------------------------------------------------------
# CLASS: ScenarioProgressFormatter
# -----------------------------------------------------------------------------
class ScenarioProgressFormatter(ProgressFormatterBase):
    """
    Report dotted progress for each scenario similar to unittest.
    """
    name = "progress"
    description = "Shows dotted progress for each executed scenario."

    def report_current_scenario_progress(self):
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

    def report_current_feature_completed(self):
        if not self.current_feature:
            return

        self.report_current_rule_completed()
        self.report_current_feature_duration()
        self.current_feature = None


# -----------------------------------------------------------------------------
# CLASS: StepProgressFormatter
# -----------------------------------------------------------------------------
class StepProgressFormatter(ProgressFormatterBase):
    """
    Report dotted progress for each step similar to unittest.
    """
    name = "progress2"
    description = "Shows dotted progress for each executed step."

    def report_current_step_progress(self, step):
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

    def report_current_feature_completed(self):
        if not self.current_feature:
            return

        self.report_current_rule_completed()
        self.report_current_feature_duration()
        self.current_feature = None

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
        ASSERT FAILED: xxx
        -----------------------------------------------------------------------
    """
    name = "progress3"
    description = "Shows detailed progress for each step of a scenario."
    indent_size = 2
    scenario_prefix = " " * indent_size

    # -- FORMATTER API:
    def feature(self, feature):
        self.report_current_feature_completed()

        # -- NEW FEATURE STARTED:
        self.current_feature = feature
        self.current_feature_scenario_counts = 0
        self.stream.write(u"%s    # %s\n" % (feature.name, feature.filename))

    def rule(self, rule):
        self.report_current_rule_completed()

        # -- NEW RULE STARTED:
        self.current_rule = rule
        self.current_rule_scenario_counts = 0
        self.stream.write(u"\n  %s: %s    # %s\n" %
                          (rule.keyword, rule.name, rule.location))

    def scenario(self, scenario):
        """Process the next scenario."""
        # -- LAST SCENARIO: Report failures (if any).
        self.report_current_scenario_completed()

        # -- NEW SCENARIO STARTED:
        assert not self.failed_steps
        self.current_scenario = scenario
        self.current_feature_scenario_counts += 1
        if self.current_rule:
            self.current_rule_scenario_counts += 1
        scenario_name = scenario.name
        prefix = self.scenario_prefix
        if self.current_rule:
            prefix += u"  "
        if scenario_name:
            scenario_name += " "
        self.stream.write(u"%s%s " % (prefix, scenario_name))
        self.stream.flush()

    def eof(self):
        # -- CHAIN-OF-RESPONSIBILITY: Call base-class
        super(ScenarioStepProgressFormatter, self).eof()

        # -- SPECIFIC: For this more detailed formatter.
        if self.current_feature_scenario_counts > 0:
            # -- ENSURE: EMPTY-LINE between two features.
            self.stream.write(u"\n")

    def close(self):
        self.close_stream()

    # -- PROGRESS FORMATTER DETAILS:
    # @override
    def report_current_feature_completed(self):
        if not self.current_feature:
            return

        self.report_current_rule_completed()
        # -- SKIP: self.report_current_feature_duration()
        self.report_current_feature_captured_output()
        if self.current_feature_scenario_counts > 0:
            # -- EMPTY-LINE between 2 features.
            self.stream.write(u"\n")

        self.current_feature = None
        self.current_feature_scenario_counts = 0

    # @override
    def report_current_rule_completed(self):
        if not self.current_rule:
            return

        self.report_current_scenario_completed()
        self.report_current_rule_captured_output()
        if self.current_rule_scenario_counts == 0:
            # -- EMPTY-LINE between last scenario and next rule.
            self.stream.write(u"\n")

        self.current_rule = None
        self.current_rule_scenario_counts = 0

    def report_current_scenario_completed(self):
        if not self.current_scenario:
            return

        # -- NORMAL CASE:
        self.report_current_scenario_progress()
        self.report_current_scenario_duration()
        self.report_current_scenario_failures()
        self.report_current_scenario_captured_output()
        self.stream.flush()

        # -- RESET DATA:
        self.current_scenario = None
        self.failed_steps = []
        self.error_steps = []

    # -- SPECIFIC PARTS:
    def report_current_feature_captured_output(self):
        if (not self.current_feature
            or not self.current_feature.status.has_failed()
            or not self.current_feature.captured.has_output()):
            return

        # -- NORMAL CASE:
        captured_output = self.current_feature.captured.make_report()
        self.stream.write(captured_output)
        self.stream.write(u" CAPTURED_SCENARIO_OUTPUT_END ----\n")

    def report_current_rule_captured_output(self):
        if (not self.current_rule
            or not self.current_rule.status.has_failed()
            or not self.current_rule.captured.has_output()):
            return

        # -- NORMAL CASE:
        captured_output = self.current_rule.captured.make_report()
        self.stream.write(captured_output)
        self.stream.write(u" CAPTURED_RULE_OUTPUT_END ----\n")

    def report_current_scenario_captured_output(self):
        # -- EXCLUDE: Status.hook_error for Scenario
        # REASON: Printed in capture_output_to_sink() already.
        has_failed = self.current_scenario.status in (Status.failed, Status.error)
        if (not self.current_scenario
            or not has_failed
            or not self.current_scenario.captured.has_output()):
            return


        # -- NORMAL CASE:
        # captured_output = self.current_scenario.captured.make_report()
        template = u"""
__CAPTURED_SCENARIO_OUTPUT__________________________
{output}
__CAPTURED_SCENARIO_OUTPUT_END______________________
""".strip()
        captured_output = self.current_scenario.captured.make_report(template=template)
        self.stream.write(indent(captured_output, prefix="  "))
        self.stream.write(u"\n")

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

    def report_current_scenario_failures(self):
        self._report_problem_steps("FAILURE", self.failed_steps)
        self._report_problem_steps("ERROR", self.error_steps)
