from nose.tools import *

from behave.log_capture import MemoryHandler

class TestLogCapture(object):
    def test_get_value_returns_all_log_records(self):
        class FakeRecord(object):
            def __init__(self, name, levelname, message):
                self.name = name
                self.levelname = levelname
                self.getMessage = lambda: message

        records = [
            ('name', 'levelname', 'message'),
            ('othername', 'otherlevelname', 'othermessage')
        ]
        expected = '\n'.join("%s %s %s" % record for record in records)

        handler = MemoryHandler()
        handler.buffer = [FakeRecord(*record) for record in records]

        eq_(handler.getvalue(), expected)
