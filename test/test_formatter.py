import sys
import tempfile

from mock import Mock
from nose.tools import *

from behave.formatter import pretty_formatter

class TestFormat(object):

    def test_feature(self):
        # this test does not actually check the result of the formatting; it
        # just exists to make sure that formatting doesn't explode in the face of
        # unicode and stuff

        # open a temp file that looks a bunch like stdout
        if sys.version_info[0] == 3:
            # in python3 it's got an encoding and accepts new-style strings
            t = tempfile.TemporaryFile(mode='w', encoding='UTF-8')
        else:
            # pre-python3 it's not got an encoding and accepts encoded data
            # (old-style strings)
            t = tempfile.TemporaryFile(mode='w')
        p = pretty_formatter.PrettyFormatter(t, False, True)
        f = Mock()
        f.tags = ['spam', 'ham']
        f.keyword = u'k\xe9yword'
        f.name = 'name'
        f.location = 'location'
        f.description = 'description'
        p.feature(f)

