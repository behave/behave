# -*- coding: UTF-8 -*-
# pylint: disable=line-too-long
"""
This module provides a reporter with JUnit XML output.

Mapping of behave model elements to XML elements::

    feature     -> xml_element:testsuite
    scenario    -> xml_element:testcase

XML document structure::

    # -- XML elements:
    # CARDINALITY SUFFIX:
    #   ?   optional (zero or one)
    #   *   many0 (zero or more)
    #   +   many (one or more)
    testsuites := sequence<testsuite>
    testsuite:
        properties? : sequence<property>
        testcase* :
            error?      : text
            failure?    : text
            system-out  : text
            system-err  : text

    testsuite:
        @name       : TokenString
        @tests      : int
        @failures   : int
        @errors     : int
        @skipped    : int
        @time       : Decimal       # Duration in seconds
        # -- SINCE: behave-1.2.6
        @timestamp  : IsoDateTime
        @hostname   : string

    testcase:
        @name       : TokenString
        @classname  : TokenString
        @status     : string        # Status enum
        @time       : Decimal       # Elapsed seconds

    error:
        @message    : string
        @type       : string

    failure:
        @message    : string
        @type       : string

    # -- HINT: Not used
    property:
        @name  : TokenString
        @value : string

    type Status : Enum("passed", "failed", "skipped", "untested")

Note that a spec for JUnit XML output was not clearly defined.
Best sources are:

* `JUnit XML`_ (for PDF)
* JUnit XML (`ant spec 1`_, `ant spec 2`_)


.. _`JUnit XML`:  https://junitpdfreport.sourceforge.net/managedcontent/PdfTranslation
.. _`ant spec 1`: https://github.com/windyroad/JUnit-Schema
.. _`ant spec 2`: https://svn.apache.org/repos/asf/ant/core/trunk/src/main/org/apache/tools/ant/taskdefs/optional/junit/XMLJUnitResultFormatter.java
"""
# pylint: enable=line-too-long

from __future__ import absolute_import
import os.path
import codecs
import re
import sys
from xml.etree import ElementTree
from datetime import datetime
from behave.reporter.base import Reporter
from behave.model import Rule, Scenario, ScenarioOutline, Step
from behave.model_type import Status
from behave.formatter import ansi_escapes
from behave.model_describe import ModelDescriptor
from behave.summary import SummaryCollector
from behave.textutil import indent, make_indentation, text as _text
from behave.userdata import UserDataNamespace
import six

if six.PY2:
    # -- USE: Python3 backport for better unicode compatibility.
    import traceback2 as traceback
else:
    import traceback
    unichr = chr


def CDATA(text=None):   # pylint: disable=invalid-name
    # -- issue #70: remove_ansi_escapes(text)
    element = ElementTree.Element('![CDATA[')
    element.text = ansi_escapes.strip_escapes(text)
    return element

def _compile_invalid_re():
    # https://stackoverflow.com/questions/1707890/fast-way-to-filter-illegal-xml-unicode-chars-in-python
    illegal_unichrs = [
        (0x00, 0x08), (0x0B, 0x1F), (0x7F, 0x84), (0x86, 0x9F),
        (0xD800, 0xDFFF), (0xFDD0, 0xFDDF), (0xFFFE, 0xFFFF),
        (0x1FFFE, 0x1FFFF), (0x2FFFE, 0x2FFFF), (0x3FFFE, 0x3FFFF),
        (0x4FFFE, 0x4FFFF), (0x5FFFE, 0x5FFFF), (0x6FFFE, 0x6FFFF),
        (0x7FFFE, 0x7FFFF), (0x8FFFE, 0x8FFFF), (0x9FFFE, 0x9FFFF),
        (0xAFFFE, 0xAFFFF), (0xBFFFE, 0xBFFFF), (0xCFFFE, 0xCFFFF),
        (0xDFFFE, 0xDFFFF), (0xEFFFE, 0xEFFFF), (0xFFFFE, 0xFFFFF),
        (0x10FFFE, 0x10FFFF),
    ]

    illegal_ranges = [
        "%s-%s" % (unichr(low), unichr(high))
        for (low, high) in illegal_unichrs
        if low < sys.maxunicode]

    return re.compile(u'[%s]' % u''.join(illegal_ranges))


_invalid_re = _compile_invalid_re()

def _escape_invalid_xml_chars(text):
    # replace invalid chars with Unicode hex
    return _invalid_re.subn(lambda c: u'U+{0:0=4}'.format(ord(c.group())), text)[0]


def escape_CDATA(text):  # pylint: disable=invalid-name
    # -- issue #510 escape text in CDATA
    # CDATA cannot contain the string "]]>" anywhere in the XML document.
    if not text:
        return text
    text = text.replace(u']]>', u']]&gt;')
    return _escape_invalid_xml_chars(text)


class ElementTreeWithCDATA(ElementTree.ElementTree):
    # pylint: disable=redefined-builtin, no-member
    def _write(self, file, node, encoding, namespaces):
        """This method is for ElementTree <= 1.2.6"""

        if node.tag == '![CDATA[':
            text = node.text.encode(encoding)
            file.write("\n<![CDATA[%s]]>\n" % text)
        else:
            ElementTree.ElementTree._write(self, file, node, encoding,
                                           namespaces)

if hasattr(ElementTree, '_serialize'):
    # pylint: disable=protected-access
    def _serialize_xml2(write, elem, encoding, qnames, namespaces,
                        orig=ElementTree._serialize_xml):
        if elem.tag == '![CDATA[':
            write("\n<%s%s]]>\n" % \
                  (elem.tag, escape_CDATA(elem.text).encode(encoding, "xmlcharrefreplace")))
            return
        return orig(write, elem, encoding, qnames, namespaces)

    def _serialize_xml3(write, elem, qnames, namespaces,
                        short_empty_elements=None,
                        orig=ElementTree._serialize_xml):
        if elem.tag == '![CDATA[':
            write("\n<{tag}{text}]]>\n".format(
                tag=elem.tag, text=escape_CDATA(elem.text)))
            return
        if short_empty_elements:
            # python >=3.3
            return orig(write, elem, qnames, namespaces, short_empty_elements)
        else:
            # python <3.3
            return orig(write, elem, qnames, namespaces)

    if six.PY3:
        ElementTree._serialize_xml = \
            ElementTree._serialize['xml'] = _serialize_xml3
    elif six.PY2:
        ElementTree._serialize_xml = \
            ElementTree._serialize['xml'] = _serialize_xml2


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
    """Generates JUnit-like XML test report for behave.
    """
    # -- XML REPORT:
    userdata_scope = "behave.reporter.junit"
    show_timings = True     # -- Show step timings.
    show_skipped_always = False
    show_timestamp = True
    show_hostname = True
    # -- XML REPORT PART: Describe scenarios
    show_scenarios = True   # Show scenario descriptions.
    show_tags = True
    show_multiline = True

    def __init__(self, config):
        super(JUnitReporter, self).__init__(config)
        self._summary_collector = SummaryCollector()
        self.setup_with_userdata(config.userdata)

    def setup_with_userdata(self, userdata):
        """Setup JUnit reporter with userdata information.
        A user can now tweak the output format of this reporter.

        EXAMPLE:
        .. code-block:: ini

            # -- FILE: behave.ini
            [behave.userdata]
            behave.reporter.junit.show_hostname = false
        """
        # -- EXPERIMENTAL:
        config = UserDataNamespace(self.userdata_scope, userdata)
        self.show_hostname = config.getbool("show_hostname", self.show_hostname)
        self.show_multiline = config.getbool("show_multiline", self.show_multiline)
        self.show_scenarios = config.getbool("show_scenarios", self.show_scenarios)
        self.show_tags = config.getbool("show_tags", self.show_tags)
        self.show_timings = config.getbool("show_timings", self.show_timings)
        self.show_timestamp = config.getbool("show_timestamp", self.show_timestamp)
        self.show_skipped_always = config.getbool("show_skipped_always",
                                              self.show_skipped_always)

    @property
    def feature_failed_counts(self):
        summary_counts4features = self._summary_collector.summary_counts.features
        return summary_counts4features.get(Status.failed, 0)

    @property
    def feature_error_counts(self):
        summary_counts4features = self._summary_collector.summary_counts.features
        counts = 0
        for error_status in (Status.error, Status.hook_error):
            counts += summary_counts4features.get(error_status, 0)
        return counts

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
        return _text(filename)

    @property
    def show_skipped(self):
        return self.config.show_skipped or self.show_skipped_always

    # -- REPORTER-API:
    def feature(self, feature):
        if feature.status == Status.skipped and not self.show_skipped:
            # -- SKIP-OUTPUT: If skipped features should not be shown.
            return

        self._summary_collector.visit_feature(feature)
        feature_filename = self.make_feature_filename(feature)
        classname = feature_filename
        report = FeatureReportData(feature, feature_filename)
        now = datetime.now()

        suite = ElementTree.Element(u'testsuite')
        feature_name = feature.name or feature_filename
        suite.set(u'name', u'%s.%s' % (classname, feature_name))

        # -- BUILD-TESTCASES: From run_items (and scenarios)
        self._process_run_items_for(feature, report)

        # -- ADD TESTCASES to testsuite:
        for testcase in report.testcases:
            suite.append(testcase)

        suite.set(u'tests', _text(report.counts_tests))
        suite.set(u'errors', _text(report.counts_errors))
        suite.set(u'failures', _text(report.counts_failed))
        suite.set(u'skipped', _text(report.counts_skipped))  # WAS: skips
        suite.set(u'time', _text(round(feature.duration, 6)))
        # -- SINCE: behave-1.2.6.dev0
        if self.show_timestamp:
            suite.set(u'timestamp', _text(now.isoformat()))
        if self.show_hostname:
            suite.set(u'hostname', _text(gethostname()))

        if not os.path.exists(self.config.junit_directory):
            # -- ENSURE: Create multiple directory levels at once.
            os.makedirs(self.config.junit_directory)

        tree = ElementTreeWithCDATA(suite)
        report_dirname = self.config.junit_directory
        report_basename = u'TESTS-%s.xml' % feature_filename
        report_filename = os.path.join(report_dirname, report_basename)
        tree.write(codecs.open(report_filename, "wb"), "UTF-8")

    # -- MORE:
    # pylint: disable=line-too-long
    @staticmethod
    def select_step_with_status(status, steps):
        """Helper function to find the first step that has the given
        step.status.

        EXAMPLE: Search for a failing step in a scenario (all steps).
            >>> scenario = ...
            >>> failed_step = select_step_with_status(Status.failed, scenario)
            >>> failed_step = select_step_with_status(Status.failed, scenario.all_steps)
            >>> assert failed_step.status == Status.failed

        EXAMPLE: Search only scenario steps, skip background steps.
            >>> failed_step = select_step_with_status(Status.failed, scenario.steps)

        :param status:  Step status to search for (as enum value).
        :param steps:   List of steps to search in (or scenario).
        :returns: Step object, if found.
        :returns: None, otherwise.

        .. versionchanged:: 1.2.6
            status: Use enum value instead of string (or string).
        """
        for step in steps:
            assert isinstance(step, Step), \
                "TYPE-MISMATCH: step.class=%s"  % step.__class__.__name__
            if step.status == status:
                return step
        # -- OTHERWISE: No step with the given status found.
        # KeyError("Step with status={0} not found".format(status))
        return None
    # pylint: enable=line-too-long

    @classmethod
    def select_step_with_any_status(cls, desired_statuses, steps):
        """
        .. versionchanged:: 1.2.7
        """
        for step in steps:
            assert isinstance(step, Step), \
                "TYPE-MISMATCH: step.class=%s"  % step.__class__.__name__
            if step.status in desired_statuses:
                return step
        # -- NOT-FOUND:
        return None

    def describe_step(self, step):
        status_text = _text(step.status.name)
        if self.show_timings:
            status_text += u" in %0.3fs" % step.duration
        text = u'%s %s ... ' % (step.keyword, step.name)
        text += u'%s\n' % status_text
        if self.show_multiline:
            prefix = make_indentation(2)
            if step.text:
                text += ModelDescriptor.describe_docstring(step.text, prefix)
            elif step.table:
                text += ModelDescriptor.describe_table(step.table, prefix)
        return text

    @classmethod
    def describe_tags(cls, tags):
        text = u''
        if tags:
            text = u'@'+ u' @'.join(tags)
        return text

    def describe_scenario(self, scenario):
        """Describe the scenario and the test status.
        NOTE: table, multiline text is missing in description.

        :param scenario:  Scenario that was tested.
        :return: Textual description of the scenario.
        """
        header_line = u'\n@scenario.begin\n'
        if self.show_tags and scenario.tags:
            header_line += u'\n  %s\n' % self.describe_tags(scenario.tags)
        header_line += u'  %s: %s\n' % (scenario.keyword, scenario.name)
        footer_line = u'\n@scenario.end\n' + u'-' * 80 + '\n'
        text = u''
        for step in scenario:
            text += self.describe_step(step)
        step_indentation = make_indentation(4)
        return header_line + indent(text, step_indentation) + footer_line

    def _process_scenario(self, scenario, report):
        """Process a scenario and append information to JUnit report object.
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
        # pylint: disable=too-many-locals, too-many-branches, too-many-statements
        assert isinstance(scenario, Scenario)
        assert not isinstance(scenario, ScenarioOutline)
        if scenario.status != Status.skipped or self.show_skipped:
            # -- NOTE: Count only if not-skipped or skipped should be shown.
            report.counts_tests += 1
        classname = report.classname
        feature = report.feature
        feature_name = feature.name
        if not feature_name:
            feature_name = self.make_feature_filename(feature)

        case = ElementTree.Element("testcase")
        case.set(u"classname", u"%s.%s" % (classname, feature_name))
        case.set(u"name", scenario.name or "")
        case.set(u"status", scenario.status.name)
        case.set(u"time", _text(round(scenario.duration, 6)))

        step = None
        failed_statuses = (Status.failed, )
        error_statuses = (Status.error, Status.hook_error, Status.pending, Status.undefined)
        skipped_statuses = (Status.skipped, Status.untested)

        if scenario.status.is_error():
            # -- NOTE: Scenario may fail now due to hook-errors.
            # UNEXPECTED RUNTIME-ERROR:
            report.counts_errors += 1
            step = self.select_step_with_any_status(error_statuses, scenario.all_steps)
            error = self._make_error_element_for(scenario, step)
            case.append(error)
        elif scenario.status.is_failure():
            # -- NOTE: Scenario may fail due to ...
            report.counts_failed += 1
            step = self.select_step_with_any_status(failed_statuses, scenario.all_steps)
            failure = self._make_failure_element_for(scenario, step)
            case.append(failure)
        elif scenario.status in skipped_statuses and self.show_skipped:
            report.counts_skipped += 1
            problematic_statuses = [Status.pending, Status.undefined]
            step = self.select_step_with_any_status(problematic_statuses, scenario.all_steps)
            if step:
                # -- UNDEFINED-STEP:
                report.counts_failed += 1
                message = u"Undefined Step: %s" % step.name.strip()
                failure = ElementTree.Element(u"failure")
                failure.set(u"type", u"undefined")
                failure.set(u"message", message)
                case.append(failure)

            # -- ALWAYS ADD TO THE REPORT:
            skip = ElementTree.Element(u'skipped')
            case.append(skip)

        # Create stdout section for each test case
        stdout = ElementTree.Element(u"system-out")
        text = u""
        if self.show_scenarios:
            text = self.describe_scenario(scenario)

        # Append the captured standard output
        if scenario.captured.stdout:
            output = _text(scenario.captured.stdout)
            text += u"\nCaptured stdout:\n%s\n" % output
        stdout.append(CDATA(text))
        case.append(stdout)

        # Create stderr section for each test case
        if scenario.captured.stderr:
            stderr = ElementTree.Element(u"system-err")
            output = _text(scenario.captured.stderr)
            text = u"\nCaptured stderr:\n%s\n" % output
            stderr.append(CDATA(text))
            case.append(stderr)

        if scenario.status != Status.skipped or self.show_skipped:
            report.testcases.append(case)

    def _make_problem_description_for(self, element_name, scenario, step):
        xml_element = ElementTree.Element(element_name)
        if step:
            step_text = self.describe_step(step).rstrip()
            text = u"\nFailing step: %s\nLocation: %s\n" % \
                   (step_text, step.location)
            message = _text(step.exception).strip()
            xml_element.set(u'type', step.exception.__class__.__name__)
            xml_element.set(u'message', message)
            text += _text(step.error_message)
        else:
            # -- MAYBE: Hook failure before any step is executed.
            failure_type = "UnknownError"
            if scenario.exception:
                failure_type = scenario.exception.__class__.__name__
            scenario_error_message = scenario.error_message
            if scenario_error_message:
                scenario_error_message = scenario_error_message.strip()
            xml_element.set(u'type', failure_type)
            xml_element.set(u'message', scenario_error_message or "")
            traceback_lines = traceback.format_tb(scenario.exc_traceback)
            traceback_lines.insert(0, u"Traceback:\n")
            text = _text(u"".join(traceback_lines))
        xml_element.append(CDATA(text))
        return xml_element

    def _make_failure_element_for(self, scenario, step):
        return self._make_problem_description_for(u"failure", scenario, step)

    def _make_error_element_for(self, scenario, step):
        return self._make_problem_description_for(u"error", scenario, step)

    def _process_run_items_for(self, parent, report):
        for run_item in parent.run_items:
            if isinstance(run_item, Rule):
                self._process_rule(run_item, report)
            elif isinstance(run_item, ScenarioOutline):
                self._process_scenario_outline(run_item, report)
            else:
                assert isinstance(run_item, Scenario)
                self._process_scenario(run_item, report)

    def _process_rule(self, rule, report):
        self._process_run_items_for(rule, report)

    def _process_scenario_outline(self, scenario_outline, report):
        assert isinstance(scenario_outline, ScenarioOutline)
        for scenario in scenario_outline:
            assert isinstance(scenario, Scenario)
            self._process_scenario(scenario, report)

# -----------------------------------------------------------------------------
# SUPPORT:
# -----------------------------------------------------------------------------
def gethostname():
    """Return hostname of local host (as string)"""
    import socket
    return socket.gethostname()
