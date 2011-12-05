import sys
import tempfile

from mock import Mock
from nose.tools import *

from behave.formatter import formatters
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
    def setUp(self):
        self.config = Mock()
        self.config.no_color = False
        self.config.executing = True

    _line = 0
    @property
    def line(self):
        self._line += 1
        return self._line

    def _formatter(self, file, config):
        f = formatters.get_formatter(self.formatter_name, file, config)
        f.uri('<string>')
        return f

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
        p = self._formatter(_tf(), self.config)
        f = self._feature()
        p.feature(f)

#    def test_step(self):
        # make a feature, scenario and step, format each in turn and then
        # .result


class TestPretty(FormatterTests):
    formatter_name = 'pretty'


class TestPlain(FormatterTests):
    formatter_name = 'plain'


class TestJson(FormatterTests):
    formatter_name = 'json'


class TestTagCount(FormatterTests):
    def _formatter(self, file, config, tag_counts=None):
        if tag_counts is None: tag_counts = {}
        f = formatters.get_formatter('plain', file, config)
        f.uri('<string>')
        f = tag_count_formatter.TagCountFormatter(f, tag_counts)
        f.uri('<string>')
        return f

    def test_tag_count(self):
        counts = {}
        p = self._formatter(_tf(), self.config, counts)

        s = self._scenario()
        f = self._feature(scenarios=[s])
        p.feature(f)
        p.scenario(s)

        eq_(counts, {'ham': ['<string>:1'], 'spam': ['<string>:1']})

