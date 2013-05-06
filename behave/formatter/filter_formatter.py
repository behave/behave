# -*- coding: utf-8 -*-
# FIXME:
__status__ = "DEAD, BROKEN"

import re
from gherkin.formatter import filters

re_type = type(re.compile(''))


class FilterError(Exception):
    pass


class FilterFormatter(object):
    def __init__(self, formatter, filters):
        self.formatter = formatter
        self.filter = self.detect_filters(filters)

        self._feature_tags = []
        self._feature_element_tags = []
        self._examples_tags = []

        self._feature_events = []
        self._background_events = []
        self._feature_element_events = []
        self._examples_events = []

        self._feature_name = None
        self._feature_element_name = None
        self._examples_name = None

        self._feature_element_range = None
        self._examples_range = None

    def uri(self, uri):
        self.formatter.uri(uri)

    def feature(self, feature):
        self._feature_tags = feature.tags
        self._feature_name = feature.name
        self._feature_events = [feature]

    def background(self, background):
        self._feature_element_name = background.name
        self._feature_element_range = background.line_range()
        self._background_events = [background]

    def scenario(self, scenario):
        self.replay()
        self._feature_element_tags = scenario.tags
        self._feature_element_name = scenario.name
        self._feature_element_range = scenario.line_range()
        self._feature_element_events = [scenario]

    def scenario_outline(self, scenario_outline):
        self.replay()
        self._feature_element_tags = scenario_outline.tags
        self._feature_element_name = scenario_outline.name
        self._feature_element_range = scenario_outline.line_range()
        self._feature_element_events = [scenario_outline]

    def examples(self, examples):
        self.replay()
        self._examples_tags = examples.tags
        self._examples_name = examples.name

        if len(examples.rows) == 0:
            table_body_range = (examples.line_range()[1],
                                examples.line_range()[1])
        elif len(examples.rows) == 1:
            table_body_range = (examples.rows[0].line, examples.rows[0].line)
        else:
            table_body_range = (examples.rows[1].line, examples.rows[-1].line)

        self._examples_range = [examples.line_range()[0], table_body_range[1]]

        if self.filter.eval([], [], [table_body_range]):
            examples.rows = self.filter.filter_table_body_rows(examples.rows)

        self._examples_events = [examples]

    def step(self, step):
        if len(self._feature_element_events) > 0:
            self._feature_element_events.append(step)
        else:
            self._background_events.append(step)

        self._feature_element_range = (self._feature_element_range[0],
                                       step.line_range()[1])

    def eof(self):
        self.replay()
        self.formatter.eof()

    def detect_filters(self, filter_list):
        filter_classes = set([type(f) for f in filter_list])
        if len(filter_classes) > 1 and filter_classes != set([str, unicode]):
            message = "Inconsistent filters: %r" % (filter_list, )
            raise FilterError(message)

        if type(filter_list[0]) == int:
            return filters.LineFilter(filter_list)
        if type(filter_list[0]) == re_type:
            return filters.RegexpFilter(filter_list)
        return filters.TagFilter(filter_list)

    def replay(self):
        tags = self._feature_tags + self._feature_element_tags
        names = [self._feature_name, self._feature_element_name]
        ranges = [self._feature_element_range]

        feature_element_ok = self.filter.eval(
            tags,
            [n for n in names if n is not None],
            [r for r in ranges if r is not None],
        )

        examples_ok = self.filter.eval(
            tags + self._examples_tags,
            [n for n in names + [self._examples_name] if n is not None],
            [r for r in ranges + [self._examples_range] if r is not None],
        )

        if feature_element_ok or examples_ok:
            self.replay_events(self._feature_events)
            self.replay_events(self._background_events)
            self.replay_events(self._feature_element_events)

            if examples_ok:
                self.replay_events(self._examples_events)

        self._examples_events[:] = []
        self._examples_tags[:] = []
        self._examples_name = None

    def replay_events(self, events):
        for event in events:
            event.replay(self.formatter)
        events[:] = []
