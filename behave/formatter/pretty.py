# -*- coding: utf8 -*-

from behave.formatter.ansi_escapes import escapes, up
from behave.formatter.base import Formatter
from behave.model_describe import escape_cell, escape_triple_quotes
from behave.textutil import indent
import sys


# -----------------------------------------------------------------------------
# TERMINAL SUPPORT:
# -----------------------------------------------------------------------------
DEFAULT_WIDTH = 80
DEFAULT_HEIGHT = 24

def get_terminal_size():
    if sys.platform == 'windows':
        # Autodetecting the size of a Windows command window is left as an
        # exercise for the reader. Prizes may be awarded for the best answer.
        return (DEFAULT_WIDTH, DEFAULT_HEIGHT)

    try:
        import fcntl
        import termios
        import struct

        zero_struct = struct.pack('HHHH', 0, 0, 0, 0)
        result = fcntl.ioctl(0, termios.TIOCGWINSZ, zero_struct)
        h, w, hp, wp = struct.unpack('HHHH', result)

        return w or DEFAULT_WIDTH, h or DEFAULT_HEIGHT
    except:
        return (DEFAULT_WIDTH, DEFAULT_HEIGHT)


# -----------------------------------------------------------------------------
# COLORING SUPPORT:
# -----------------------------------------------------------------------------
class MonochromeFormat(object):
    def text(self, text):
        assert isinstance(text, unicode)
        return text


class ColorFormat(object):
    def __init__(self, status):
        self.status = status

    def text(self, text):
        assert isinstance(text, unicode)
        return escapes[self.status] + text + escapes['reset']


# -----------------------------------------------------------------------------
# CLASS: PrettyFormatter
# -----------------------------------------------------------------------------
class PrettyFormatter(Formatter):
    name = 'pretty'
    description = 'Standard colourised pretty formatter'

    def __init__(self, stream_opener, config):
        super(PrettyFormatter, self).__init__(stream_opener, config)
        # -- ENSURE: Output stream is open.
        self.stream = self.open()
        isatty = getattr(self.stream, "isatty", lambda: True)
        stream_supports_colors = isatty()
        self.monochrome = not config.color or not stream_supports_colors
        self.show_source = config.show_source
        self.show_timings = config.show_timings
        self.show_multiline = config.show_multiline
        self.formats = None
        self.display_width = get_terminal_size()[0]

        # -- UNUSED: self.tag_statement = None
        self.steps = []
        self._uri = None
        self._match = None
        self.statement = None
        self.indentations = []
        self.step_lines = 0


    def reset(self):
        # -- UNUSED: self.tag_statement = None
        self.steps = []
        self._uri = None
        self._match = None
        self.statement = None
        self.indentations = []
        self.step_lines = 0

    def uri(self, uri):
        self.reset()
        self._uri = uri

    def feature(self, feature):
        #self.print_comments(feature.comments, '')
        self.print_tags(feature.tags, '')
        self.stream.write(u"%s: %s" % (feature.keyword, feature.name))
        if self.show_source:
            format = self.format('comments')
            self.stream.write(format.text(u" # %s" % feature.location))
        self.stream.write("\n")
        self.print_description(feature.description, '  ', False)
        self.stream.flush()

    def background(self, background):
        self.replay()
        self.statement = background

    def scenario(self, scenario):
        self.replay()
        self.statement = scenario

    def scenario_outline(self, scenario_outline):
        self.replay()
        self.statement = scenario_outline

    def replay(self):
        self.print_statement()
        self.print_steps()
        self.stream.flush()

    def examples(self, examples):
        self.replay()
        self.stream.write("\n")
        self.print_comments(examples.comments, '    ')
        self.print_tags(examples.tags, '    ')
        self.stream.write('    %s: %s\n' % (examples.keyword, examples.name))
        self.print_description(examples.description, '      ')
        self.table(examples.rows)
        self.stream.flush()

    def step(self, step):
        self.steps.append(step)

    def match(self, match):
        self._match = match
        self.print_statement()
        self.print_step('executing', self._match.arguments,
                        self._match.location, self.monochrome)
        self.stream.flush()

    def result(self, result):
        if not self.monochrome:
            lines = self.step_lines + 1
            if self.show_multiline:
                if result.table:
                    lines += len(result.table.rows) + 1
                if result.text:
                    lines += len(result.text.splitlines()) + 2
            self.stream.write(up(lines))
            arguments = []
            location = None
            if self._match:
                arguments = self._match.arguments
                location = self._match.location
            self.print_step(result.status, arguments, location, True)
        if result.error_message:
            self.stream.write(indent(result.error_message.strip(), u'      '))
            self.stream.write('\n\n')
        self.stream.flush()

    def arg_format(self, key):
        return self.format(key + '_arg')

    def format(self, key):
        if self.monochrome:
            if self.formats is None:
                self.formats = MonochromeFormat()
            return self.formats
        if self.formats is None:
            self.formats = {}
        format = self.formats.get(key, None)
        if format is not None:
            return format
        format = self.formats[key] = ColorFormat(key)
        return format

    def eof(self):
        self.replay()
        self.stream.write('\n')
        self.stream.flush()

    def table(self, table):
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
            #    self.stream.write('      %s\n' % comment.value)
            self.stream.write('      |')
            for j, (cell, max_length) in enumerate(zip(row, max_lengths)):
                self.stream.write(' ')
                self.stream.write(self.color(cell, None, j))
                self.stream.write(' ' * (max_length - cell_lengths[i][j]))
                self.stream.write(' |')
            self.stream.write('\n')
        self.stream.flush()

    def doc_string(self, doc_string):
        #self.stream.write('      """' + doc_string.content_type + '\n')
        prefix = '      '
        self.stream.write('%s"""\n' % prefix)
        doc_string = escape_triple_quotes(indent(doc_string, prefix))
        self.stream.write(doc_string)
        self.stream.write('\n%s"""\n' % prefix)
        self.stream.flush()

    # def doc_string(self, doc_string):
    #     from behave.model_describe import ModelDescriptor
    #     prefix = '      '
    #     text = ModelDescriptor.describe_docstring(doc_string, prefix)
    #     self.stream.write(text)
    #     self.stream.flush()

    def exception(self, exception):
        exception_text = HERP
        self.stream.write(self.failed(exception_text) + '\n')
        self.stream.flush()

    def color(self, cell, statuses, color):
        if statuses:
            return escapes['color'] + escapes['reset']
        else:
            return escape_cell(cell)

    def indented_text(self, text, proceed):
        if not text:
            return u''

        if proceed:
            indentation = self.indentations.pop(0)
        else:
            indentation = self.indentations[0]

        indentation = u' ' * indentation
        return u'%s # %s' % (indentation, text)

    def calculate_location_indentations(self):
        line_widths = []
        for s in [self.statement] + self.steps:
            string = s.keyword + ' ' + s.name
            line_widths.append(len(string))
        max_line_width = max(line_widths)
        self.indentations = [max_line_width - width for width in line_widths]

    def print_statement(self):
        if self.statement is None:
            return

        self.calculate_location_indentations()
        self.stream.write(u"\n")
        #self.print_comments(self.statement.comments, '  ')
        if hasattr(self.statement, 'tags'):
            self.print_tags(self.statement.tags, u'  ')
        self.stream.write(u"  %s: %s " % (self.statement.keyword,
                                          self.statement.name))

        location = self.indented_text(unicode(self.statement.location), True)
        if self.show_source:
            self.stream.write(self.format('comments').text(location))
        self.stream.write("\n")
        #self.print_description(self.statement.description, u'    ')
        self.statement = None

    def print_steps(self):
        while self.steps:
            self.print_step('skipped', [], None, True)

    def print_step(self, status, arguments, location, proceed):
        if proceed:
            step = self.steps.pop(0)
        else:
            step = self.steps[0]

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
            location = unicode(location)
            if self.show_timings and status in ('passed', 'failed'):
                location += ' %0.3fs' % step.duration
            location = self.indented_text(location, proceed)
            self.stream.write(self.format('comments').text(location))
            line_length += len(location)
        elif self.show_timings and status in ('passed', 'failed'):
            timing = '%0.3fs' % step.duration
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

    def print_tags(self, tags, indentation):
        if not tags:
            return
        line = ' '.join('@' + tag for tag in tags)
        self.stream.write(indentation + line + '\n')

    def print_comments(self, comments, indentation):
        if not comments:
            return

        self.stream.write(indent([c.value for c in comments], indentation))
        self.stream.write('\n')

    def print_description(self, description, indentation, newline=True):
        if not description:
            return

        self.stream.write(indent(description, indentation))
        if newline:
            self.stream.write('\n')
