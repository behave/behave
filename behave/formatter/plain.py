# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function
from contextlib import contextmanager
from behave.textutil import indent
import sys
from behave.formatter.base import Formatter
from behave.model_describe import ModelPrinter
from behave.model_type import Status
from behave.textutil import make_indentation


# -----------------------------------------------------------------------------
# UTILITY FUNCTIONS:
# -----------------------------------------------------------------------------
@contextmanager
def suppress_unicode_errors(stream=None, use_raise=False):
    if stream is None:
        stream = sys.stdout

    try:
        yield
    except UnicodeError as e:
        # unicode_errors += 1
        stream.write(u"%s while writing error message: %s\n" %
                     (e.__class__.__name__, e))
        if use_raise:
            raise


# -----------------------------------------------------------------------------
# CLASS: PlainFormatter
# -----------------------------------------------------------------------------
class PlainFormatter(Formatter):
    """
    Provides a simple plain formatter without coloring/formatting.
    The formatter displays now also:

       * multi-line text (doc-strings)
       * table
       * tags (maybe)
    """
    name = "plain"
    description = "Very basic formatter with maximum compatibility"

    SHOW_MULTI_LINE = True
    SHOW_TAGS = False
    SHOW_RULES = True
    SHOW_BACKGROUNDS = True
    SHOW_ALIGNED_KEYWORDS = False
    DEFAULT_INDENT_SIZE = 2
    RAISE_OUTPUT_ERRORS = True

    def __init__(self, stream_opener, config, **kwargs):
        super(PlainFormatter, self).__init__(stream_opener, config)
        self.steps = []
        self.show_timings = config.show_timings
        self.show_multiline = config.show_multiline and self.SHOW_MULTI_LINE
        self.show_aligned_keywords = self.SHOW_ALIGNED_KEYWORDS
        self.show_tags = self.SHOW_TAGS
        self.indent_size = self.DEFAULT_INDENT_SIZE
        self.current_feature = None
        self.current_rule = None
        self.current_scenario = None
        # -- ENSURE: Output stream is open.
        self.stream = self.open()
        self.printer = ModelPrinter(self.stream)
        # -- LAZY-EVALUATE:
        self._multiline_indentation = None

    @property
    def multiline_indentation(self):
        if self._multiline_indentation is None:
            offset = 0
            if self.show_aligned_keywords:
                offset = 2
            indentation = make_indentation(3 * self.indent_size + offset)
            self._multiline_indentation = indentation

        if self.current_rule:
            indent_extra = make_indentation(self.indent_size)
            return self._multiline_indentation + indent_extra
        return self._multiline_indentation

    def reset_steps(self):
        self.steps = []

    def write_tags(self, tags, indent=None):
        if tags and self.show_tags:
            indent = indent or ""
            text = " @".join(tags)
            self.stream.write(u"%s@%s\n" % (indent, text))

    def write_entity(self, entity, indent="", has_tags=True):
        if has_tags:
            self.write_tags(entity.tags, indent)
        text = u"%s%s: %s\n" % (indent, entity.keyword, entity.name)
        self.stream.write(text)

    # -- IMPLEMENT-INTERFACE FOR: Formatter
    def feature(self, feature):
        self._finish_current_feature()
        # AVOID: self.reset_steps()

        # -- START FEATURE:
        self.current_feature = feature
        self.write_entity(feature)

    def rule(self, rule):
        self._finish_current_rule()
        # AVOID: self.reset_steps()
        self.current_rule = rule
        indent = make_indentation(self.indent_size)
        self.stream.write(u"\n")
        self.write_entity(rule, indent)

    def background(self, background):
        self.reset_steps()
        if not self.SHOW_BACKGROUNDS:
            return

        indent_extra = 0
        if self.current_rule:
            indent_extra = self.indent_size

        indent = make_indentation(self.indent_size + indent_extra)
        self.write_entity(background, indent, has_tags=False)

    def scenario(self, scenario):
        self._finish_current_scenario()

        # -- START SCENARIO:
        self.current_scenario = scenario
        indent_extra = 0
        if self.current_rule:
            indent_extra = self.indent_size

        self.reset_steps()
        self.stream.write(u"\n")
        indent = make_indentation(self.indent_size + indent_extra)
        self.write_entity(scenario, indent)

    def step(self, step):
        self.steps.append(step)

    def result(self, step):
        """Process the result of a step (after step execution).

        :param step:   Step object with result to process.
        """
        indent_extra = 0
        if self.current_rule:
            indent_extra = self.indent_size

        step = self.steps.pop(0)
        indent = make_indentation(2 * self.indent_size + indent_extra)
        if self.show_aligned_keywords:
            # -- RIGHT-ALIGN KEYWORDS (max. keyword width: 6):
            text = u"%s%6s %s ... " % (indent, step.keyword, step.name)
        else:
            text = u"%s%s %s ... " % (indent, step.keyword, step.name)
        self.stream.write(text)

        status_text = step.status.name
        if self.show_timings:
            status_text += " in %0.3fs" % step.duration

        use_raise = self.RAISE_OUTPUT_ERRORS
        with suppress_unicode_errors(self.stream, use_raise=use_raise):
            self.stream.write(u"%s\n" % status_text)

        if self.show_multiline:
            if step.text:
                with suppress_unicode_errors(self.stream, use_raise=use_raise):
                    self.doc_string(step.text)
            if step.table:
                self.table(step.table)
        # -- MAYBE: SHOW ERROR after step
        if step.error_message:
            with suppress_unicode_errors(self.stream, use_raise=use_raise):
                self.stream.write(u"%s\n" % step.error_message)

            # -- DISABLED: Use SCENARIO_CAPTURED_OUTPUT
            # if step.captured.has_output():
            #     output = step.captured.make_report()
            #     with suppress_unicode_errors(self.stream, use_raise=use_raise):
            #         self.stream.write(output)
            #     self.stream.write(u" CAPTURED_STEP_OUTPUT_END ----\n")

    def eof(self):
        self._finish_current_feature()
        self.stream.write("\n")

    # -- MORE: Formatter helpers
    def doc_string(self, doc_string):
        self.printer.print_docstring(doc_string, self.multiline_indentation)

    def table(self, table):
        self.printer.print_table(table, self.multiline_indentation)

    # -- SPECIFIC:
    def _reporrt_current_scenario_captured_output(self):
        if not self.current_scenario.captured.has_output():
            return

        report = self.current_scenario.captured.make_report()
        self.stream.write(indent(report, prefix=""))
        self.stream.write(" CAPTURED_SCENARIO_OUTPUT_END ----\n")

    def _finish_current_scenario(self):
        if not self.current_scenario:
            return

        # -- FINISH CURRENT SCENARIO:
        if self.current_scenario.status in (Status.failed, Status.error):
            # -- EXCLUDE: Status.hook_error
            # REASON: Printed in capture_output_to_sink() already.
            self._reporrt_current_scenario_captured_output()

        self.reset_steps()
        self.current_scenario = None

    def _finish_current_rule(self):
        # -- FINISH CURRENT RULE:
        self._finish_current_scenario()
        self.current_rule = None

    def _finish_current_feature(self):
        if not self.current_feature:
            return

        self._finish_current_scenario()
        self._finish_current_rule()
        self.current_feature = None


# -----------------------------------------------------------------------------
# CLASS: Plain0Formatter
# -----------------------------------------------------------------------------
class Plain0Formatter(PlainFormatter):
    """
    Similar to old plain formatter without support for:

      * multi-line text
      * tables
      * tags
    """
    name = "plain0"
    description = "Very basic formatter with maximum compatibility"
    SHOW_MULTI_LINE = False
    SHOW_TAGS = False
    SHOW_ALIGNED_KEYWORDS = False
