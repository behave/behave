import struct
import sys
import tempfile

from mock import Mock, patch
from nose.tools import *

from behave.formatter import formatters
from behave.formatter import pretty
# from behave.formatter import tags
from behave.formatter.base import StreamOpener
from behave.model import Tag, Feature, Match, Scenario, Step


class TestGetTerminalSize(object):
    def setUp(self):
        try:
            self.ioctl_patch = patch('fcntl.ioctl')
            self.ioctl = self.ioctl_patch.start()
        except ImportError:
            self.ioctl_patch = None
            self.ioctl = None
        self.zero_struct = struct.pack('HHHH', 0, 0, 0, 0)

    def tearDown(self):
        if self.ioctl_patch:
            self.ioctl_patch.stop()

    def test_windows_fallback(self):
        platform = sys.platform
        sys.platform = 'windows'

        eq_(pretty.get_terminal_size(), (80, 24))

        sys.platform = platform

    def test_termios_fallback(self):
        try:
            import termios
            return
        except ImportError:
            pass

        eq_(pretty.get_terminal_size(), (80, 24))

    def test_exception_in_ioctl(self):
        try:
            import termios
        except ImportError:
            return

        def raiser(*args, **kwargs):
            raise Exception('yeehar!')

        self.ioctl.side_effect = raiser

        eq_(pretty.get_terminal_size(), (80, 24))
        self.ioctl.assert_called_with(0, termios.TIOCGWINSZ, self.zero_struct)

    def test_happy_path(self):
        try:
            import termios
        except ImportError:
            return

        self.ioctl.return_value = struct.pack('HHHH', 17, 23, 5, 5)

        eq_(pretty.get_terminal_size(), (23, 17))
        self.ioctl.assert_called_with(0, termios.TIOCGWINSZ, self.zero_struct)

    def test_zero_size_fallback(self):
        try:
            import termios
        except ImportError:
            return

        self.ioctl.return_value = self.zero_struct

        eq_(pretty.get_terminal_size(), (80, 24))
        self.ioctl.assert_called_with(0, termios.TIOCGWINSZ, self.zero_struct)


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
        self.config.color = True
        self.config.outputs = [ StreamOpener(stream=sys.stdout) ]
        self.config.format = [self.formatter_name]

    _line = 0
    @property
    def line(self):
        self._line += 1
        return self._line

    def _formatter(self, file, config):
        stream_opener = StreamOpener(stream=file)
        f = formatters.get_formatter(config, [stream_opener])[0]
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

    def _step(self, keyword=u'k\xe9yword', step_type='given', name=u'name',
              text=None, table=None):
        line = self.line
        return Step('<string>', line, keyword, step_type, name, text=text,
                    table=table)

    def _match(self, arguments=None):
        def dummy():
            pass

        return Match(dummy, arguments)

    def test_feature(self):
        # this test does not actually check the result of the formatting; it
        # just exists to make sure that formatting doesn't explode in the face of
        # unicode and stuff
        p = self._formatter(_tf(), self.config)
        f = self._feature()
        p.feature(f)

    def test_scenario(self):
        p = self._formatter(_tf(), self.config)
        f = self._feature()
        p.feature(f)
        s = self._scenario()
        p.scenario(s)

    def test_step(self):
        p = self._formatter(_tf(), self.config)
        f = self._feature()
        p.feature(f)
        s = self._scenario()
        p.scenario(s)
        s = self._step()
        p.step(s)
        p.match(self._match([]))
        s.status = u'passed'
        p.result(s)


class TestPretty(FormatterTests):
    formatter_name = 'pretty'


class TestPlain(FormatterTests):
    formatter_name = 'plain'


class TestJson(FormatterTests):
    formatter_name = 'json'


class TestTagsCount(FormatterTests):
    formatter_name = 'tags'

    def test_tag_counts(self):
        p = self._formatter(_tf(), self.config)

        s = self._scenario(tags=[u'ham', u'foo'])
        f = self._feature(scenarios=[s])  # feature.tags= ham, spam
        p.feature(f)
        p.scenario(s)

        eq_(p.tag_counts, {'ham': [ f, s ], 'spam': [ f ], 'foo': [ s ]})


class MultipleFormattersTests(FormatterTests):
    formatters = []

    def setUp(self):
        self.config = Mock()
        self.config.color = True
        self.config.outputs = [ StreamOpener(stream=sys.stdout)
                                for i in self.formatters ]
        self.config.format = self.formatters

    def _formatters(self, file, config):
        stream_opener = StreamOpener(stream=file)
        fs = formatters.get_formatter(config, [stream_opener])
        for f in fs:
            f.uri('<string>')
        return fs

    def test_feature(self):
        # this test does not actually check the result of the formatting; it
        # just exists to make sure that formatting doesn't explode in the face of
        # unicode and stuff
        ps = self._formatters(_tf(), self.config)
        f = self._feature()
        for p in ps:
            p.feature(f)

    def test_scenario(self):
        ps = self._formatters(_tf(), self.config)
        f = self._feature()
        for p in ps:
            p.feature(f)
            s = self._scenario()
            p.scenario(s)

    def test_step(self):
        ps = self._formatters(_tf(), self.config)
        f = self._feature()
        for p in ps:
            p.feature(f)
            s = self._scenario()
            p.scenario(s)
            s = self._step()
            p.step(s)
            p.match(self._match([]))
            s.status = u'passed'
            p.result(s)


class TestPrettyAndPlain(MultipleFormattersTests):
    formatters = ['pretty', 'plain']

class TestPrettyAndJSON(MultipleFormattersTests):
    formatters = ['pretty', 'json']

class TestJSONAndPlain(MultipleFormattersTests):
    formatters = ['json', 'plain']
