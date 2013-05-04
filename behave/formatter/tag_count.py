# -*- coding: utf-8 -*-
"""
Collects data how often a tag count is used and where.

EXAMPLE:

    $ behave --dry-run -f tag_counts features/
"""

from behave.formatter.base import Formatter


class AbstractTagCountFormatter(Formatter):
    with_tag_inheritance = False

    def __init__(self, stream_opener, config):
        super(AbstractTagCountFormatter, self).__init__(stream_opener, config)
        self.tag_counts = {}
        self._uri = None
        self._feature_tags = None
        self._scenario_outline_tags = None

    # -- Formatter API:
    def uri(self, uri):
        self._uri = uri

    def feature(self, feature):
        self._feature_tags = feature.tags
        self.record_tags(feature.tags, feature.location)

    def scenario(self, scenario):
        tags = set(scenario.tags)
        if self.with_tag_inheritance:
            tags.update(self._feature_tags)
        self.record_tags(tags, scenario.location)

    def scenario_outline(self, scenario_outline):
        self._scenario_outline_tags = scenario_outline.tags
        self.record_tags(scenario_outline.tags, scenario_outline.location)

    def examples(self, examples):
        tags = set(examples.tags)
        if self.with_tag_inheritance:
            tags.update(self._scenario_outline_tags)
            tags.update(self._feature_tags)
        self.record_tags(tags, examples.location)

    def close(self):
        """Emit tag count reports."""
        # -- ENSURE: Output stream is open.
        self.stream = self.open()
        self.report_tags()
        self.close_stream()

    # -- SPECIFIC API:
    def record_tags(self, tags, location):
        for tag in tags:
            if tag not in self.tag_counts:
                self.tag_counts[tag] = []
            self.tag_counts[tag].append(location)

    def report_tags(self):
        raise NotImplementedError



class TagCountFormatter(AbstractTagCountFormatter):
    name = "tag_count"
    description = "Collects data how often a tag is used."
    with_tag_inheritance = False

    def report_tags(self):
        self.report_tag_counts()

    def report_tag_counts(self):
        compare = lambda x, y: cmp(len(self.tag_counts[y]),
                                   len(self.tag_counts[x]))
        ordered_tags = sorted(list(self.tag_counts.keys()), compare)
        self.stream.write("TAG COUNTS (most often used first):\n")
        for tag in ordered_tags:
            counts = len(self.tag_counts[tag])
            self.stream.write("  @%-30s  %4d\n" % (tag, counts))
        self.stream.write("\n")


class TagLocationFormatter(AbstractTagCountFormatter):
    name = "tag_location"
    description = "Collects data which tags are used where."
    with_tag_inheritance = False

    def report_tags(self):
        self.report_tags_by_locations()

    def report_tags_by_locations(self):
        ordered_tags = sorted(self.tag_counts.keys())
        self.stream.write("TAG LOCATIONS (tags alphabetically ordered):\n")
        for tag in ordered_tags:
            self.stream.write("  @%s:\n" % tag)
            for location in self.tag_counts[tag]:
                self.stream.write("    %s\n" % location)
            self.stream.write("\n")
        self.stream.write("\n")
