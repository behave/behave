# -*- coding: utf-8 -*-
# pylint: disable=C0103,C0301,R0201,W0212,W0401,W0614
#   C0103   Invalid name (setUp(), ...)
#   C0301   Line too long
#   R0201   Method could be a function
#   W0401   Wildcard import
#   W0614   Unused import ... from wildcard import

from __future__ import with_statement

from nose.tools import *
from mock import patch
from behave.log_capture import LoggingCapture
import unittest

class TestLogCapture(unittest.TestCase):
    def test_get_value_returns_all_log_records(self):
        __pychecker__ = "no-shadowbuiltin unusednames=x"
        class FakeConfig(object):
            logging_filter = None
            logging_format = None
            logging_datefmt = None
            logging_level = None

        fake_records = [object() for x in range(0, 10)]

        handler = LoggingCapture(FakeConfig())
        handler.buffer = fake_records

        # pylint: disable=W0622
        #   W0622   Redefining built-in format
        with patch.object(handler.formatter, 'format') as format:
            format.return_value = 'foo'
            expected = '\n'.join(['foo'] * len(fake_records))

            eq_(handler.getvalue(), expected)

            calls = [args[0][0] for args in format.call_args_list]
            eq_(calls, fake_records)
