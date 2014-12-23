# -*- coding: utf-8 -*-
"""
Contains utility functions and classes for Runners.
"""

from __future__ import absolute_import
from behave import parser
from behave.model import FileLocation
from bisect import bisect
from six import string_types
import glob
import os.path
import re
import sys


# -----------------------------------------------------------------------------
# EXCEPTIONS:
# -----------------------------------------------------------------------------
class FileNotFoundError(LookupError):
    pass


class InvalidFileLocationError(LookupError):
    pass


class InvalidFilenameError(ValueError):
    pass


# -----------------------------------------------------------------------------
# CLASS: FileLocationParser
# -----------------------------------------------------------------------------
class FileLocationParser:
    # -- pylint: disable=W0232
    # W0232: 84,0:FileLocationParser: Class has no __init__ method
    pattern = re.compile(r"^\s*(?P<filename>.*):(?P<line>\d+)\s*$", re.UNICODE)

    @classmethod
    def parse(cls, text):
        match = cls.pattern.match(text)
        if match:
            filename = match.group("filename").strip()
            line = int(match.group("line"))
            return FileLocation(filename, line)
        else:
            # -- NORMAL PATH/FILENAME:
            filename = text.strip()
            return FileLocation(filename)

    # @classmethod
    # def compare(cls, location1, location2):
    #     loc1 = cls.parse(location1)
    #     loc2 = cls.parse(location2)
    #     return cmp(loc1, loc2)


# -----------------------------------------------------------------------------
# CLASSES:
# -----------------------------------------------------------------------------
class FeatureScenarioLocationCollector(object):
    """
    Collects FileLocation objects for a feature.
    This is used to select a subset of scenarios in a feature that should run.

    USE CASE:
        behave feature/foo.feature:10
        behave @selected_features.txt
        behave @rerun_failed_scenarios.txt

    With features configuration files, like:

        # -- file:rerun_failed_scenarios.txt
        feature/foo.feature:10
        feature/foo.feature:25
        feature/bar.feature
        # -- EOF

    """
    def __init__(self, feature=None, location=None, filename=None):
        if not filename and location:
            filename = location.filename
        self.feature = feature
        self.filename = filename
        self.use_all_scenarios = False
        self.scenario_lines = set()
        self.all_scenarios = set()
        self.selected_scenarios = set()
        if location:
            self.add_location(location)

    def clear(self):
        self.feature = None
        self.filename = None
        self.use_all_scenarios = False
        self.scenario_lines = set()
        self.all_scenarios = set()
        self.selected_scenarios = set()

    def add_location(self, location):
        if not self.filename:
            self.filename = location.filename
            # if self.feature and False:
            #     self.filename = self.feature.filename
        # -- NORMAL CASE:
        assert self.filename == location.filename, \
            "%s <=> %s" % (self.filename, location.filename)
        if location.line:
            self.scenario_lines.add(location.line)
        else:
            # -- LOCATION WITHOUT LINE NUMBER:
            # Selects all scenarios in a feature.
            self.use_all_scenarios = True

    @staticmethod
    def select_scenario_line_for(line, scenario_lines):
        """
        Select scenario line for any given line.

        ALGORITHM: scenario.line <= line < next_scenario.line

        :param line:  A line number in the file (as number).
        :param scenario_lines: Sorted list of scenario lines.
        :return: Scenario.line (first line) for the given line.
        """
        if not scenario_lines:
            return 0    # -- Select all scenarios.
        pos = bisect(scenario_lines, line) - 1
        if pos < 0:
            pos = 0
        return scenario_lines[pos]

    def discover_selected_scenarios(self, strict=False):
        """
        Discovers selected scenarios based on the provided file locations.
        In addition:
          * discover all scenarios
          * auto-correct BAD LINE-NUMBERS

        :param strict:  If true, raises exception if file location is invalid.
        :return: List of selected scenarios of this feature (as set).
        :raises InvalidFileLocationError:
            If file location is no exactly correct and strict is true.
        """
        assert self.feature
        if not self.all_scenarios:
            self.all_scenarios = self.feature.walk_scenarios()

        # -- STEP: Check if lines are correct.
        existing_lines = [scenario.line for scenario in self.all_scenarios]
        selected_lines = list(self.scenario_lines)
        for line in selected_lines:
            new_line = self.select_scenario_line_for(line, existing_lines)
            if new_line != line:
                # -- AUTO-CORRECT BAD-LINE:
                self.scenario_lines.remove(line)
                self.scenario_lines.add(new_line)
                if strict:
                    msg = "Scenario location '...:%d' should be: '%s:%d'" % \
                          (line, self.filename, new_line)
                    raise InvalidFileLocationError(msg)

        # -- STEP: Determine selected scenarios and store them.
        scenario_lines = set(self.scenario_lines)
        selected_scenarios = set()
        for scenario in self.all_scenarios:
            if scenario.line in scenario_lines:
                selected_scenarios.add(scenario)
                scenario_lines.remove(scenario.line)
        # -- CHECK ALL ARE RESOLVED:
        assert not scenario_lines
        return selected_scenarios

    def build_feature(self):
        """
        Determines which scenarios in the feature are selected and marks the
        remaining scenarios as skipped. Scenarios with the following tags
        are excluded from skipped-marking:

          * @setup
          * @teardown

        If no file locations are stored, the unmodified feature is returned.

        :return: Feature object to use.
        """
        use_all_scenarios = not self.scenario_lines or self.use_all_scenarios
        if not self.feature or use_all_scenarios:
            return self.feature

        # -- CASE: Select subset of all scenarios of this feature.
        #    Mark other scenarios as skipped (except in a few cases).
        self.all_scenarios = self.feature.walk_scenarios()
        self.selected_scenarios = self.discover_selected_scenarios()
        unselected_scenarios = set(self.all_scenarios) - self.selected_scenarios
        for scenario in unselected_scenarios:
            if "setup" in scenario.tags or "teardown" in scenario.tags:
                continue
            scenario.mark_skipped()
        return self.feature


class FeatureListParser(object):
    """
    Read textual file, ala '@features.txt'. This file contains:

      * a feature filename or FileLocation on each line
      * empty lines (skipped)
      * comment lines (skipped)
      * wildcards are expanded to select 0..N filenames or directories

    Relative path names are evaluated relative to the listfile directory.
    A leading '@' (AT) character is removed from the listfile name.
    """

    @staticmethod
    def parse(text, here=None):
        """
        Parse contents of a features list file as text.

        :param text: Contents of a features list(file).
        :param here: Current working directory to use (optional).
        :return: List of FileLocation objects
        """
        locations = []
        for line in text.splitlines():
            filename = line.strip()
            if not filename:
                continue    # SKIP: Over empty line(s).
            elif filename.startswith('#'):
                continue    # SKIP: Over comment line(s).

            if here and not os.path.isabs(filename):
                filename = os.path.join(here, line)
            filename = os.path.normpath(filename)
            if glob.has_magic(filename):
                # -- WITH WILDCARDS:
                for filename2 in glob.iglob(filename):
                    location = FileLocationParser.parse(filename2)
                    locations.append(location)
            else:
                location = FileLocationParser.parse(filename)
                locations.append(location)
        return locations

    @classmethod
    def parse_file(cls, filename):
        """
        Read textual file, ala '@features.txt'.

        :param filename:  Name of feature list file.
        :return: List of feature file locations.
        """
        if filename.startswith('@'):
            filename = filename[1:]
        if not os.path.isfile(filename):
            raise FileNotFoundError(filename)
        here = os.path.dirname(filename) or "."
        contents = open(filename).read()
        return cls.parse(contents, here)

# -----------------------------------------------------------------------------
# FUNCTIONS:
# -----------------------------------------------------------------------------
def parse_features(feature_files, language=None):
    """
    Parse feature files and return list of Feature model objects.
    Handles:

      * feature file names, ala "alice.feature"
      * feature file locations, ala: "alice.feature:10"

    :param feature_files: List of feature file names to parse.
    :param language:      Default language to use.
    :return: List of feature objects.
    """
    scenario_collector = FeatureScenarioLocationCollector()
    features = []
    for location in feature_files:
        if not isinstance(location, FileLocation):
            assert isinstance(location, string_types)
            location = FileLocation(os.path.normpath(location))

        if location.filename == scenario_collector.filename:
            scenario_collector.add_location(location)
            continue
        elif scenario_collector.feature:
            # -- ADD CURRENT FEATURE: As collection of scenarios.
            current_feature = scenario_collector.build_feature()
            features.append(current_feature)
            scenario_collector.clear()

        # -- NEW FEATURE:
        assert isinstance(location, FileLocation)
        filename = os.path.abspath(location.filename)
        feature = parser.parse_file(filename, language=language)
        if feature:
            # -- VALID FEATURE:
            # SKIP CORNER-CASE: Feature file without any feature(s).
            scenario_collector.feature = feature
            scenario_collector.add_location(location)
    # -- FINALLY:
    if scenario_collector.feature:
        current_feature = scenario_collector.build_feature()
        features.append(current_feature)
    return features


def collect_feature_locations(paths, strict=True):
    """
    Collect feature file names by processing list of paths (from command line).
    A path can be a:

      * filename (ending with ".feature")
      * location, ala "{filename}:{line_number}"
      * features configuration filename, ala "@features.txt"
      * directory, to discover and collect all "*.feature" files below.

    :param paths:  Paths to process.
    :return: Feature file locations to use (as list of FileLocations).
    """
    locations = []
    for path in paths:
        if os.path.isdir(path):
            for dirpath, dirnames, filenames in os.walk(path):
                dirnames.sort()
                for filename in sorted(filenames):
                    if filename.endswith(".feature"):
                        location = FileLocation(os.path.join(dirpath, filename))
                        locations.append(location)
        elif path.startswith('@'):
            # -- USE: behave @list_of_features.txt
            locations.extend(FeatureListParser.parse_file(path[1:]))
        else:
            # -- OTHERWISE: Normal filename or location (schema: filename:line)
            location = FileLocationParser.parse(path)
            if not location.filename.endswith(".feature"):
                raise InvalidFilenameError(location.filename)
            elif location.exists():
                locations.append(location)
            elif strict:
                raise FileNotFoundError(path)
    return locations


def make_undefined_step_snippet(step, language=None):
    """
    Helper function to create an undefined-step snippet for a step.

    :param step: Step to use (as Step object or step text).
    :param language: i18n language, optionally needed for step text parsing.
    :return: Undefined-step snippet (as string).
    """
    if isinstance(step, string_types):
        step_text = step
        steps = parser.parse_steps(step_text, language=language)
        step = steps[0]
        assert step, "ParseError: %s" % step_text
    # prefix = u""
    # if sys.version_info[0] == 2:
    #    prefix = u"u"
    prefix = u"u"
    single_quote = "'"
    if single_quote in step.name:
        step.name = step.name.replace(single_quote, r"\'")

    schema = u"@%s(%s'%s')\ndef step_impl(context):\n    raise NotImplementedError()\n\n"
    snippet = schema % (step.step_type, prefix, step.name)
    return snippet


def print_undefined_step_snippets(undefined_steps, stream=None, colored=True):
    """
    Print snippets for the undefined steps that were discovered.

    :param undefined_steps:  List of undefined steps (as list<string>).
    :param stream:      Output stream to use (default: sys.stderr).
    :param colored:     Indicates if coloring should be used (default: True)
    """
    if not undefined_steps:
        return
    if not stream:
        stream = sys.stderr

    msg = u"\nYou can implement step definitions for undefined steps with "
    msg += u"these snippets:\n\n"
    printed = set()
    for step in undefined_steps:
        if step in printed:
            continue
        printed.add(step)
        msg += make_undefined_step_snippet(step)

    if colored:
        # -- OOPS: Unclear if stream supports ANSI coloring.
        from behave.formatter.ansi_escapes import escapes
        msg = escapes['undefined'] + msg + escapes['reset']
    stream.write(msg)
    stream.flush()
