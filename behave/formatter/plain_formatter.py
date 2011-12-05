
class PlainFormatter(object):
    name = 'plain'
    description = 'Very basic formatter with maximum compatibility'

    def __init__(self, stream, config):
        self.stream = stream
        self.steps = []

    def uri(self, uri):
        pass

    def feature(self, feature):
        self.stream.write(u'%s: %s\n' % (feature.keyword, feature.name))

    def background(self, background):
        self.stream.write(u'%s: %s\n' % (background.keyword, background.name))

    def scenario(self, scenario):
        self.stream.write(u'%11s: %s\n' % (scenario.keyword, scenario.name))

    def scenario_outline(self, outline):
        self.stream.write(u' %s: %s\n' % (outline.keyword, outline.name))

    def examples(self, examples):
        pass

    def step(self, step):
        self.steps.append(step)

    def match(self, match):
        pass

    def result(self, result):
        step = self.steps.pop(0)
        # TODO right-align the keyword to maximum keyword width?
        self.stream.write(u'%12s %s ... ' % (step.keyword, step.name))
        if result.error_message:
            self.stream.write(u'%s: %s\n' % (result.status, result.error_message))
        else:
            self.stream.write(u'%s\n' % result.status)

    def eof(self):
        pass

