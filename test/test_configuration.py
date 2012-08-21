# -*- coding: utf-8 -*-
# pylint: disable=C0103,R0201,W0401,W0614
#   C0103   Invalid name (setUp(), ...)
#   R0201   Method could be a function
#   W0401   Wildcard import
#   W0614   Unused import ... from wildcard import

from __future__ import with_statement
from test.testutil_tempfile import named_temporary_file
from nose.tools import *
from behave import configuration
import unittest

# one entry of each kind handled
TEST_CONFIG = '''[behave]
outfile=/tmp/spam
tags = @foo,~@bar
       @zap
format=pretty
       tag-counter
stdout_capture=no
bogus=spam
'''

class TestConfiguration(unittest.TestCase):

    def test_read_file(self):
        # XXX-JE-ORIG, DEPRECATED: mktemp()
        with named_temporary_file() as f:
            f.write(TEST_CONFIG)
            f.close()

            d = configuration.read_configuration(f.name)
            eq_(d['outfile'], '/tmp/spam')
            eq_(d['format'], ['pretty', 'tag-counter'])
            eq_(d['tags'], ['@foo,~@bar', '@zap'])
            eq_(d['stdout_capture'], False)
            ok_('bogus' not in d)

