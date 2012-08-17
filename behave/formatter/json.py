from __future__ import absolute_import

import base64
try:
    import json
except ImportError:
    import simplejson as json

from behave.formatter.base import Formatter


class JSONFormatter(Formatter):
    name = 'json'
    description = 'JSON dump of test run'

    def __init__(self, stream, config):
        super(JSONFormatter, self).__init__(stream, config)

        self._gherkin_object = None
        self._step_index = 0

    def uri(self, uri):
        pass

    def feature(self, feature):
        self._gherkin_object = {
            'keyword': feature.keyword,
            'tags': list(feature.tags),
            'description': feature.description,
            'location': feature.location,
        }

    def background(self, background):
        self._add_feature_element({
            'keyword': background.keyword,
            'location': background.location,
            'steps': [],
        })
        self._step_index = 0

    def scenario(self, scenario):
        self._add_feature_element({
            'keyword': scenario.keyword,
            'name': scenario.name,
            'tags': scenario.tags,
            'location': scenario.location,
            'steps': [],
        })
        self._step_index = 0

    def scenario_outline(self, scenario_outline):
        self._add_feature_element({
            'keyword': scenario_outline.keyword,
            'name': scenario_outline.name,
            'tags': scenario_outline.tags,
            'location': scenario_outline.location,
            'steps': [],
            'examples': [],
        })
        self._step_index = 0

    def examples(self, examples):
        e = {
            'keyword': examples.keyword,
            'name': examples.name,
            'location': examples.location,
        }

        if examples.table:
            e['table'] = {
                'headings': examples.table.headings,
                'rows': examples.table.rows,
            }

        element = self._feature_element()
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
            s['table'] = {
                'headings': step.table.headings,
                'rows': step.table.rows,
            }

        element = self._feature_element()
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

        steps = self._feature_element()['steps']
        steps[self._step_index]['match'] = match

    def result(self, result):
        steps = self._feature_element()['steps']
        steps[self._step_index]['result'] = {
            'status': result.status,
            'duration': result.duration,
        }
        self._step_index += 1

    def embedding(self, mime_type, data):
        step = self._feature_element()['steps'][-1]
        step['embeddings'].append({
            'mime_type': mime_type,
            'data': base64.b64encode(data).replace('\n', ''),
        })

    def eof(self):
        if not self.stream:
            return
        self.stream.write(json.dumps(self._gherkin_object))

    def _add_feature_element(self, element):
        if 'elements' not in self._gherkin_object:
            self._gherkin_object['elements'] = []
        self._gherkin_object['elements'].append(element)

    def _feature_element(self):
        return self._gherkin_object['elements'][-1]
