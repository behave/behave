from behave.formatter.ansi_escapes import escapes
from behave.formatter.plain import PlainFormatter
from behave.textutil import make_indentation


class PlainColorFormatter(PlainFormatter):
    """For environments with ansi color support but wihtout terminal support"""

    name = 'plain.color'

    SHOW_ALIGNED_KEYWORDS = True
    SHOW_TAGS = True

    def result(self, result):
        step = self.steps.pop(0)
        indent = make_indentation(2 * self.indent_size)

        if self.show_aligned_keywords:
            # -- RIGHT-ALIGN KEYWORDS (max. keyword width: 6):
            plain_text = u"%s%6s %s " % (indent, step.keyword, step.name)
        else:
            plain_text = u"%s%s %s " % (indent, step.keyword, step.name)

        text = escapes[result.status] + plain_text + escapes['reset']
        self.stream.write(text)

        status = result.status
        if self.show_timings:
            status += " in %0.3fs" % step.duration

        term_width = 80
        text_width = term_width - len(plain_text) - len(status) - len('... ')
        whitespace_len = max(1, text_width)
        whitespace = ' ' * whitespace_len
        self.stream.write(u"%s... %s\n" % (whitespace, status))

        if result.error_message:
            self.stream.write(u"%s\n" %result.error_message)

        if self.show_multiline:
            if step.text:
                self.doc_string(step.text)
            if step.table:
                self.table(step.table)
