# -*- coding: UTF-8 -*-

from __future__ import absolute_import
from behave.model import Feature, Scenario, reset_model
from behave.model_core import Status
from behave.runner import ModelRunner
from behave.parser import parse_tags
from behave.configuration import Configuration


# -----------------------------------------------------------------------------
# TYPE CONVERTERS:
# -----------------------------------------------------------------------------
def convert_comma_list(text):
    text = text.strip()
    return [part.strip()  for part in text.split(",")]

def convert_model_element_tags(text):
    return parse_tags(text.strip())


# -----------------------------------------------------------------------------
# TEST DOMAIN, FIXTURES, STEP UTILS:
# -----------------------------------------------------------------------------
class Model(object):
    def __init__(self, features=None):
        self.features = features or []

class BehaveModelBuilder(object):
    REQUIRED_COLUMNS = ["statement", "name"]
    OPTIONAL_COLUMNS = ["tags"]

    def __init__(self):
        self.features = []
        self.current_feature = None
        self.current_scenario = None

    def build_feature(self, name=u"", tags=None):
        if not name:
            name = u"alice"
        filename = u"%s.feature" % name
        line = 1
        feature = Feature(filename, line, u"Feature", name, tags=tags)
        self.features.append(feature)
        self.current_feature = feature
        return feature

    def build_scenario(self, name="", tags=None):
        if not self.current_feature:
            self.build_feature()
        filename = self.current_feature.filename
        line = self.current_feature.line + 1
        scenario = Scenario(filename, line, u"Scenario", name, tags=tags)
        self.current_feature.add_scenario(scenario)
        self.current_scenario = scenario
        return scenario

    def build_unknown(self, statement, name=u"", row_index=None):
        # pylint: disable=no-self-use
        assert False, u"UNSUPPORTED: statement=%s, name=%s (row=%s)" % \
                      (statement, name, row_index)

    def build_model_from_table(self, table):
        table.require_columns(self.REQUIRED_COLUMNS)
        for row_index, row in enumerate(table.rows):
            statement = row["statement"]
            name = row["name"]
            tags = row.get("tags", [])
            if tags:
                tags = convert_model_element_tags(tags)

            if statement == "Feature":
                self.build_feature(name, tags)
            elif statement == "Scenario":
                self.build_scenario(name, tags)
            else:
                self.build_unknown(statement, name, row_index=row_index)
        return Model(self.features)

def run_model_with_cmdline(model, cmdline):
    reset_model(model.features)
    command_args = cmdline
    config = Configuration(command_args,
                           load_config=False,
                           default_format="null",
                           stdout_capture=False,
                           stderr_capture=False,
                           log_capture=False)
    model_runner = ModelRunner(config, model.features)
    return model_runner.run()

def collect_selected_and_skipped_scenarios(model):  # pylint: disable=invalid-name
    selected = []
    skipped = []
    for feature in model.features:
        scenarios = feature.scenarios
        for scenario in scenarios:
            if scenario.status == Status.skipped:
                skipped.append(scenario)
            else:
                assert scenario.status != Status.untested
                selected.append(scenario)
    return (selected, skipped)


