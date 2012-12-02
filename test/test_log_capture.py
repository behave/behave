from __future__ import with_statement

from nose.tools import *
from mock import patch

from behave.log_capture import LoggingCapture

class TestLogCapture(object):
    def test_get_value_returns_all_log_records(self):
        class FakeConfig(object):
            logging_filter = None
            logging_format = None
            logging_datefmt = None
            logging_level = None

        fake_records = [object() for x in range(0, 10)]

        handler = LoggingCapture(FakeConfig())
        handler.buffer = fake_records

        with patch.object(handler.formatter, 'format') as format:
            format.return_value = 'foo'
            expected = '\n'.join(['foo'] * len(fake_records))

            eq_(handler.getvalue(), expected)

            calls = [args[0][0] for args in format.call_args_list]
            eq_(calls, fake_records)
