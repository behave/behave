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
        self._gherkin_object = feature.to_dict()

    def background(self, background):
        self._add_feature_element(background.to_dict())
        self._step_index = 0

    def scenario(self, scenario):
        self._add_feature_element(scenario.to_dict())
        self._step_index = 0

    def scenario_outline(self, scenario_outline):
        self._add_feature_element(scenario_outline.to_dict())
        self._step_index = 0

    def examples(self, examples):
        element = self._feature_element()
        if 'examples' not in element:
            element['examples'] = []
        element['examples'].append(examples.to_dict())

    def step(self, step):
        element = self._feature_element()
        if 'steps' not in element:
            element['steps'] = []
        element['steps'].append(step.to_dict())

    def match(self, match):
        steps = self._feature_element()['steps']
        steps[self._step_index]['match'] = match.to_dict()

    def result(self, result):
        steps = self._feature_element()['steps']
        steps[self._step_index]['result'] = result.to_dict()
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
