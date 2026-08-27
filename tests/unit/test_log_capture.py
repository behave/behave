import logging
from unittest.mock import patch
from behave.log_capture import LoggingCapture, capture


class TestLogCapture:
    def test_capture_preserves_function_name(self):
        @capture
        def before_scenario(context, scenario):
            pass

        assert before_scenario.__name__ == "before_scenario"

    def test_capture_with_kwargs_preserves_function_name(self):
        @capture(level=logging.ERROR)
        def after_scenario(context, scenario):
            pass

        assert after_scenario.__name__ == "after_scenario"

    def test_get_value_returns_all_log_records(self):
        class FakeConfig:
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

            assert handler.getvalue() == expected

            calls = [args[0][0] for args in format.call_args_list]
            assert calls == fake_records
