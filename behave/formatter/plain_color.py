# -*- coding: utf-8 -*-

from behave.formatter.ansi_escapes import escapes
from behave.formatter.plain import PlainFormatter
from behave.model_core import Status
from behave.textutil import make_indentation


class PlainColorFormatter(PlainFormatter):
    """For environments with ansi color support but without terminal support

    Use case examples that support ansi colors:

       * Emacs compilation buffer.
       * Jenkins build output.
       * less -R|--RAW-CONTROL-CHARS.
    """

    name = 'plain.color'
    description = (
        'For environments with ANSI color support but without terminal support'
    )

    SHOW_ALIGNED_KEYWORDS = True
    SHOW_TAGS = True

    def __init__(self, stream_opener, config, **kwargs):
        super(PlainColorFormatter, self).__init__(
            stream_opener, config, **kwargs)
        self.step_format = u"%s%s %s "

        if self.show_aligned_keywords:
            self.step_format = u"%s%6s %s "

    def result(self, result_step):
        step = self.steps.pop(0)
        assert step == result_step
        self.print_step(result_step)

    def feature(self, feature):
        super(PlainColorFormatter, self).feature(feature)

        if feature.description:
            self.stream.write('\n')

            for line in feature.description:
                self.stream.write(make_indentation(self.indent_size))
                self.stream.write(line)
                self.stream.write('\n')

            self.stream.write('\n')

    def eof(self, *args, **kwargs):
        self.print_not_executed_steps()
        return super().eof(*args, **kwargs)

    def print_step(self, step, executed=True):
        indent = make_indentation(2 * self.indent_size)
        plain_text = self.step_format % (indent, step.keyword, step.name)

        # pretty formater prints not executed steps as skipped
        status = step.status if executed else Status.skipped
        status_text = status.name

        self.stream.write(
            escapes[status_text] + plain_text + escapes['reset']
        )

        if self.show_timings:
            if executed:
                status_text += " in %0.3fs" % step.duration
            else:
                status_text += " in -.---s"

        # creates nice indentation between end of step description and status
        whitespace_width = 80
        whitespace_width -= len(plain_text)
        whitespace_width -= len(status_text)
        whitespace_width -= len('... ')

        self.stream.write(u" " * max(1, whitespace_width))
        self.stream.write(u"... ")
        self.stream.write(status_text)
        self.stream.write('\n')

        if step.error_message:
            for line in step.error_message.split('\n'):
                self.stream.write(make_indentation(self.indent_size * 4))
                self.stream.write(line)
                self.stream.write('\n')

        if self.show_multiline:
            if step.text:
                self.doc_string(step.text)
            if step.table:
                self.table(step.table)

    def print_not_executed_steps(self):
        for step in self.steps:
            self.print_step(step, executed=False)
