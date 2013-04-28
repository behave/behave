#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Utility script to retrieve duration information from behave JSON output.

REQUIRES: Python >= 2.6 (json module is part of Python standard library)
LICENSE:  BSD
"""

__author__    = "Jens Engel"
__copyright__ = "(c) 2013 by Jens Engel"
__license__   = "BSD"
VERSION = "0.1.0"


# -- IMPORTS:
from behave import json_parser
from behave.model import ScenarioOutline
from   optparse import OptionParser
import os.path
import sys


# ----------------------------------------------------------------------------
# FUNCTIONS:
# ----------------------------------------------------------------------------
class StepDurationData(object):
    def __init__(self, step=None):
        self.step_name = None
        self.min_duration = sys.maxint
        self.max_duration = 0
        self.durations = []
        self.step = step
        if step:
            self.process_step(step)

    @staticmethod
    def make_step_name(step):
        step_name = "%s %s" % (step.step_type.capitalize(), step.name)
        return step_name

    def process_step(self, step):
        step_name = self.make_step_name(step)
        if not self.step_name:
            self.step_name = step_name
        if self.min_duration > step.duration:
            self.min_duration = step.duration
        if self.max_duration < step.duration:
            self.max_duration = step.duration
        self.durations.append(step.duration)


class BehaveDurationData(object):
    def __init__(self):
        self.step_registry = {}
        self.all_steps = []
        self.all_scenarios = []


    def process_features(self, features):
        for feature in features:
            self.process_feature(feature)

    def process_feature(self, feature):
        if feature.background:
            self.process_background(feature.background)
        for scenario in feature.scenarios:
            if isinstance(scenario, ScenarioOutline):
                self.process_scenario_outline(scenario)
            else:
                self.process_scenario(scenario)

    def process_step(self, step):
        step_name = StepDurationData.make_step_name(step)
        known_step = self.step_registry.get(step_name, None)
        if known_step:
            known_step.process_step(step)
        else:
            step_data = StepDurationData(step)
            self.step_registry[step_name] = step_data
        self.all_steps.append(step)

    def process_background(self, scenario):
        for step in scenario:
            self.process_step(step)

    def process_scenario(self, scenario):
        for step in scenario:
            self.process_step(step)

    def process_scenario_outline(self, scenario_outline):
        for scenario in scenario_outline:
            self.process_scenario(scenario)

    def report_step_durations(self, limit=None, min_duration=None, ostream=sys.stdout):
        step_datas = self.step_registry.values()
        steps_size = len(step_datas)
        compare = lambda x, y: cmp(x.max_duration, y.max_duration)
        steps_by_longest_duration_first = sorted(step_datas, compare, reverse=True)
        ostream.write("STEP DURATIONS (longest first, size=%d):\n" % steps_size)
        ostream.write("-" * 80)
        ostream.write("\n")
        for index, step in enumerate(steps_by_longest_duration_first):
            ostream.write("% 4d.  %9.6fs  %s" % \
                          (index+1, step.max_duration, step.step_name))
            calls = len(step.durations)
            if calls > 1:
                ostream.write(" (%d calls, min: %.6fs)\n" % (calls, step.min_duration))
            else:
                ostream.write("\n")
            if ((limit and index+1 >= limit) or
                (step.max_duration < min_duration)):
                remaining = steps_size - (index+1)
                ostream.write("...\nSkip remaining %d steps.\n" % remaining)
                break


# ----------------------------------------------------------------------------
# MAIN FUNCTION:
# ----------------------------------------------------------------------------
def main(args=None):
    if args is None:
        args = sys.argv[1:]

    usage_ = """%prog [OPTIONS] JsonFile
Read behave JSON data file and extract steps with longest duration."""
    parser = OptionParser(usage=usage_, version=VERSION)
    parser.add_option("-e", "--encoding", dest="encoding",
                     default="UTF-8",
                     help="Encoding to use (default: %default).")
    parser.add_option("-l", "--limit", dest="limit", type="int",
                     help="Max. number of steps (default: %default).")
    parser.add_option("-m", "--min", dest="min_duration", default="0",
                     help="Min. duration threshold (default: %default).")
    options, filenames = parser.parse_args(args)
    if not filenames:
        parser.error("OOPS, no filenames provided.")
    elif len(filenames) > 1:
        parser.error("OOPS: Can only process one JSON file.")
    min_duration = float(options.min_duration)
    if min_duration < 0:
        min_duration = None
    json_filename = filenames[0]
    if not os.path.exists(json_filename):
        parser.error("JSON file '%s' not found" % json_filename)

    # -- NORMAL PROCESSING: Read JSON, extract step durations and report them.
    features = json_parser.parse(json_filename)
    processor = BehaveDurationData()
    processor.process_features(features)
    processor.report_step_durations(options.limit, min_duration)
    sys.stdout.write("Detected %d features.\n" % len(features))
    return 0


# ----------------------------------------------------------------------------
# AUTO-MAIN:
# ----------------------------------------------------------------------------
if __name__ == "__main__":
    sys.exit(main())
