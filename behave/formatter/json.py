# -*- coding: utf-8 -*-

from __future__ import absolute_import
from behave.formatter.base import Formatter
import base64
try:
    import json
except ImportError:
    import simplejson as json


# -----------------------------------------------------------------------------
# CLASS: JSONFormatter
# -----------------------------------------------------------------------------
class JSONFormatter(Formatter):
    name = 'json'
    description = 'JSON dump of test run'
    dumps_kwargs = {}


    def __init__(self, stream_opener, config):
        super(JSONFormatter, self).__init__(stream_opener, config)
        # -- ENSURE: Output stream is open.
        self.stream = self.open()
        self.feature_count = 0
        self.current_feature_data = None
        self._step_index = 0

    def reset(self):
        self.current_feature_data = None
        self._step_index = 0


    def uri(self, uri):
        pass

    def feature(self, feature):
        self.reset()
        self.current_feature_data = {
            'keyword': feature.keyword,
            'tags': list(feature.tags),
            'description': feature.description,
            'location': feature.location,
        }

    def background(self, background):
        element = self.add_feature_element({
            'keyword': background.keyword,
            'location': background.location,
            'steps': [],
        })
        if background.name:
            element['name'] = background.name
        self._step_index = 0

        # -- ADD BACKGROUND STEPS: Support *.feature file regeneration.
        for step_ in background.steps:
            self.step(step_)

    def scenario(self, scenario):
        element = self.add_feature_element({
            'keyword': scenario.keyword,
            'name': scenario.name,
            'tags': scenario.tags,
            'location': scenario.location,
            'steps': [],
        })
        if scenario.description:
            element['description'] = scenario.description
        self._step_index = 0

    def scenario_outline(self, scenario_outline):
        element = self.add_feature_element({
            'keyword': scenario_outline.keyword,
            'name': scenario_outline.name,
            'tags': scenario_outline.tags,
            'location': scenario_outline.location,
            'steps': [],
            'examples': [],
        })
        if scenario_outline.description:
            element['description'] = scenario_outline.description
        self._step_index = 0

    @classmethod
    def make_table(cls, table):
        table_data = {
            'headings': table.headings,
            'rows': [ list(row) for row in table.rows ]
        }
        return table_data

    def examples(self, examples):
        e = {
            'keyword': examples.keyword,
            'name': examples.name,
            'location': examples.location,
        }

        if examples.table:
            e['table'] = self.make_table(examples.table)

        element = self.current_feature_element
        element['examples'].append(e)

    def step(self, step):
        s = {
            'keyword': step.keyword,
            'step_type': step.step_type,
            'name': step.name,
            'location': step.location,
        }

        if step.text:
            s['text'] = step.text
        if step.table:
            s['table'] = self.make_table(step.table)
        element = self.current_feature_element
        element['steps'].append(s)

    def match(self, match):
        args = []
        for argument in match.arguments:
            arg = {
                'original': argument.original,
                'value': argument.value,
            }
            if argument.name:
                arg['name'] = argument.name
            args.append(arg)

        match = {
            'location': match.location,
            'arguments': args,
        }

        steps = self.current_feature_element['steps']
        steps[self._step_index]['match'] = match

    def result(self, result):
        steps = self.current_feature_element['steps']
        steps[self._step_index]['result'] = {
            'status': result.status,
            'duration': result.duration,
        }
        self._step_index += 1

    def embedding(self, mime_type, data):
        step = self.current_feature_element['steps'][-1]
        step['embeddings'].append({
            'mime_type': mime_type,
            'data': base64.b64encode(data).replace('\n', ''),
        })

    def eof(self):
        """
        End of feature
        """
        if not self.current_feature_data:
            return

        # -- NORMAL CASE: Write collected data of current feature.
        if self.feature_count == 0:
            # -- FIRST FEATURE:
            self.write_json_header()
        else:
            # -- NEXT FEATURE:
            self.write_json_feature_separator()

        self.write_json_feature(self.current_feature_data)
        self.current_feature_data = None
        self.feature_count += 1

    def close(self):
        self.write_json_footer()
        self.close_stream()

    # -- JSON-DATA COLLECTION:
    def add_feature_element(self, element):
        assert self.current_feature_data is not None
        if 'elements' not in self.current_feature_data:
            self.current_feature_data['elements'] = []
        self.current_feature_data['elements'].append(element)
        return element

    @property
    def current_feature_element(self):
        assert self.current_feature_data is not None
        return self.current_feature_data['elements'][-1]


    # -- JSON-WRITER:
    def write_json_header(self):
        self.stream.write('{ "features": [\n')

    def write_json_footer(self):
        self.stream.write(']}\n')

    def write_json_feature(self, feature):
        self.stream.write(json.dumps(feature, **self.dumps_kwargs))
        self.stream.flush()

    def write_json_feature_separator(self):
        self.stream.write(",\n\n")


# -----------------------------------------------------------------------------
# CLASS: PrettyJSONFormatter
# -----------------------------------------------------------------------------
class PrettyJSONFormatter(JSONFormatter):
    """
    Provides readable/comparable textual JSON output.
    """
    name = 'json-pretty'
    description = 'JSON dump of test run (human readable)'
    dumps_kwargs = { 'indent': 2, 'sort_keys': True }
