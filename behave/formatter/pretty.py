# -*- coding: utf8 -*-

from __future__ import absolute_import, division
import sys
import six
from six.moves import range, zip
from behave.formatter.ansi_escapes import escapes, up
from behave.formatter.base import Formatter
from behave.model_type import Status
from behave.model_describe import escape_cell, escape_triple_quotes
from behave.textutil import indent, text as _text


# -----------------------------------------------------------------------------
# TERMINAL SUPPORT:
# -----------------------------------------------------------------------------
DEFAULT_WIDTH = 80
DEFAULT_HEIGHT = 24

def get_terminal_size():
    if sys.platform == "windows":
        # Autodetecting the size of a Windows command window is left as an
        # exercise for the reader. Prizes may be awarded for the best answer.
        return (DEFAULT_WIDTH, DEFAULT_HEIGHT)

    try:
        import fcntl
        import termios
        import struct

        zero_struct = struct.pack("HHHH", 0, 0, 0, 0)
        result = fcntl.ioctl(0, termios.TIOCGWINSZ, zero_struct)
        h, w, hp1, wp1 = struct.unpack("HHHH", result)

        return w or DEFAULT_WIDTH, h or DEFAULT_HEIGHT
    except Exception:   # pylint: disable=broad-except
        return (DEFAULT_WIDTH, DEFAULT_HEIGHT)


# -----------------------------------------------------------------------------
# COLORING SUPPORT:
# -----------------------------------------------------------------------------
class MonochromeFormat(object):
    def text(self, text):   # pylint: disable=no-self-use
        assert isinstance(text, six.text_type)
        return text

class ColorFormat(object):
    def __init__(self, status):
        self.status = status

    def text(self, text):
        assert isinstance(text, six.text_type)
        return escapes[self.status] + text + escapes["reset"]


# -----------------------------------------------------------------------------
# CLASS: PrettyFormatter
# -----------------------------------------------------------------------------
class PrettyFormatter(Formatter):
    # pylint: disable=too-many-instance-attributes
    name = "pretty"
    description = "Standard colourised pretty formatter"

    def __init__(self, stream_opener, config):
        super(PrettyFormatter, self).__init__(stream_opener, config)
        # -- ENSURE: Output stream is open.
        self.stream = self.open()
        self.colored = config.has_colored_mode(self.stream)
        self.show_source = config.show_source
        self.show_timings = config.show_timings
        self.show_multiline = config.show_multiline
        self.formats = None
        self.display_width = get_terminal_size()[0]

        # -- UNUSED: self.tag_statement = None
        self.current_feature_scenario_counts = 0
        self.current_feature = None
        self.current_rule = None
        self.current_scenario = None
        self.indentations = []
        self.statement = None
        self.steps = []
        self.step_lines = 0
        self._uri = None
        self._match = None

    @property
    def monochrome(self):
        return not self.colored

    def reset(self):
        # -- UNUSED: self.tag_statement = None
        self.current_feature_scenario_counts = 0
        self.current_feature = None
        self.current_rule = None
        self.current_scenario = None
        self.indentations = []
        self.statement = None
        self.steps = []
        self.step_lines = 0
        self._uri = None
        self._match = None

    # -- INTERFACE FOR: Formatter
    def uri(self, uri):
        self.reset()
        self._uri = uri

    def feature(self, feature):
        self._finish_current_feature()

        # -- FEATURE START:
        self.current_feature_scenario_counts = 0
        self.current_feature = feature
        self.statement = feature

        # -- PRINT FEATURE HEADER:
        # MAYBE: self.print_comments(feature.comments, '')
        prefix = ""
        self.print_tags(feature.tags, prefix)
        self.stream.write(u"%s: %s" % (feature.keyword, feature.name))
        if self.show_source:
            # pylint: disable=redefined-builtin
            this_format = self.format("comments")
            self.stream.write(this_format.text(u" # %s" % feature.location))
        self.stream.write("\n")
        self.print_description(feature.description, "  ", False)
        self.stream.flush()

    def rule(self, rule):
        self._finish_current_rule()
        # AVOID: self.replay()

        # -- START RULE:
        self.current_rule = rule
        self.statement = rule

    def background(self, background):
        self.replay()
        self.statement = background

    def scenario(self, scenario):
        self._finish_current_scenario()
        # AVOID: self.replay()

        # -- START SCENARIO:
        self.current_feature_scenario_counts += 1
        self.current_scenario = scenario
        self.statement = scenario
        # MAYBE: self.steps = []

    def step(self, step):
        self.steps.append(step)

    def match(self, match):
        self._match = match
        self.print_statement()
        self.print_step(Status.executing, self._match.arguments,
                        self._match.location, proceed=self.monochrome)
        self.stream.flush()

    def result(self, step):
        if self.colored:
            lines = self.step_lines + 1
            if self.show_multiline:
                if step.table:
                    lines += len(step.table.rows) + 1
                if step.text:
                    lines += len(step.text.splitlines()) + 2
            self.stream.write(up(lines))
            arguments = []
            location = None
            if self._match:
                arguments = self._match.arguments
                location = self._match.location
            self.print_step(step.status, arguments, location, proceed=True)

        # -- CASE: monochrome = not colored
        # HINT: print_step() already called by match() function.
        #       Step.status is not used in monochrome mode.

        if step.error_message:
            self.stream.write(indent(step.error_message.strip(), u"      "))
            self.stream.write("\n\n")
        self.stream.flush()

    def eof(self):
        # AVOID: self.replay()
        self._finish_current_feature()
        if self.current_feature_scenario_counts > 0:
            # -- ENSURE: EMPTY-LINE between two features.
            self.stream.write("\n")

        self.reset()
        self.stream.flush()

    # -- SPECIFIC PARTS:
    def _print_current_scenario_captured_output(self):
        if not self.current_scenario.captured.has_output():
            return

        output = self.current_scenario.captured.make_report()
        self.stream.write(output)
        self.stream.write(u" CAPTURED_SCENARIO_OUTPUT_END ----\n")

    def _finish_current_scenario(self):
        if self.current_scenario is None:
            return

        self.replay()  # -- REPLAY STEPS
        # -- EXCLUDE: Status.hook_error for Scenario
        # REASON: Printed in capture_output_to_sink() already.
        if self.current_scenario.status in (Status.failed, Status.error):
            self._print_current_scenario_captured_output()

        self.steps = []
        self.current_scenario = None

    def _finish_current_rule(self):
        self._finish_current_scenario()
        self.current_rule = None

    def _finish_current_feature(self):
        if self.current_feature is None:
            return

        self._finish_current_rule()
        self.current_feature = None

    def replay(self):
        self.print_statement()
        self.print_steps()
        self.stream.flush()

    def arg_format(self, key):
        return self.format(key + "_arg")

    def format(self, key):
        if not self.colored:
            if self.formats is None:
                self.formats = MonochromeFormat()
            return self.formats

        # -- OTHERWISE:
        if self.formats is None:
            self.formats = {}
        # pylint: disable=redefined-builtin
        this_format = self.formats.get(key, None)
        if this_format is not None:
            return this_format
        this_format = self.formats[key] = ColorFormat(key)
        return this_format

    def table(self, table):
        prefix = u"      "
        if self.current_rule:
            prefix += u"  "

        cell_lengths = []
        all_rows = [table.headings] + table.rows
        for row in all_rows:
            lengths = [len(escape_cell(c)) for c in row]
            cell_lengths.append(lengths)

        max_lengths = []
        for col in range(0, len(cell_lengths[0])):
            max_lengths.append(max([c[col] for c in cell_lengths]))

        for i, row in enumerate(all_rows):
            #for comment in row.comments:
            #    self.stream.write("      %s\n" % comment.value)
            self.stream.write(u"%s|" % prefix)
            for j, (cell, max_length) in enumerate(zip(row, max_lengths)):
                self.stream.write(" ")
                self.stream.write(self.color(cell, None, j))
                self.stream.write(" " * (max_length - cell_lengths[i][j]))
                self.stream.write(" |")
            self.stream.write("\n")
        self.stream.flush()

    def doc_string(self, doc_string):
        #self.stream.write('      """' + doc_string.content_type + '\n')
        doc_string = _text(doc_string)
        prefix = u"      "
        if self.current_rule:
            prefix += u"  "
        self.stream.write(u'%s"""\n' % prefix)
        doc_string = escape_triple_quotes(indent(doc_string, prefix))
        self.stream.write(doc_string)
        self.stream.write(u'\n%s"""\n' % prefix)
        self.stream.flush()

    # def doc_string(self, doc_string):
    #     from behave.model_describe import ModelDescriptor
    #     prefix = "      "
    #     text = ModelDescriptor.describe_docstring(doc_string, prefix)
    #     self.stream.write(text)
    #     self.stream.flush()

    # -- UNUSED:
    # def exception(self, exception):
    #     exception_text = _text(exception)
    #     self.stream.write(self.format("failed").text(exception_text) + "\n")
    #     self.stream.flush()

    def color(self, cell, statuses, _color):  # pylint: disable=no-self-use
        if statuses:
            return escapes["color"] + escapes["reset"]
        # -- OTHERWISE:
        return escape_cell(cell)

    def indented_text(self, text, proceed):
        if not text:
            return u""

        if proceed:
            indentation = self.indentations.pop(0)
        else:
            indentation = self.indentations[0]

        indentation = u" " * indentation
        return u"%s # %s" % (indentation, text)

    def calculate_location_indentations(self):
        line_widths = []
        for s in [self.statement] + self.steps:
            string = s.keyword + " " + s.name
            line_widths.append(len(string))
        max_line_width = max(line_widths)
        self.indentations = [max_line_width - width for width in line_widths]

    def print_statement(self):
        if self.statement is None:
            return

        prefix = u"  "
        if self.current_rule and self.statement.type != "rule":
            prefix += prefix

        self.calculate_location_indentations()
        self.stream.write(u"\n")
        #self.print_comments(self.statement.comments, "  ")
        if hasattr(self.statement, "tags"):
            self.print_tags(self.statement.tags, prefix)
        self.stream.write(u"%s%s: %s " % (prefix, self.statement.keyword,
                                          self.statement.name))

        location = self.indented_text(six.text_type(self.statement.location), True)
        if self.show_source:
            self.stream.write(self.format("comments").text(location))
        self.stream.write("\n")
        #self.print_description(self.statement.description, u"    ")
        self.statement = None

    def print_steps(self):
        while self.steps:
            self.print_step(Status.skipped, [], None, True)

    def print_step(self, status, arguments, location, proceed):
        if proceed:
            step = self.steps.pop(0)
        else:
            step = self.steps[0]
        # -- FIX: Protect against type-conversion errors/MatchWithError
        arguments = arguments or []

        text_format = self.format(status.name)
        arg_format = self.arg_format(status.name)

        prefix = u"    "
        if self.current_rule:
            prefix += u"  "
        #self.print_comments(step.comments, "    ")
        self.stream.write(prefix)
        self.stream.write(text_format.text(step.keyword + " "))
        line_length = 5 + len(step.keyword)

        step_name = six.text_type(step.name)

        text_start = 0
        for arg in arguments:
            if arg.end <= text_start:
                # -- SKIP-OVER: Optional and nested regexp args
                #    - Optional regexp args (unmatched: None).
                #    - Nested regexp args that are already processed.
                continue
                # -- VALID, MATCHED ARGUMENT:
            assert arg.original is not None
            text = step_name[text_start:arg.start]
            self.stream.write(text_format.text(text))
            line_length += len(text)
            self.stream.write(arg_format.text(arg.original))
            line_length += len(arg.original)
            text_start = arg.end

        if text_start != len(step_name):
            text = step_name[text_start:]
            self.stream.write(text_format.text(text))
            line_length += (len(text))

        if self.show_source:
            location = six.text_type(location)
            if self.show_timings and status in (Status.passed, Status.failed):
                location += " %0.3fs" % step.duration
            location = self.indented_text(location, proceed)
            self.stream.write(self.format("comments").text(location))
            line_length += len(location)
        elif self.show_timings and status in (Status.passed, Status.failed):
            timing = "%0.3fs" % step.duration
            timing = self.indented_text(timing, proceed)
            self.stream.write(self.format("comments").text(timing))
            line_length += len(timing)
        self.stream.write("\n")

        self.step_lines = int((line_length - 1) / self.display_width)

        if self.show_multiline:
            if step.text:
                self.doc_string(step.text)
            if step.table:
                self.table(step.table)

    def print_tags(self, tags, indentation):
        if not tags:
            return
        line = " ".join("@" + tag for tag in tags)
        self.stream.write(indentation + line + "\n")

    def print_comments(self, comments, indentation):
        if not comments:
            return

        self.stream.write(indent([c.value for c in comments], indentation))
        self.stream.write("\n")

    def print_description(self, description, indentation, newline=True):
        if not description:
            return

        self.stream.write(indent(description, indentation))
        if newline:
            self.stream.write("\n")
