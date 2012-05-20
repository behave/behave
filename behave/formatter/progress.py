# -*- coding: utf-8 -*-
# pylint: disable=C0111,W0511
#   C0111   missing docstrings

from behave.formatter.base import Formatter
import os.path

class ProgressFormatter(Formatter):
    name = "progress"
    description = "Provides dotted progress bar on successful execution"

    def __init__(self, stream, config):
        super(ProgressFormatter, self).__init__(stream, config)
        self.steps = []
        self.failures = []
        self.current_feature  = None
        self.current_scenario = None

    def reset(self):
        self.steps = []
        self.failures = []
        self.current_feature  = None
        self.current_scenario = None

    # -- FORMATTER API:
    def feature(self, feature):
        self.current_feature = feature
        short_filename = os.path.relpath(feature.filename, os.getcwd())
        self.stream.write("%s  " % short_filename)

    def background(self, background):
        pass

    def scenario(self, scenario):
        self.current_scenario = scenario

    def scenario_outline(self, outline):
        self.current_scenario = outline

    def step(self, step):
        self.steps.append(step)

    def result(self, result):
        self.steps.pop(0)
        # print "XXX result.status=%s" % result
        if result.error_message:
            self.stream.write(u"F")
            result.feature  = self.current_feature
            result.scenario = self.current_scenario
            self.failures.append(result)
        else:
            self.stream.write(u".")
        # self.stream.flush()

    def eof(self):
        """
        Called at end of a feature.
        It would be better to have a hook that is called after all features.
        """
        self.report_failures()
        self.reset()

    # -- SPECIFIC PART:
    def report_failures(self):
        if self.failures:
            self.stream.write(u"\n{seperator}\n".format(seperator="-"*80))
            for result in self.failures:
                self.stream.write(u"FAILURE in step '%s':\n" % result.name)
                self.stream.write(u"  Feature:  %s\n" % result.feature.name)
                self.stream.write(u"  Scenario: %s\n" % result.scenario.name)
                self.stream.write(u"%s\n" % result.error_message)
            self.stream.write(u"{seperator}\n".format(seperator="-"*80))

