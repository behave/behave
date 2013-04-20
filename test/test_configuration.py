from __future__ import with_statement
import os.path
import tempfile

from nose.tools import *
from behave import configuration

# one entry of each kind handled
TEST_CONFIG='''[behave]
outfiles= /absolute/path1
          relative/path2
paths = /absolute/path3
        relative/path4
tags = @foo,~@bar
       @zap
format=pretty
       tag-counter
stdout_capture=no
bogus=spam
'''

class TestConfiguration(object):

    def test_read_file(self):
        tn = tempfile.mktemp()
        tndir = os.path.dirname(tn)
        with open(tn, 'w') as f:
            f.write(TEST_CONFIG)

        d = configuration.read_configuration(tn)
        eq_(d['outfiles'], [
            os.path.normpath('/absolute/path1'),
            os.path.normpath(os.path.join(tndir, 'relative/path2')),
        ])
        eq_(d['paths'], [
            os.path.normpath('/absolute/path3'),  # -- WINDOWS-REQUIRES: normpath
            os.path.normpath(os.path.join(tndir, 'relative/path4')),
            ])
        eq_(d['format'], ['pretty', 'tag-counter'])
        eq_(d['tags'], ['@foo,~@bar', '@zap'])
        eq_(d['stdout_capture'], False)
        ok_('bogus' not in d)

