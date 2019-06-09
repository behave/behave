# -*- coding: UTF-8 -*-
r"""

Regular expressions for winpath:
http://regexlib.com/Search.aspx?k=file+name

^(([a-zA-Z]:|\\)\\)?(((\.)|(\.\.)|([^\\/:\*\?"\|<>\. ](([^\\/:\*\?"\|<>\. ])|([^\\/:\*\?"\|<>]*[^\\/:\*\?"\|<>\. ]))?))\\)*[^\\/:\*\?"\|<>\. ](([^\\/:\*\?"\|<>\. ])|([^\\/:\*\?"\|<>]*[^\\/:\*\?"\|<>\. ]))?$

https://github.com/kgryte/regex-filename-windows/blob/master/lib/index.js
REGEX: /^([a-zA-Z]:|[\\\/]{2}[^\\\/]+[\\\/]+[^\\\/]+|)([\\\/]|)([\s\S]*?)((?:\.{1,2}|[^\\\/]+?|)(\.[^.\/\\]*|))(?:[\\\/]*)$/
Splits a Windows filename.
Modified from Node.js [source]{@link https://github.com/nodejs/node/blob/1a3b295d0f46b2189bd853800b1e63ab4d106b66/lib/path.js#L65}.
"""

from __future__ import absolute_import
from behave4cmd0.command_shell_proc import \
    BehaveWinCommandOutputProcessor, \
    TracebackLineNormalizer, ExceptionWithPathNormalizer
import re
import pytest

# -----------------------------------------------------------------------------
# IMPLEMENTATION
# -----------------------------------------------------------------------------
# winpath_pattern = ur"^($([A-Za-z]:(\[^\]+)*)|((\[^\]+)*)|([^\]+\[^\]+)*)$"
winpath_pattern = u"^([A-Za-z]:(\\[\w\.\-]+)+)|((\\[\w\.\-]+)*)|(\s[\w\.\-]+([\w\.\-]+)*)$"
winpath_re = re.compile(winpath_pattern, re.UNICODE)

class PathNormalizer(object):
    def normalize(self, output):
        pattern = u'^.*$'
    def __call__(self, output):
        pass

# -----------------------------------------------------------------------------
# TEST CANDIDATES:
# -----------------------------------------------------------------------------
line_processor_configerrors = [
    ExceptionWithPathNormalizer(
        u"ConfigError: No steps directory in '(?P<path>.*)'",
        "ConfigError: No steps directory in"),
    BehaveWinCommandOutputProcessor.line_processors[1],
]

line_processor_parsererrors = [
    ExceptionWithPathNormalizer(
        u'ParserError: Failed to parse "(?P<path>.*)"',
        u'ParserError: Failed to parse'),
    BehaveWinCommandOutputProcessor.line_processors[2],
]

line_processor_ioerrors = [
    ExceptionWithPathNormalizer(
        # ur"No such file or directory: '(?P<path>.*)'",
        # u"No such file or directory:"),  # IOError
        # ur"Error: \\[Errno 2\\] No such file or directory: '(?P<path>.*)'",
        u"No such file or directory: '(?P<path>.*)'",
        u"[Errno 2] No such file or directory:"),  # IOError
    BehaveWinCommandOutputProcessor.line_processors[3],
]

line_processor_traceback = [
    ExceptionWithPathNormalizer(
        r'^\s*File "(?P<path>.*)", line \d+, in ',
        '  File "'),
    BehaveWinCommandOutputProcessor.line_processors[4],
]

# -----------------------------------------------------------------------------
# TEST SUITE
# -----------------------------------------------------------------------------
xfail = pytest.mark.xfail()

class TestWinpathRegex(object):

    @pytest.mark.parametrize("winpath", [
        u'C:\\foo\\bar\\alice.txt',
        u'C:\\foo\\bar',
        u'C:\\alice.txt',
        u'C:\\.verbose',
        u'.\\foo\\bar\\alice.txt',
        u'..\\foo\\..\\bar\\alice.txt',
        u'foo\\bar\\alice.txt',
        u'alice.txt',
    ])
    def test_match__with_valid_winpath(self, winpath):
        mo = winpath_re.match(winpath)
        assert mo is not None

    @xfail
    @pytest.mark.parametrize("winpath", [
        u'2:\\foo\\bar\\alice.txt',
        u'C:\\bar\\alice.txt',
    ])
    def test_match__with_invalid_winpath(self, winpath):
        mo = winpath_re.match(winpath)
        assert mo is None

class TestPathNormalizer(object):
    @pytest.mark.parametrize("output, expected", [
        (u"ConfigError: No steps directory in 'C:\\one\\two\\three.txt'",
         u"ConfigError: No steps directory in 'C:/one/two/three.txt'"),
    ])
    def test_call__with_pattern1(self, output, expected):
        for line_processor in line_processor_configerrors:
            actual = line_processor(output)
            assert actual == expected

    # ParserError: Failed to parse "(?P<path2>.*)"
    @pytest.mark.parametrize("output, expected", [
        (u'ParserError: Failed to parse "C:\\one\\two\\three.txt"',
         u'ParserError: Failed to parse "C:/one/two/three.txt"'),
    ])
    def test_call__with_pattern2(self, output, expected):
        for line_processor in line_processor_parsererrors:
            actual = line_processor(output)
            assert actual == expected

    @pytest.mark.parametrize("output, expected", [
        (u"Error: [Errno 2] No such file or directory: 'C:\\one\\two\\three.txt'",
         u"Error: [Errno 2] No such file or directory: 'C:/one/two/three.txt'"),
    ])
    def test_call__with_pattern3(self, output, expected):
        for index, line_processor in enumerate(line_processor_ioerrors):
            actual = line_processor(output)
            assert actual == expected, "line_processor %s" % index

    @pytest.mark.parametrize("output, expected", [
        (u'  File "C:\\one\\two\\three.txt", line 123, in xxx_some_method',
         u'  File "C:/one/two/three.txt", line 123, in xxx_some_method'),
    ])
    def test_call__with_pattern4(self, output, expected):
        for index, line_processor in enumerate(line_processor_traceback):
            actual = line_processor(output)
            assert actual == expected, "line_processor %s" % index
