from unittest.mock import patch
from behave.log_capture import LoggingCapture


class TestLogCapture:
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


class TestNestedLogCapture:
    """A hook (like: before_scenario) is captured while the capture of its
    scenario is active. The scenario must get its log output afterwards.
    """

    class FakeConfig:
        logging_filter = None
        logging_format = None
        logging_datefmt = None
        logging_level = None
        logging_clear_handlers = False

    @staticmethod
    def restore_root_logger(root_logger, handlers, level):
        root_logger.handlers[:] = handlers
        root_logger.setLevel(level)

    def test_outer_capture_is_reinstated_after_nested_capture(self):
        import logging
        root_logger = logging.getLogger()
        old_handlers, old_level = root_logger.handlers[:], root_logger.level
        logger = logging.getLogger("behave.test_nested_log_capture")
        outer = LoggingCapture(self.FakeConfig(), level=logging.INFO)
        inner = LoggingCapture(self.FakeConfig(), level=logging.INFO)
        try:
            outer.inveigle()
            logger.info("OUTER_1: before hook")
            inner.inveigle()            # -- HOOK: Nested capture starts.
            logger.info("INNER: in hook")
            inner.abandon()             # -- HOOK: Nested capture ends.
            logger.info("OUTER_2: step after hook")
            outer.abandon()
            logger.info("NOT CAPTURED: after abandon")
        finally:
            self.restore_root_logger(root_logger, old_handlers, old_level)

        assert "INNER: in hook" in inner.getvalue()
        assert "OUTER_1: before hook" in outer.getvalue()
        assert "OUTER_2: step after hook" in outer.getvalue()   # -- REGRESSION
        assert "INNER" not in outer.getvalue()
        assert "NOT CAPTURED" not in outer.getvalue()
        assert outer not in root_logger.handlers
        assert inner not in root_logger.handlers

    def test_abandoned_capture_is_not_reinstated(self):
        # -- SEQUENCE: Scenario 1 ends (abandon), then scenario 2 starts.
        import logging
        root_logger = logging.getLogger()
        old_handlers, old_level = root_logger.handlers[:], root_logger.level
        first = LoggingCapture(self.FakeConfig(), level=logging.INFO)
        second = LoggingCapture(self.FakeConfig(), level=logging.INFO)
        try:
            first.inveigle()
            first.abandon()
            second.inveigle()
            second.abandon()
            assert first not in root_logger.handlers
            assert second.displaced_captures == []
        finally:
            self.restore_root_logger(root_logger, old_handlers, old_level)

    def test_capture_that_was_abandoned_meanwhile_is_not_reinstated(self):
        # -- REGRESSION: A dead log handler stayed on the root logger
        # (and captured log records for the rest of the process).
        import logging
        root_logger = logging.getLogger()
        old_handlers, old_level = root_logger.handlers[:], root_logger.level
        outer = LoggingCapture(self.FakeConfig(), level=logging.INFO)
        inner = LoggingCapture(self.FakeConfig(), level=logging.INFO)
        try:
            outer.inveigle()
            inner.inveigle()    # -- DISPLACES: outer
            outer.abandon()     # -- MEANWHILE: outer is given up.
            inner.abandon()
            assert outer not in root_logger.handlers
            assert not outer.active and not inner.active
        finally:
            self.restore_root_logger(root_logger, old_handlers, old_level)
