import types


class TagCountFormatter(object):
    def __init__(self, formatter, tag_counts):
        self.formatter = formatter
        self.tag_counts = tag_counts

        self._uri = None
        self._feature_tags = None
        self._scenario_outline_tags = None

    def uri(self, uri):
        self._uri = uri

    def feature(self, feature):
        self._feature_tags = feature.tags
        self.formatter.feature(feature)

    def scenario(self, scenario):
        tags = set(self._feature_tags)
        tags.update(scenario.tags)
        self.record_tags(tags, scenario.line)

    def scenario_outline(self, scenario_outline):
        self._scenario_outline_tags = scenario_outline.tags
        self.formatter.scenario_outline(scenario_outline)

    def examples(self, examples):
        tags = set(self._feature_tags)
        tags.update(self._scenario_outline_tags)
        tags.update(examples.tags)
        self.record_tags(tags, examples.line)

    def record_tags(self, tags, line):
        for tag in tags:
            if tag.name not in self.tag_counts:
                self.tag_counts[tag.name] = []
            entry = "{0:s}:{1:d}".format(self._uri, line)
            self.tag_counts[tag.name].append(entry)

    def __getattr__(self, name):
        attr = getattr(self.formatter, name)
        if type(attr) is not types.MethodType:
            raise AttributeError
        return attr
