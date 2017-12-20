#!/usr/bin/env python
"""
Filter JUnit XML reports to show only a subset of all information.

JUNIT XML SCHEMA:

    element:testsuite: failures="..." errors="..."
        +-- element:testcase: name="..." status="..."
"""

from __future__ import absolute_import, print_function, with_statement
import os.path
import sys
import argparse
from fnmatch import fnmatch
from xml.etree import ElementTree as ET
from xml.dom import minidom
from behave.textutil import indent

__author = "Jens Engel"
__status__ = "prototype"

NAME = os.path.basename(__file__)
VERSION = "0.1.0"
REPORT_DIR = "reports"

def xml_prettify(elem):
    """Return a pretty-printed XML string for the XML element."""
    text = ET.tostring(elem, "utf-8")
    reparsed = minidom.parseString(text)
    return reparsed.toprettyxml(indent=" ")

def xml_select_testcases_with_status(tree, status):
    return tree.findall(".//testcase[@status='%s']" % status)

def path_select_files(paths, pattern="*.xml"):
    if not paths:
        paths = [REPORT_DIR]

    selected = []
    for pathname in paths:
        if os.path.isdir(pathname):
            for root, dirs, files in os.walk(pathname):
                for filename in files:
                    if fnmatch(filename, pattern):
                        filename2 = os.path.join(root, filename)
                        selected.append(os.path.normpath(filename2))
        elif os.path.isfile(pathname) and fnmatch(pathname, pattern):
            selected.append(pathname)
    return selected

def report_testcases(filename, testcases):
    print(u"REPORT: {0}".format(filename))
    for xml_testcase in testcases:
        print("  TESTCASE: {0}".format(xml_testcase.get("name")))
        xml_text = indent(xml_prettify(xml_testcase), "    ")
        print(xml_text)

def main(args=None):
    """Filter JUnit XML reports to show only a subset of all information."""
    if args is None:
        args = sys.argv[1:]

    parser = argparse.ArgumentParser(prog=NAME,
                                     description=main.__doc__)
    parser.add_argument("-s", "--status", default="failed", required=False,
                        choices=["passed", "failed", "skipped"],
                        help="Status to select (passed, failed, skipped).")
    parser.add_argument("xml_file", nargs="*",
                        help="XML file(s) or directory with XML files.")
    parser.add_argument("--version", action="version", version=VERSION)

    options = parser.parse_args(args)

    xml_files = options.xml_file
    xml_reports = path_select_files(xml_files)
    for xml_filename in xml_reports:
        tree = ET.parse(xml_filename)
        testcases = xml_select_testcases_with_status(tree, options.status)
        if testcases:
            report_testcases(xml_filename, testcases)
    return 0

if __name__ == "__main__":
    sys.exit(main())
