# -*- coding: utf-8 -*-
"""
Contains utility functions and classes for Runners.
"""

from behave import parser
from bisect import bisect
import os.path
import re
import sys
import types


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
# CLASS: FileLocation
# -----------------------------------------------------------------------------
class FileLocation(unicode):
    """
    Provides a value object for file location objects.
    A file location consists of:

      * filename
      * line (number), optional

    LOCATION SCHEMA:
      * "{filename}:{line}" or
      * "{filename}" (if line number is not present)
    """
    # -- pylint: disable=R0904,R0924
    #   R0904: 30,0:FileLocation: Too many public methods (43/30) => unicode
    #   R0924: 30,0:FileLocation: Badly implemented Container, ...=> unicode
    __pychecker__ = "missingattrs=line"     # -- Ignore warnings for 'line'.

    def __new__(cls, filename, line=None):
        assert isinstance(filename, basestring)
        obj = unicode.__new__(cls, filename)
        obj.line = line
        return obj

    @property
    def filename(self):
        return unicode(self)

    def get(self):
        return self.filename

    def exists(self):
        return os.path.exists(self.filename)

    def __eq__(self, other):
        if isinstance(other, FileLocation):
            return self.filename == other.filename and self.line == other.line
        else:
            return self.filename == other

    def __ne__(self, other):
        return not self == other

    def __repr__(self):
        return u'<FileLocation: filename="%s", line=%s>' % \
               (self.filename, self.line)

    def __str__(self):
        if self.line is None:
            return self.filename
        else:
            assert self.line > 0
            return u"%s:%d" % (self.filename, self.line)


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


# -----------------------------------------------------------------------------
# CLASS: FeatureScenarioLocationCollector
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
            if self.feature and False:
                self.filename = self.feature.filename
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
            assert isinstance(location, basestring)
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
        filename = os.path.abspath(location)
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


def parse_features_configfile(features_configfile):
    """
    Read textual file, ala '@features.txt'. This file contains:

      * a feature filename in each line
      * empty lines (skipped)
      * comment lines (skipped)

    Relative path names are evaluated relative to the configfile directory.
    A leading '@' (AT) character is removed from the configfile name.

    :param features_configfile:  Name of features configfile.
    :return: List of feature filenames.
    """
    if features_configfile.startswith('@'):
        features_configfile = features_configfile[1:]
    if not os.path.isfile(features_configfile):
        raise FileNotFoundError(features_configfile)
    here = os.path.dirname(features_configfile) or "."
    files = []
    for line in open(features_configfile).readlines():
        line = line.strip()
        if not line:
            continue    # SKIP: Over empty line(s).
        elif line.startswith('#'):
            continue    # SKIP: Over comment line(s).
        filename = os.path.normpath(os.path.join(here, line))
        location = FileLocationParser.parse(filename)
        files.append(location)
    return files


def collect_feature_files(paths, strict=True):
    """
    Collect feature file names by processing list of paths (from command line).
    A path can be a:

      * filename (ending with ".feature")
      * location, ala "{filename}:{line_number}"
      * features configuration filename, ala "@features.txt"
      * directory, to discover and collect all "*.feature" files below.

    :param paths:  Paths to process.
    :return: Feature filenames to use.
    """
    files = []
    for path in paths:
        if os.path.isdir(path):
            for dirpath, dirnames, filenames in os.walk(path):
                dirnames.sort()
                for filename in sorted(filenames):
                    if filename.endswith(".feature"):
                        location = FileLocation(os.path.join(dirpath, filename))
                        files.append(location)
        elif path.startswith('@'):
            # -- USE: behave @list_of_features.txt
            files.extend(parse_features_configfile(path[1:]))
        else:
            # -- OTHERWISE: Normal filename or location (schema: filename:line)
            location = FileLocationParser.parse(path)
            if not location.filename.endswith(".feature"):
                raise InvalidFilenameError(location.filename)
            elif location.exists():
                files.append(location)
            elif strict:
                raise FileNotFoundError(path)
    return files



def make_undefined_step_snippet(step, language=None):
    """
    Helper function to create an undefined-step snippet for a step.

    :param step: Step to use (as Step object or step text).
    :param language: i18n language, optionally needed for step text parsing.
    :return: Undefined-step snippet (as string).
    """
    if isinstance(step, types.StringTypes):
        step_text = step
        steps = parser.parse_steps(step_text, language=language)
        step = steps[0]
        assert step, "ParseError: %s" % step_text
    prefix = u""
    if sys.version_info[0] == 2:
        prefix = u"u"

    # snippet  = u"@"+ step.step_type +"("+ prefix + step.name + "')"
    # snippet += u"\ndef impl(context):\n    assert False\n\n"
    schema = u"@%s(%s'%s')\ndef impl(context):\n    assert False\n\n"
    snippet = schema % (step.step_type, prefix, step.name)
    return snippet
