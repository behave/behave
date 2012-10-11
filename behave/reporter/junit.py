# -*- coding: utf-8 -*-

import os.path
from xml.etree import ElementTree

from behave.reporter.base import Reporter
from behave.model import Scenario, ScenarioOutline, Step

def CDATA(text=None):         # pylint: disable=C0103
    element = ElementTree.Element('![CDATA[')
    element.text = text
    return element


class ElementTreeWithCDATA(ElementTree.ElementTree):
    def _write(self, file, node, encoding, namespaces):
        """This method is for ElementTree <= 1.2.6"""
        # pylint: disable=W0622
        #   Redefining built-in file

        if node.tag == '![CDATA[':
            text = node.text.encode(encoding)
            file.write("\n<![CDATA[%s]]>\n" % text)
        else:
            ElementTree.ElementTree._write(self, file, node, encoding,
                                           namespaces)


if hasattr(ElementTree, '_serialize'):
    def _serialize_xml(write, elem, encoding, qnames, namespaces,
                       orig=ElementTree._serialize_xml):
        if elem.tag == '![CDATA[':
            write("\n<%s%s]]>\n" % (elem.tag, elem.text))
            return
        return orig(write, elem, encoding, qnames, namespaces)

    ElementTree._serialize_xml = ElementTree._serialize['xml'] = _serialize_xml



class FeatureReportData(object):
    """
    Provides value object to collect JUnit report data from a Feature.
    """
    def __init__(self, feature, filename, classname=None):
        if not classname and filename:
            classname = filename.replace('/', '.')
        self.feature  = feature
        self.filename = filename
        self.classname = classname
        self.testcases = []
        self.counts_tests = 0
        self.counts_failed = 0
        self.counts_skipped = 0

    def reset(self):
        self.testcases = []
        self.counts_tests = 0
        self.counts_failed = 0
        self.counts_skipped = 0



class JUnitReporter(Reporter):

    def get_feature_filename(self, feature):
        filename = None
        for path in self.config.paths:
            if feature.filename.startswith(path):
                filename = feature.filename[len(path) + 1:]
                break
        if filename is None:
            filename = os.path.split(feature.filename)[1]
        filename = filename.rsplit('.', 1)[0]
        filename = filename.replace('/', '.')
        return filename

    def feature(self, feature):
        filename  = self.get_feature_filename(feature)
        classname = filename
        report    = FeatureReportData(feature, filename)
        filename  = 'TESTS-%s.xml' % filename

        suite = ElementTree.Element('testsuite')
        suite.set('name', '%s.%s' % (classname, feature.name or feature.filename))

        # -- BUILD-TESTCASES: From scenarios
        for scenario in feature:
            if isinstance(scenario, ScenarioOutline):
                scenario_outline = scenario
                self._process_scenario_outline(report, scenario_outline)
            else:
                self._process_scenario(report, scenario)

        # -- ADD TESTCASES to testsuite:
        for testcase in report.testcases:
            suite.append(testcase)

        suite.set('tests', str(report.counts_tests))
        suite.set('failures', str(report.counts_failed))
        suite.set('skips', str(report.counts_skipped))
        # -- ORIG: suite.set('time', str(round(feature.duration, 3)))
        suite.set('time', str(round(feature.duration, 6)))

        if not os.path.exists(self.config.junit_directory):
            # -- ENSURE: Create multiple directory levels at once.
            os.makedirs(self.config.junit_directory)

        tree = ElementTreeWithCDATA(suite)
        report_filename = os.path.join(self.config.junit_directory, filename)
        tree.write(open(report_filename, 'w'), 'utf8')

    @staticmethod
    def select_first_step_with_status(status, steps):
        """
        Helper method to find the first step that has the given status.
        :param status:  Step status to search for (as string).
        :param steps:   List of steps to search in.
        :returns: Step object, if found.
        :returns: None, otherwise.
        """
        for step in steps:
            assert isinstance(step, Step), "TYPE-MISMATCH: "+\
                    "step.class={0}".format(step.__class__.__name__)
            if step.status == status:
                return step
            # -- OTHERWISE:
        # KeyError("Step with status={0} not found".format(status))
        return None

    def _process_scenario(self, report, scenario):
        """
        Process a scenario and append information to JUnit report object.
        This corresponds to a JUnit testcase.
        """
        assert isinstance(scenario, Scenario)
        feature   = report.feature
        classname = report.classname
        report.counts_tests += 1

        case = ElementTree.Element('testcase')
        case.set('classname', '%s.%s' % (classname, feature.name or feature.filename))
        case.set('name', scenario.name or '')
        # -- ORIG: case.set('time', str(round(scenario.duration, 3)))
        case.set('time', str(round(scenario.duration, 6)))

        if scenario.status == 'failed':
            report.counts_failed += 1
            failure = ElementTree.Element('failure')
            step = self.select_first_step_with_status('failed', scenario)
            if step:
                failure.set('type', step.exception.__class__.__name__)
                failure.set('message', str(step.exception))
                if not isinstance(step.exception, AssertionError):
                    failure.text = step.error_message
                case.append(failure)
        elif scenario.status in ('skipped', 'untested'):
            report.counts_skipped += 1
            step = self.select_first_step_with_status('undefined', scenario)
            if step:
                # -- UNDEFINED-STEP:
                report.counts_failed += 1
                failure = ElementTree.Element('failure')
                failure.set('type', 'undefined')
                failure.set('message', '')
                case.append(failure)
            else:
                skip = ElementTree.Element('skipped')
                case.append(skip)

        # Create stdout section for each test case
        stdout = ElementTree.Element('system-out')
        text = u'Steps:\n'
        for step in scenario:
            text += u'%12s %s ... ' % (step.keyword, step.name)
            text += u'%s\n' % step.status
            # Append the captured standard output
        if scenario.stdout:
            text += '\nCaptured stdout:\n%s\n' % scenario.stdout
        stdout.append(CDATA(text))
        case.append(stdout)

        # Create stderr section for each test case
        if scenario.stderr:
            stderr = ElementTree.Element('system-err')
            text = u'\nCaptured stderr:\n%s\n' % scenario.stderr
            stderr.append(CDATA(text))
            case.append(stderr)

        report.testcases.append(case)

    def _process_scenario_outline(self, report, scenario_outline):
        assert isinstance(scenario_outline, ScenarioOutline)
        for scenario in scenario_outline:
            assert isinstance(scenario, Scenario)
            self._process_scenario(report, scenario)

