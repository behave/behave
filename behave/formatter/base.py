class Formatter(object):
    name = None
    description = None

    def __init__(self, stream, config):
        self.stream = stream
        self.config = config

    def uri(self, uri):
        pass

    def feature(self, feature):
        pass

    def background(self, background):
        pass

    def scenario(self, scenario):
        pass

    def scenario_outline(self, outline):
        pass

    def examples(self, examples):
        pass

    def step(self, step):
        pass

    def match(self, match):
        pass

    def result(self, result):
        pass

    def eof(self):
        pass
