import sys
import tempfile

from mock import Mock
from nose.tools import *

from behave.formatter import pretty_formatter
from behave.formatter import json_formatter
from behave.formatter import tag_count_formatter

from behave.model import Tag, Feature, Scenario

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

    _line = 0
    @property
    def line(self):
        self._line += 1
        return self._line

    def _feature(self, keyword=u'k\xe9yword', name=u'name', tags=[u'spam', u'ham'],
            location=u'location', description=[u'description'], scenarios=[],
            background=None):
        line = self.line
        tags = [Tag(name, line) for name in tags]
        return Feature('<string>', line, keyword, name, tags=tags,
            description=description, scenarios=scenarios,
            background=background)

    def _scenario(self, keyword=u'k\xe9yword', name=u'name', tags=[], steps=[]):
        line = self.line
        tags = [Tag(name, line) for name in tags]
        return Scenario('<string>', line, keyword, name, tags=tags, steps=steps)

    def test_feature(self):
        # this test does not actually check the result of the formatting; it
        # just exists to make sure that formatting doesn't explode in the face of
        # unicode and stuff
        p = self._formatter(_tf())
        f = self._feature()
        p.feature(f)

#    def test_step(self):
        # make a feature, scenario and step, format each in turn and then
        # .result


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
        formatter = pretty_formatter.PrettyFormatter(file, False, True)
        f = tag_count_formatter.TagCountFormatter(formatter, tag_counts)
        f.uri('<string>')
        return f

    def test_tag_count(self):
        counts = {}
        p = self._formatter(_tf(), counts)

        s = self._scenario()
        f = self._feature(scenarios=[s])
        p.feature(f)
        p.scenario(s)

        eq_(counts, {'ham': ['<string>:1'], 'spam': ['<string>:1']})

