# -*- coding: utf-8 -*-

from behave.formatter.base import Formatter


class PlainFormatter(Formatter):
    """
    Provides a simple plain formatter without coloring/formatting.
    In addition, multi-line text and tables are not shown in output (SAD).
    """
    name = 'plain'
    description = 'Very basic formatter with maximum compatibility'

    def __init__(self, stream, config):
        super(PlainFormatter, self).__init__(stream, config)
        self.steps = []
        self.show_timings = config.show_timings

    def reset_steps(self):
        self.steps = []

    def feature(self, feature):
        self.reset_steps()
        self.stream.write(u'%s: %s\n' % (feature.keyword, feature.name))

    def background(self, background):
        self.stream.write(u'%s: %s\n' % (background.keyword, background.name))

    def scenario(self, scenario):
        self.reset_steps()
        self.stream.write(u'%11s: %s\n' % (scenario.keyword, scenario.name))

    def scenario_outline(self, outline):
        self.reset_steps()
        self.stream.write(u' %s: %s\n' % (outline.keyword, outline.name))

    def step(self, step):
        self.steps.append(step)

    def result(self, result):
        step = self.steps.pop(0)
        # TODO right-align the keyword to maximum keyword width?
        self.stream.write(u'%12s %s ... ' % (step.keyword, step.name))

        status = result.status
        if self.show_timings:
            status += " in %0.2fs" % step.duration

        if result.error_message:
            self.stream.write(u'%s\n%s\n' % (status, result.error_message))
        else:
            self.stream.write(u'%s\n' % status)
