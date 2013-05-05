# -*- coding: utf-8 -*-
"""
Provides textual descriptions for :mod:`behave.model` elements.
"""


# -----------------------------------------------------------------------------
# FUNCTIONS:
# -----------------------------------------------------------------------------
def make_indentation(indent_size, part=u" "):
    """
    Creates an indentation prefix string of the given size.
    """
    return indent_size * part


def indent(text, prefix):
    """
    Indent text or a number of text lines (with newline).

    :param lines:  Text lines to indent (as string or list of strings).
    :param prefix: Line prefix to use (as string).
    :return: Indented text (as unicode string).
    """
    lines = text
    newline = u""
    if isinstance(text, basestring):
        lines = text.splitlines(True)
    elif lines and not lines[0].endswith("\n"):
        # -- TEXT LINES: Without trailing new-line.
        newline = u"\n"
    return newline.join([prefix + unicode(line) for line in lines])


def escape_cell(cell):
    """
    Escape table cell contents.
    :param cell:  Table cell (as unicode string).
    :return: Escaped cell (as unicode string).
    """
    cell = cell.replace(u'\\', u'\\\\')
    cell = cell.replace(u'\n', u'\\n')
    cell = cell.replace(u'|', u'\\|')
    return cell


def escape_triple_quotes(text):
    """
    Escape triple-quotes, used for multi-line text/doc-strings.
    """
    return text.replace(u'"""', u'\\"\\"\\"')


def compute_words_maxsize(words):
    """
    Compute the maximum word size from a list of words (or strings).

    :param words: List of words (or strings) to use.
    :return: Maximum size of all words.
    """
    max_size = 0
    for word in words:
        if len(word) > max_size:
            max_size = len(word)
    return max_size


# -----------------------------------------------------------------------------
# CLASS:
# -----------------------------------------------------------------------------
class ModelDescriptor(object):

    @staticmethod
    def describe_table(table, indentation=None):
        """
        Provide a textual description of the table (as used w/ Gherkin).

        :param table:  Table to use (as :class:`behave.model.Table`)
        :param indentation:  Line prefix to use (as string, if any).
        :return: Textual table description (as unicode string).
        """
        # -- STEP: Determine output size of all cells.
        cell_lengths = []
        all_rows = [table.headings] + table.rows
        for row in all_rows:
            lengths = [len(escape_cell(c)) for c in row]
            cell_lengths.append(lengths)

        # -- STEP: Determine max. output size for each column.
        max_lengths = []
        for col in range(0, len(cell_lengths[0])):
            max_lengths.append(max([c[col] for c in cell_lengths]))

        # -- STEP: Build textual table description.
        lines = []
        for r, row in enumerate(all_rows):
            line = u"|"
            for c, (cell, max_length) in enumerate(zip(row, max_lengths)):
                pad_size = max_length - cell_lengths[r][c]
                line += u" %s%s |" % (escape_cell(cell), " " * pad_size)
            line += u"\n"
            lines.append(line)

        if indentation:
            return indent(lines, indentation)
        # -- OTHERWISE:
        return u"".join(lines)

    @staticmethod
    def describe_docstring(doc_string, indentation=None):
        """
        Provide a textual description of the multi-line text/triple-quoted
        doc-string (as used w/ Gherkin).

        :param doc_string:  Multi-line text to use.
        :param indentation:  Line prefix to use (as string, if any).
        :return: Textual table description (as unicode string).
        """
        text = escape_triple_quotes(doc_string)
        text = u'"""\n' + text + '\n"""\n'

        if indentation:
            text = indent(text, indentation)
        return text


class ModelPrinter(ModelDescriptor):

    def __init__(self, stream):
        super(ModelPrinter, self).__init__()
        self.stream = stream

    def print_table(self, table, indentation=None):
        self.stream.write(self.describe_table(table, indentation))
        self.stream.flush()

    def print_docstring(self, text, indentation=None):
        self.stream.write(self.describe_docstring(text, indentation))
        self.stream.flush()
