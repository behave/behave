# -*- coding: utf-8 -*-
"""
Collects data how often a tag count is used and where.

EXAMPLE:

    $ behave --dry-run -f tag_counts features/
"""

from behave.formatter.base import Formatter
from behave.model_describe import compute_words_maxsize


# -----------------------------------------------------------------------------
# CLASS: AbstractTagCountFormatter
# -----------------------------------------------------------------------------
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
        self.record_tags(feature.tags, feature)

    def scenario(self, scenario):
        tags = set(scenario.tags)
        if self.with_tag_inheritance:
            tags.update(self._feature_tags)
        self.record_tags(tags, scenario)

    def scenario_outline(self, scenario_outline):
        self._scenario_outline_tags = scenario_outline.tags
        self.record_tags(scenario_outline.tags, scenario_outline)

    def examples(self, examples):
        tags = set(examples.tags)
        if self.with_tag_inheritance:
            tags.update(self._scenario_outline_tags)
            tags.update(self._feature_tags)
        self.record_tags(tags, examples)

    def close(self):
        """Emit tag count reports."""
        # -- ENSURE: Output stream is open.
        self.stream = self.open()
        self.report_tags()
        self.close_stream()

    # -- SPECIFIC API:
    def record_tags(self, tags, model_element):
        for tag in tags:
            if tag not in self.tag_counts:
                self.tag_counts[tag] = []
            self.tag_counts[tag].append(model_element)

    def report_tags(self):
        raise NotImplementedError


# -----------------------------------------------------------------------------
# CLASS: TagCountFormatter
# -----------------------------------------------------------------------------
class TagCountFormatter(AbstractTagCountFormatter):
    name = "tag_count"
    description = "Collects data how often a tag is used."
    with_tag_inheritance = False
    show_ordered_by_usage = False

    def report_tags(self):
        self.report_tag_counts()
        if self.show_ordered_by_usage:
            self.report_tag_counts_by_usage()

    @staticmethod
    def get_tag_count_details(tag_count):
        details = {}
        for element in tag_count:
            category = element.keyword.lower()
            if category not in details:
                details[category] = 0
            details[category] += 1

        parts = []
        if len(details) == 1:
            parts.append(details.keys()[0])
        else:
            for category in sorted(details.keys()):
                text = u"%s: %d" % (category, details[category])
                parts.append(text)
        return ", ".join(parts)

    def report_tag_counts(self):
        # -- PREPARE REPORT:
        ordered_tags = sorted(list(self.tag_counts.keys()))
        tag_maxsize = compute_words_maxsize(ordered_tags)
        schema = "  @%-" + str(tag_maxsize) + "s %4d    (used for %s)\n"

        # -- EMIT REPORT:
        self.stream.write("TAG COUNTS (alphabetically sorted):\n")
        for tag in ordered_tags:
            tag_data = self.tag_counts[tag]
            counts = len(tag_data)
            details = self.get_tag_count_details(tag_data)
            self.stream.write(schema % (tag, counts, details))
        self.stream.write("\n")

    def report_tag_counts_by_usage(self):
        # -- PREPARE REPORT:
        compare = lambda x, y: cmp(len(self.tag_counts[y]),
                                   len(self.tag_counts[x]))
        ordered_tags = sorted(list(self.tag_counts.keys()), compare)
        tag_maxsize = compute_words_maxsize(ordered_tags)
        schema = "  @%-" + str(tag_maxsize) + "s %4d    (used for %s)\n"

        # -- EMIT REPORT:
        self.stream.write("TAG COUNTS (most often used first):\n")
        for tag in ordered_tags:
            tag_data = self.tag_counts[tag]
            counts = len(tag_data)
            details = self.get_tag_count_details(tag_data)
            self.stream.write(schema % (tag, counts, details))
        self.stream.write("\n")


# -----------------------------------------------------------------------------
# CLASS: TagLocationFormatter
# -----------------------------------------------------------------------------
class TagLocationFormatter(AbstractTagCountFormatter):
    name = "tag_location"
    description = "Collects data which tags are used where."
    with_tag_inheritance = False

    def report_tags(self):
        self.report_tags_by_locations()

    def report_tags_by_locations(self):
        # -- PREPARE REPORT:
        locations = set()
        for tag_elements in self.tag_counts.values():
            locations.update([x.location for x in tag_elements])
        location_maxsize = compute_words_maxsize(locations)
        schema = u"    %-" + str(location_maxsize) + "s   %s\n"

        # -- EMIT REPORT:
        self.stream.write("TAG LOCATIONS (alphabetically ordered):\n")
        for tag in sorted(self.tag_counts.keys()):
            self.stream.write("  @%s:\n" % tag)
            for element in self.tag_counts[tag]:
                info = u"%s: %s" % (element.keyword, element.name)
                self.stream.write(schema % (element.location, info))
            self.stream.write("\n")
        self.stream.write("\n")
