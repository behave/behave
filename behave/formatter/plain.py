from behave.formatter.base import Formatter


class PlainFormatter(Formatter):
    name = 'plain'
    description = 'Very basic formatter with maximum compatibility'

    def __init__(self, stream, config):
        super(PlainFormatter, self).__init__(stream, config)
        self.steps = []

    def feature(self, feature):
        self.stream.write(u'%s: %s\n' % (feature.keyword, feature.name))

    def background(self, background):
        self.stream.write(u'%s: %s\n' % (background.keyword, background.name))

    def scenario(self, scenario):
        self.stream.write(u'%11s: %s\n' % (scenario.keyword, scenario.name))

    def scenario_outline(self, outline):
        self.stream.write(u' %s: %s\n' % (outline.keyword, outline.name))

    def step(self, step):
        self.steps.append(step)

    def result(self, result):
        step = self.steps.pop(0)
        # TODO right-align the keyword to maximum keyword width?
        self.stream.write(u'%12s %s ... ' % (step.keyword, step.name))
        if result.error_message:
            self.stream.write(u'%s: %s\n' % (result.status, result.error_message))
        else:
            self.stream.write(u'%s\n' % result.status)
