# -*- coding: utf-8 -*-
# pylint: disable=C0111,W0511
#   C0111   missing docstrings
"""
XXX UNDER-CONSTRUCTION
"""

from behave.formatter import pretty
from behave.formatter import ansi_escapes


# -----------------------------------------------------------------------------
# CLASS: Pretty1Formatter
# -----------------------------------------------------------------------------
class Pretty1Formatter(pretty.PrettyFormatter):
    """
    Provides a pretty formatter class without using cursor-ups.

    The normal pretty formatter prints the the currently executed step
    and then executes the current step. After step execution, the step result
    is known. Therefore, it repositions the cursor with ANSI cursor-ups
    and overwrites the current step with the step result color (green/red).
    This behaviour is useful when step execution takes long(er).
    The user knows which step is currently executed before the result is known.


    """
    name = "pretty1"

    def __init__(self, stream, config):
        super(Pretty1Formatter, self).__init__(stream, config)
        self.colored = config.color
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
    def uri(self, uri):
        self._uri = uri

    def feature(self, feature):
        self.current_feature = feature
        self.print_feature(feature)

    def background(self, background):
        self.statement = background
        pass

    def scenario(self, scenario):
        """
        Process the next scenario.
        But first allow to report the status on the last scenario.
        """
        self.finish_last_scenario()
        self.current_scenario = scenario
        self.statement = scenario
        self.print_scenario(scenario)

    def scenario_outline(self, scenario_outline):
        self.finish_last_scenario()
        self.current_scenario = scenario_outline
        self.statement = scenario_outline

    def step(self, step):
        self.steps.append(step)

    def match(self, match):
        self._match = match
        # XXX self.print_statement()
        # XXX self.print_step('executing', self._match.arguments,
        # XXX     self._match.location, self.monochrome)
        self.stream.flush()

    def result(self, result):
        step = self.steps.pop(0)
        # XXX print "XXX result=%s: %s" % (result.status, step)
        self.print_step_with_status(step, result.status)
        if result.error_message:
            self.stream.write(
                self.indent(result.error_message.strip(), u'      '))
            self.stream.write('\n\n')
        self.stream.flush()

    def eof(self):
        """
        Called at end of a feature.
        It would be better to have a hook that is called after all features.
        """
        self.finish_last_scenario()
        self.report_failures()
        self.reset()

    # -- SPECIFIC PART:
#    def replay(self):
#        assert False
#        # self.print_statement()
#        # self.print_steps()
#        self.stream.flush()

    def finish_last_scenario(self):
        # XXX assert self.steps
        self.current_scenario = None
        self.steps = []

    def print_tags(self, tags, indent):
        if not tags:
            return
        self.stream.write(indent + ' '.join('@' + tag for tag in tags) + '\n')

    def print_feature(self, feature):
        self.print_tags(feature.tags, '')
        self.stream.write(u"%s: %s" % (feature.keyword, feature.name))
        if self.show_source:
            format_ = self.format('comments')
            self.stream.write(format_.text(u" # %s" % feature.location))
        self.stream.write("\n")
        self.print_description(feature.description, '  ', False)
        self.stream.flush()

    def print_scenario(self, scenario):
        self.statement = scenario
        current_steps = self.steps
        self.steps = list(scenario.steps)
        self.calculate_location_indentations()
        self.steps = current_steps
        self.stream.write(u"\n")
        #self.print_comments(self.statement.comments, '  ')
        if hasattr(self.statement, 'tags'):
            self.print_tags(self.statement.tags, u'  ')
        self.stream.write(u"  %s: %s " % (self.statement.keyword,
                                          self.statement.name))

        location = self.indented_text(self.statement.location, True)
        if self.show_source:
            self.stream.write(self.format('comments').text(location))
        self.stream.write("\n")
        #self.print_description(self.statement.description, u'    ')
        self.statement = None

    def __override_and_disable(self):
        pass

    def print_step(self, status, arguments, location, proceed):
        assert False
        self.__override_and_disable()

    def print_step_with_status(self, step, status):
        proceed = True
        arguments = []
        location = ''  # XXX-WAS: None
        if self._match:
            arguments = self._match.arguments
            location = self._match.location

        text_format = self.format(status)
        arg_format = self.arg_format(status)

        #self.print_comments(step.comments, '    ')
        self.stream.write('    ')
        self.stream.write(text_format.text(step.keyword + ' '))
        line_length = 5 + len(step.keyword)

        step_name = unicode(step.name)

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
            if self.show_timings and status in ('passed', 'failed'):
                assert isinstance(location, str)
                location += ' %0.2fs' % step.duration
            location = self.indented_text(location, proceed)
            self.stream.write(self.format('comments').text(location))
            line_length += len(location)
        elif self.show_timings and status in ('passed', 'failed'):
            timing = '%0.2fs' % step.duration
            timing = self.indented_text(timing, proceed)
            self.stream.write(self.format('comments').text(timing))
            line_length += len(timing)
        self.stream.write("\n")

        self.step_lines = int((line_length - 1) / self.display_width)

        if self.show_multiline:
            if step.text:
                self.doc_string(step.text)
            if step.table:
                self.table(step.table)

    def print_table(self, table):
        cell_lengths = []
        all_rows = [table.headings] + table.rows
        for row in all_rows:
            lengths = [len(pretty.escape_cell(c)) for c in row]
            cell_lengths.append(lengths)

        max_lengths = []
        for col in range(0, len(cell_lengths[0])):
            max_lengths.append(max([c[col] for c in cell_lengths]))

        for i, row in enumerate(all_rows):
            #for comment in row.comments:
            #    self.stream.write('      %s\n' % comment.value)
            self.stream.write('      |')
            for j, (cell, max_length) in enumerate(zip(row, max_lengths)):
                self.stream.write(' ')
                self.stream.write(self.color(cell, None, j))
                self.stream.write(' ' * (max_length - cell_lengths[i][j]))
                self.stream.write(' |')
            self.stream.write('\n')
        self.stream.flush()

    def print_multiline_text(self, text):
        self.stream.write('      """\n')
        text = self.escape_triple_quotes(self.indent(text, '      '))
        self.stream.write(text)
        self.stream.write('\n      """\n')
        self.stream.flush()

    def print_error(self, error_message):
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
# CLASS: SimplePrettyFormatter
# -----------------------------------------------------------------------------
# from behave.formatter import ansi_escapes
#class SimplePrettyFormatter(PrettyFormatter):
#    def __init__(self, stream, config):
#        super(SimplePrettyFormatter, self).__init__(stream, config)
#        self.colored = config.color
#        # -- DISABLE: Nice coloring with cursor-up usage.
#        # Enforce monochrome mode to avoid cursor-ups.
#        self.monochrome = True
#
#        self.show_source = config.show_source
#        self.show_timings = config.show_timings
#        self.show_multiline = config.show_multiline
#
#        self.tag_statement = None
#        self.steps = []
#
#        self._uri = None
#        self._match = None
#        self.statement = None
#        self.indentations = []
#        self.step_lines = 0
#        self.formats = None
#
#        if self.colored:
#            self.init_formats()
#
#    def init_formats(self):
#        self.formats = {}
#        # XXX for color, color_escape in ansi_escapes.colors.items():
#        # XXX   self.formats[color] = ColorFormat(color)
#        for style in ansi_escapes.aliases.keys():
#            # print "XXX-FORMAT: %s" % style
#            arg_style = style + "_arg"
#            self.formats[style] = ColorFormat(style)
#            self.formats[arg_style] = ColorFormat(arg_style)
#
#    def format(self, key):
#        if not self.colored:
#            # -- MONOCHROME: Enforce init once.
#            return super(SimplePrettyFormatter, self).format(key)
#        # -- CASE COLORED:
#        return self.formats[key]
#
#    def print_steps(self):
#        while self.steps:
#            self.print_step('skipped', [], None, True)
#
#    def print_step(self, status, arguments, location, proceed):
#        if proceed:
#            step = self.steps.pop(0)
#        else:
#            step = self.steps[0]
#
#        text_format = self.format(status)
#        arg_format = self.arg_format(status)
#
#        #self.print_comments(step.comments, '    ')
#        self.stream.write('    ')
#        self.stream.write(text_format.text(step.keyword + ' '))
#        line_length = 5 + len(step.keyword)
#
#        step_name = unicode(step.name)
#
#        text_start = 0
#        for arg in arguments:
#            text = step_name[text_start:arg.start]
#            self.stream.write(text_format.text(text))
#            line_length += len(text)
#            if arg.end <= text_start:
#                # -- SKIP-OVER: Optional and nested regexp args
#                #    - Optional regexp args (None).
#                #    - Nested regexp args that are already processed.
#                continue
#            assert arg.original is not None
#            self.stream.write(arg_format.text(arg.original))
#            line_length += len(arg.original)
#            text_start = arg.end
#
#        if text_start != len(step_name):
#            text = step_name[text_start:]
#            self.stream.write(text_format.text(text))
#            line_length += (len(text))
#
#        if self.show_source:
#            if self.show_timings and status in ('passed', 'failed'):
#                assert isinstance(location, str)
#                location += ' %0.2fs' % step.duration
#            location = self.indented_text(location, proceed)
#            self.stream.write(self.format('comments').text(location))
#            line_length += len(location)
#        elif self.show_timings and status in ('passed', 'failed'):
#            timing = '%0.2fs' % step.duration
#            timing = self.indented_text(timing, proceed)
#            self.stream.write(self.format('comments').text(timing))
#            line_length += len(timing)
#        self.stream.write("\n")
#
#        self.step_lines = int((line_length - 1) / self.display_width)
#
#        if self.show_multiline:
#            if step.text:
#                self.doc_string(step.text)
#            if step.table:
#                self.table(step.table)
#
#    def result(self, result):
#        if self.colored:
#            # XXX-REWIND-UP self.stream.write(up(lines))
#            arguments = []
#            location = ''  # XXX-WAS: None
#            if self._match:
#                arguments = self._match.arguments
#                location = self._match.location
#            self.print_step(result.status, arguments, location, True)
#            if self.show_multiline:
#                if result.table:
#                    self.print_table(result.table)
#                if result.text:
#                    self.print_multiline_text(result.text)
#        if result.error_message:
#            self.stream.write(self.indent(result.error_message.strip(),
#                u'      '))
#            self.stream.write('\n\n')
#        self.stream.flush()
#
#    def __SKIP_uri(self, uri):
#        self._uri = uri
#
#    def __SKIP_feature(self, feature):
#        pass
#
#    def background(self, background):
#        self.replay()
#        self.statement = background
#
#    def scenario(self, scenario):
#        self.replay()
#        self.statement = scenario
#
#    def scenario_outline(self, scenario_outline):
#        self.replay()
#        self.statement = scenario_outline
#
#    def examples(self, examples):
#        pass
#
#    def step(self, step):
#        self.steps.append(step)
#
#    def match(self, match):
#        self._match = match
#        # XXX self.print_statement()
#        # XXX self.print_step('executing', self._match.arguments,
#        # XXX    self._match.location, self.monochrome)
#        self.stream.flush()
#
#    def print_table(self, table):
#        cell_lengths = []
#        all_rows = [table.headings] + table.rows
#        for row in all_rows:
#            lengths = [len(escape_cell(c)) for c in row]
#            cell_lengths.append(lengths)
#
#        max_lengths = []
#        for col in range(0, len(cell_lengths[0])):
#            max_lengths.append(max([c[col] for c in cell_lengths]))
#
#        for i, row in enumerate(all_rows):
#            #for comment in row.comments:
#            #    self.stream.write('      %s\n' % comment.value)
#            self.stream.write('      |')
#            for j, (cell, max_length) in enumerate(zip(row, max_lengths)):
#                self.stream.write(' ')
#                self.stream.write(self.color(cell, None, j))
#                self.stream.write(' ' * (max_length - cell_lengths[i][j]))
#                self.stream.write(' |')
#            self.stream.write('\n')
#        self.stream.flush()
#
#    def print_multiline_text(self, text):
#        #self.stream.write('      """' + doc_string.content_type + '\n')
#        self.stream.write('      """\n')
#        doc_string = self.escape_triple_quotes(self.indent(doc_string,
#            '      '))
#        self.stream.write(doc_string)
#        self.stream.write('\n      """\n')
#        self.stream.flush()
#
#    def result(self, result):
#        pass
# -----------------------------------------------------------------------------
# CLASS: SimplePrettyFormatter
# -----------------------------------------------------------------------------
class SimplePrettyFormatter(pretty.PrettyFormatter):
    """
    Provides a pretty formatter class without using cursor-ups.
    """
    name = "pretty2"

    def __init__(self, stream, config):
        super(SimplePrettyFormatter, self).__init__(stream, config)
        self.colored = config.color
        # -- DISABLE: Nice coloring with cursor-up usage.
        # Enforce monochrome mode to avoid cursor-ups.
        self.monochrome = True
        self.formats = None

        if self.colored:
            self.init_formats()

    def init_formats(self):
        self.formats = {}
        for style in ansi_escapes.aliases.keys():
            # print "XXX-FORMAT: %s" % style
            arg_style = style + "_arg"
            self.formats[style] = pretty.ColorFormat(style)
            self.formats[arg_style] = pretty.ColorFormat(arg_style)

    def format(self, key):
        if not self.colored:
            # -- MONOCHROME: Enforce init once.
            return super(SimplePrettyFormatter, self).format(key)
        # -- CASE COLORED:
        return self.formats[key]

    def match(self, match):
        """
        Overridden from base class to avoid prelimary step-printing
        before step is executed.
        """
        self._match = match

    def result(self, result):
        """
        Overridden from base class to avoid cursor-ups.
        Called when step result is known.
        """
        arguments = []
        location = ''  # XXX-WAS: None
        if self._match:
            arguments = self._match.arguments
            location = self._match.location
        self.print_step(result.status, arguments, location, True)
        if result.error_message:
            self.stream.write(self.indent(result.error_message.strip(),
                u'      '))
            self.stream.write('\n\n')
        self.stream.flush()

# -----------------------------------------------------------------------------
# CLASS: Pretty1AsPrettyFormatter
# -----------------------------------------------------------------------------
class Pretty1AsPrettyFormatter(Pretty1Formatter):
    """
    Helper class to be able to register Pretty1Formatter as PrettyFormatter.
    """
    name = pretty.PrettyFormatter.name

class SimplePrettyAsPrettyFormatter(SimplePrettyFormatter):
    """
    Helper class to be able to register Pretty1Formatter as PrettyFormatter.
    """
    name = pretty.PrettyFormatter.name

