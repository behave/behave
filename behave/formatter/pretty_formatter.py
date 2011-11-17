# -*- coding: utf8 -*-

import codecs
import sys

from behave.formatter.ansi_escapes import escapes, up
from behave.formatter.step_printer import StepPrinter

utf8writer = codecs.getwriter('utf8')

def escape_cell(cell):
    cell = cell.replace(u'\\', u'\\\\')
    cell = cell.replace(u'\n', u'\\n')
    cell = cell.replace(u'|', u'\\|')
    return cell

class MonochromeFormat(object):
    def text(self, text):
        return text

class ColorFormat(object):
    def __init__(self, status):
        self.status = status

    def text(self, text):
        if type(text) is str:
            text = text.decode('utf8')
        return escapes[self.status] + text + escapes['reset']

def get_terminal_size():
    if sys.platform == 'windows':
        # Autodetecting the size of a Windows command window is left as an
        # exercise for the reader. Prizes may be awarded for the best answer.
        return 80

    import fcntl, termios, struct
    h, w, hp, wp = struct.unpack('HHHH',
        fcntl.ioctl(0, termios.TIOCGWINSZ,
        struct.pack('HHHH', 0, 0, 0, 0)))
    return w, h

class PrettyFormatter(object):
    def __init__(self, stream, monochrome, executing):
        self.stream = utf8writer(stream)
        self.monochrome = monochrome
        self.executing = executing

        self.step_printer = StepPrinter()
        self.tag_statement = None
        self.steps = []

        self._uri = None
        self._match = None
        self.statement = None
        self.indentations = []
        self.display_width = get_terminal_size()[0]
        self.statement_lines = 0

        self.formats = None

    def uri(self, uri):
        self._uri = uri

    def feature(self, feature):
        #self.print_comments(feature.comments, '')
        self.print_tags(feature.tags, '')
        self.stream.write("%s: %s" % (feature.keyword, feature.name))
        self.stream.write(" %s# %s%s\n" % (escapes['comments'], feature.location, escapes['reset']))
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
        # self.print_step('executing', self._match.arguments,
        #                self._match.location, False)
        self.print_step('executing', [],
                        self._match.location, False)
        self.stream.flush()

    def result(self, result):
        self.stream.write(up(1 + self.statement_lines))
        arguments = []
        location = None
        if self._match:
            arguments = self._match.arguments
            location = self._match.location
        self.print_step(result.status, arguments, location, True)
        if result.error_message:
            self.stream.write(self.indent(result.error_message.strip(),
                                          '      '))
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
        self.stream.flush()

    def table(self, rows):
        cell_lengths = []
        for row in rows:
            lengths = [len(escape_cell(c)) for c in row.cells]
            cell_lengths.append(lengths)

        max_lengths = []
        for col in range(0, len(cell_lengths[0])):
            max_lengths.append(max([c[col] for c in cell_lengths]))

        for i, row in enumerate(rows):
            for comment in row.comments:
                self.stream.write('      %s\n' % comment.value)
            j = -1
            self.stream.write('      |')
            for cell, max_length in zip(row.cells, max_lengths):
                j += 1
                self.stream.write(' ')
                self.stream.write(self.color(cell, None, j))
                self.stream.write(' ' * (max_length - cell_lengths[i][j]))
                self.stream.write(' |')
            self.stream.write('\n')
        self.stream.flush()

    def doc_string(self, doc_string):
        self.stream.write('      """' + doc_string.content_type + '\n')
        doc_string = self.escape_triple_quotes(self.indent(doc_string.value,
                                                           '      '))
        self.stream.write(doc_string)
        self.stream.write('\n      """\n')
        self.stream.flush()

    def exception(self, exception):
        exception_text = HERP
        self.stream.write(self.failed(exception_text) + '\n')
        self.stream.flush()

    def color(self, cell, statuses, color):
        if statuses:
            return escapes['color'] + escapes['reset']
        else:
            return escape_cell(cell)

    def indent(self, string, indentation):
        return '\n'.join([indentation + s for s in string.split('\n')])

    def escape_triple_quotes(self, string):
        return string.replace(u'"""', u'\\"\\"\\"')

    def indented_location(self, location, proceed):
        if not location:
            return ''

        if proceed:
            indentation = self.indentations.pop(0)
        else:
            indentation = self.indentations[0]

        indentation = ' ' * indentation
        return '%s # %s' % (indentation, location)

    def calculate_location_indentations(self):
        line_widths = []
        for s in [self.statement] + self.steps:
            string = s.keyword + ' '+ s.name
            if type(string) is str:
                string = string.decode('utf8')
            line_widths.append(len(string))
        max_line_width = max(line_widths)
        self.indentations = [max_line_width - width for width in line_widths]

    def print_statement(self):
        if self.statement is None:
            return

        self.calculate_location_indentations()
        self.stream.write("\n")
        #self.print_comments(self.statement.comments, '  ')
        if hasattr(self.statement, 'tags'):
            self.print_tags(self.statement.tags, '  ')
        self.stream.write("  %s: %s " % (self.statement.keyword,
                                         self.statement.name))
        location = self.indented_location(self.statement.location, True)
        self.stream.write(self.format('comments').text(location) + "\n")
        #self.print_description(self.statement.description, '    ')
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
            if arg.offset != 0:
                text = step_name[text_start:arg.offset].encode('utf8')
                self.stream.write(text_format.text(text))
                line_length += len(text)
            self.stream.write(arg_format.text(arg.value))
            line_length += len(arg.value)
            text_start = arg.offset + len(unicode(arg.value))

        if text_start != len(step_name):
            text = step_name[text_start:].encode('utf8')
            self.stream.write(text_format.text(text))
            line_length += (len(text))

        location = self.indented_location(location, proceed)
        self.stream.write(self.format('comments').text(location) + "\n")
        line_length += len(location)

        self.statement_lines = int((line_length - 1) / self.display_width)

        if step.string:
            self.doc_string(step.string)
        if step.table:
            self.table(step.table.rows)

    def print_tags(self, tags, indent):
        if not tags:
            return

        self.stream.write(indent + ' '.join(tags) + '\n')

    def print_comments(self, comments, indent):
        if not comments:
            return

        line = indent + ('\n' + indent).join([c.value for c in comments]) + '\n'
        self.stream.write(line)

    def print_description(self, description, indent, newline=True):
        if not description:
            return

        self.stream.write(self.indent(description, indent) + '\n')
        if newline:
            self.stream.write('\n')
