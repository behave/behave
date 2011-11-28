import tempfile

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

from mock import Mock
from nose.tools import *

from behave.formatter import pretty_formatter

from test.support import forcibly_utf8

class TestFormat(object):

    def test_feature(self):
        # this test does not actually check the result of the formatting; it
        # just exists to make sure that formatting doesn't explode in the face of
        # unicode and stuff
        t = tempfile.TemporaryFile()
        p = pretty_formatter.PrettyFormatter(t, False, True)
        f = Mock()
        f.tags = ['spam', 'ham']
        f.keyword = forcibly_utf8('k\xc3\xa9yword')
        f.name = 'name'
        f.location = 'location'
        f.description = 'description'
        p.feature(f)

