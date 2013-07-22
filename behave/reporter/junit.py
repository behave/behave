# -*- coding: utf-8 -*-

import os.path
import codecs
from xml.etree import ElementTree
from behave.reporter.base import Reporter
from behave.model import Scenario, ScenarioOutline, Step
from behave.formatter import ansi_escapes
from behave.model_describe import ModelDescriptor
from behave.textutil import indent, make_indentation


def CDATA(text=None):
    # -- issue #70: remove_ansi_escapes(text)
    element = ElementTree.Element('![CDATA[')
    element.text = ansi_escapes.strip_escapes(text)
    return element


class ElementTreeWithCDATA(ElementTree.ElementTree):
    def _write(self, file, node, encoding, namespaces):
        """This method is for ElementTree <= 1.2.6"""

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
            write("\n<%s%s]]>\n" % (elem.tag, elem.text.encode(encoding)))
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
        self.feature = feature
        self.filename = filename
        self.classname = classname
        self.testcases = []
        self.counts_tests = 0
        self.counts_errors = 0
        self.counts_failed = 0
        self.counts_skipped = 0

    def reset(self):
        self.testcases = []
        self.counts_tests = 0
        self.counts_errors = 0
        self.counts_failed = 0
        self.counts_skipped = 0


class JUnitReporter(Reporter):
    """
    Generates JUnit-like XML test report for behave.
    """
    show_multiline = True
    show_timings   = True     # -- Show step timings.

    def make_feature_filename(self, feature):
        filename = None
        for path in self.config.paths:
            if feature.filename.startswith(path):
                filename = feature.filename[len(path) + 1:]
                break
        if not filename:
            # -- NOTE: Directory path (subdirs) are taken into account.
            filename = feature.location.relpath(self.config.base_dir)
        filename = filename.rsplit('.', 1)[0]
        filename = filename.replace('\\', '/').replace('/', '.')
        return filename

    # -- REPORTER-API:
    def feature(self, feature):
        filename  = self.make_feature_filename(feature)
        classname = filename
        report    = FeatureReportData(feature, filename)
        filename  = 'TESTS-%s.xml' % filename

        suite = ElementTree.Element('testsuite')
        suite.set('name', '%s.%s' % (classname, feature.name or feature.filename))

        # -- BUILD-TESTCASES: From scenarios
        for scenario in feature:
            if isinstance(scenario, ScenarioOutline):
                scenario_outline = scenario
                self._process_scenario_outline(scenario_outline, report)
            else:
                self._process_scenario(scenario, report)

        # -- ADD TESTCASES to testsuite:
        for testcase in report.testcases:
            suite.append(testcase)

        suite.set('tests', str(report.counts_tests))
        suite.set('errors', str(report.counts_errors))
        suite.set('failures', str(report.counts_failed))
        suite.set('skipped', str(report.counts_skipped))  # WAS: skips
        # -- ORIG: suite.set('time', str(round(feature.duration, 3)))
        suite.set('time', str(round(feature.duration, 6)))

        if not os.path.exists(self.config.junit_directory):
            # -- ENSURE: Create multiple directory levels at once.
            os.makedirs(self.config.junit_directory)

        tree = ElementTreeWithCDATA(suite)
        report_filename = os.path.join(self.config.junit_directory, filename)
        tree.write(codecs.open(report_filename, 'w'), 'UTF-8')

    # -- MORE:
    @staticmethod
    def select_step_with_status(status, steps):
        """
        Helper function to find the first step that has the given step.status.

        EXAMPLE: Search for a failing step in a scenario (all steps).
            >>> scenario = ...
            >>> failed_step = select_step_with_status("failed", scenario)
            >>> failed_step = select_step_with_status("failed", scenario.all_steps)
            >>> assert failed_step.status == "failed"

        EXAMPLE: Search only scenario steps, skip background steps.
            >>> failed_step = select_step_with_status("failed", scenario.steps)

        :param status:  Step status to search for (as string).
        :param steps:   List of steps to search in (or scenario).
        :returns: Step object, if found.
        :returns: None, otherwise.
        """
        for step in steps:
            assert isinstance(step, Step), \
                "TYPE-MISMATCH: step.class=%s"  % step.__class__.__name__
            if step.status == status:
                return step
        # -- OTHERWISE: No step with the given status found.
        # KeyError("Step with status={0} not found".format(status))
        return None

    @classmethod
    def describe_step(cls, step):
        status = str(step.status)
        if cls.show_timings:
            status += u" in %0.3fs" % step.duration
        text  = u'%s %s ... ' % (step.keyword, step.name)
        text += u'%s\n' % status
        if cls.show_multiline:
            prefix = make_indentation(2)
            if step.text:
                text += ModelDescriptor.describe_docstring(step.text, prefix)
            elif step.table:
                text += ModelDescriptor.describe_table(step.table, prefix)
        return text

    @classmethod
    def describe_scenario(cls, scenario):
        """
        Describe the scenario and the test status.
        NOTE: table, multiline text is missing in description.

        :param scenario:  Scenario that was tested.
        :return: Textual description of the scenario.
        """
        header_line  = u'\n@scenario.begin\n'
        header_line += '  %s: %s\n' % (scenario.keyword, scenario.name)
        footer_line  = u'\n@scenario.end\n' + u'-' * 80 + '\n'
        text = u''
        for step in scenario:
            text += cls.describe_step(step)
        step_indentation = make_indentation(4)
        return header_line + indent(text, step_indentation) + footer_line

    def _process_scenario(self, scenario, report):
        """
        Process a scenario and append information to JUnit report object.
        This corresponds to a JUnit testcase:

          * testcase.@classname = f(filename) +'.'+ feature.name
          * testcase.@name   = scenario.name
          * testcase.@status = scenario.status
          * testcase.@time   = scenario.duration

        Distinguishes now between failures and errors.
        Failures are AssertationErrors: expectation is violated/not met.
        Errors are unexpected RuntimeErrors (all other exceptions).

        If a failure/error occurs, the step, that caused the failure,
        and its location are provided now.

        :param scenario:  Scenario to process.
        :param report:    Context object to store/add info to (outgoing param).
        """
        assert isinstance(scenario, Scenario)
        assert not isinstance(scenario, ScenarioOutline)
        feature   = report.feature
        classname = report.classname
        report.counts_tests += 1

        case = ElementTree.Element('testcase')
        case.set('classname', '%s.%s' % (classname, feature.name or feature.filename))
        case.set('name', scenario.name or '')
        case.set('status', scenario.status)
        # -- ORIG: case.set('time', str(round(scenario.duration, 3)))
        case.set('time', str(round(scenario.duration, 6)))

        step = None
        if scenario.status == 'failed':
            for status in ('failed', 'undefined'):
                step = self.select_step_with_status(status, scenario)
                if step:
                    break
            assert step, "OOPS: No failed step found in scenario: %s" % scenario.name
            assert step.status in ('failed', 'undefined')
            element_name = 'failure'
            if isinstance(step.exception, (AssertionError, type(None))):
                # -- FAILURE: AssertionError
                report.counts_failed += 1
            else:
                # -- UNEXPECTED RUNTIME-ERROR:
                report.counts_errors += 1
                element_name = 'error'
            # -- COMMON-PART:
            failure = ElementTree.Element(element_name)
            step_text = self.describe_step(step).rstrip()
            text = u"\nFailing step: %s\nLocation: %s\n" % (step_text, step.location)
            message = unicode(step.exception)
            if len(message) > 80:
                message = message[:80] + "..."
            failure.set('type', step.exception.__class__.__name__)
            failure.set('message', message)
            text += unicode(step.error_message)
            failure.append(CDATA(text))
            case.append(failure)
        elif scenario.status in ('skipped', 'untested'):
            report.counts_skipped += 1
            step = self.select_step_with_status('undefined', scenario)
            if step:
                # -- UNDEFINED-STEP:
                report.counts_failed += 1
                failure = ElementTree.Element('failure')
                failure.set('type', 'undefined')
                failure.set('message', ('Undefined Step: %s' % step.name))
                case.append(failure)
            else:
                skip = ElementTree.Element('skipped')
                case.append(skip)

        # Create stdout section for each test case
        stdout = ElementTree.Element('system-out')
        text  = self.describe_scenario(scenario)

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

    def _process_scenario_outline(self, scenario_outline, report):
        assert isinstance(scenario_outline, ScenarioOutline)
        for scenario in scenario_outline:
            assert isinstance(scenario, Scenario)
            self._process_scenario(scenario, report)
