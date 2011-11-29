import sys
import tempfile

from mock import Mock
from nose.tools import *

from behave.formatter import pretty_formatter
from behave.formatter import json_formatter
from behave.formatter import tag_count_formatter

def _tf():
    '''Open a temp file that looks a bunch like stdout.
    '''
    if sys.version_info[0] == 3:
        # in python3 it's got an encoding and accepts new-style strings
        return tempfile.TemporaryFile(mode='w', encoding='UTF-8')

    # pre-python3 it's not got an encoding and accepts encoded data
    # (old-style strings)
    return tempfile.TemporaryFile(mode='w')


class FormatterTests(object):
    def test_feature(self):
        # this test does not actually check the result of the formatting; it
        # just exists to make sure that formatting doesn't explode in the face of
        # unicode and stuff
        p = self._formatter(_tf())
        f = Mock()
        f.tags = ['spam', 'ham']
        f.keyword = u'k\xe9yword'
        f.name = 'name'
        f.location = 'location'
        f.description = 'description'
        p.feature(f)


class TestPretty(FormatterTests):
    def _formatter(self, file, monochrome=False, executing=True):
        f = pretty_formatter.PrettyFormatter(file, monochrome, executing)
        f.uri('<string>')
        return f


class TestJson(FormatterTests):
    def _formatter(self, file):
        f = json_formatter.JSONFormatter(file)
        f.uri('<string>')
        return f


class TestTagCount(FormatterTests):
    def _formatter(self, file, tag_counts=None):
        if tag_counts is None: tag_counts = {}
        formatter = json_formatter.JSONFormatter(file)
        f = tag_count_formatter.TagCountFormatter(formatter, tag_counts)
        f.uri('<string>')
        return f

    def test_tag_count(self):
        counts = {}
        p = self._formatter(_tf(), counts)
        f = Mock()
        spam = Mock(name='spam')
        spam.name = 'spam'
        ham = Mock(name='ham')
        ham.name = 'ham'
        f.tags = [spam, ham]
        f.keyword = u'k\xe9yword'
        f.name = 'name'
        p.feature(f)

        s = Mock()
        s.keyword = u'k\xe9yword'
        s.name = 'name'
        s.tags = []
        s.line = 1
        p.scenario(s)

        eq_(counts, {'ham': ['<string>:1'], 'spam': ['<string>:1']})

