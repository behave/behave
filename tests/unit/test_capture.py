# -*- coding: UTF-8 -*-
"""
Unittests for :mod:`behave.capture` module.
"""

from __future__ import absolute_import, print_function
import sys
from behave.capture import Captured, CaptureController
from mock import Mock
import pytest

# -----------------------------------------------------------------------------
# TEST SUPPORT:
# -----------------------------------------------------------------------------
def create_capture_controller(config=None):
    if not config:
        config = Mock()
        config.stdout_capture = True
        config.stderr_capture = True
        config.log_capture = True
        config.logging_filter = None
        config.logging_level = "INFO"
    return CaptureController(config)

def setup_capture_controller(capture_controller, context=None):
    if not context:
        context = Mock()
    context.aborted = False
    context.config = capture_controller.config
    capture_controller.setup_capture(context)


# -----------------------------------------------------------------------------
# FIXTURES:
# -----------------------------------------------------------------------------
@pytest.fixture
def capture_controller():
    """Provides a capture_controller that is already setup and automatically
    performs a teardown afterwards.
    """
    capture_controller = create_capture_controller()
    setup_capture_controller(capture_controller)
    yield capture_controller
    # -- CLEANUP:
    capture_controller.teardown_capture()


# -----------------------------------------------------------------------------
# TEST SUITE:
# -----------------------------------------------------------------------------
class TestCaptured(object):

    def test_default_ctor(self):
        captured = Captured()
        assert captured.stdout == u""
        assert captured.stderr == u""
        assert captured.log_output == u""
        assert not captured

    def test_ctor_with_params(self):
        captured = Captured(u"STDOUT", u"STDERR", u"LOG_OUTPUT")
        assert captured.stdout == u"STDOUT"
        assert captured.stderr == u"STDERR"
        assert captured.log_output == u"LOG_OUTPUT"

        captured = Captured(stdout=u"STDOUT")
        assert captured.stdout == u"STDOUT"
        assert captured.stderr == u""
        assert captured.log_output == u""

        captured = Captured(stderr=u"STDERR")
        assert captured.stdout == u""
        assert captured.stderr == u"STDERR"
        assert captured.log_output == u""

        captured = Captured(log_output=u"LOG_OUTPUT")
        assert captured.stdout == u""
        assert captured.stderr == u""
        assert captured.log_output == u"LOG_OUTPUT"

    def test_reset(self):
        captured = Captured("STDOUT", "STDERR", "LOG_OUTPUT")
        captured.reset()
        assert captured.stdout == u""
        assert captured.stderr == u""
        assert captured.log_output == u""
        assert not captured

    def test_bool_conversion__returns_false_without_captured_output(self):
        captured = Captured()
        assert bool(captured) == False

    @pytest.mark.parametrize("params", [
        dict(stdout="xxx"),
        dict(stderr="yyy"),
        dict(log_output="zzz"),
        dict(stderr="yyy", log_output="zzz"),
        dict(stdout="xxx", stderr="yyy", log_output="zzz"),
    ])
    def test_bool_conversion__returns_true_with_captured_output(self, params):
        captured = Captured(**params)
        assert bool(captured)

    @pytest.mark.parametrize("params, expected", [
        (dict(), ""),
        (dict(stdout="STDOUT"), "STDOUT"),
        (dict(stderr="STDERR"), "STDERR"),
        (dict(log_output="LOG_OUTPUT"), "LOG_OUTPUT"),
        (dict(stdout="STDOUT", stderr="STDERR"), "STDOUT\nSTDERR"),
        (dict(stdout="STDOUT", log_output="LOG_OUTPUT"), "STDOUT\nLOG_OUTPUT"),
        (dict(stdout="STDOUT", stderr="STDERR", log_output="LOG_OUTPUT"),
         "STDOUT\nSTDERR\nLOG_OUTPUT"),
    ])
    def test_output__contains_concatenated_parts(self, params, expected):
        captured = Captured(**params)
        assert captured.output == expected

    def test_add__without_captured_data(self):
        captured1 = Captured()
        captured2 = Captured("STDOUT", "STDERR", "LOG_OUTPUT")
        captured1.add(captured2)
        assert captured1.stdout == "STDOUT"
        assert captured1.stderr == "STDERR"
        assert captured1.log_output == "LOG_OUTPUT"

    def test_add__with_captured_data(self):
        captured1 = Captured("stdout1", "stderr1", "log_output1")
        captured2 = Captured("STDOUT2", "STDERR2", "LOG_OUTPUT2")

        captured1.add(captured2)
        assert captured1.stdout == "stdout1\nSTDOUT2"
        assert captured1.stderr == "stderr1\nSTDERR2"
        assert captured1.log_output == "log_output1\nLOG_OUTPUT2"

    def test_operator_add(self):
        captured1 = Captured("stdout1", "stderr1", "log_output1")
        captured2 = Captured("STDOUT2", "STDERR2", "LOG_OUTPUT2")

        captured3 = captured1 + captured2
        assert captured3.stdout == "stdout1\nSTDOUT2"
        assert captured3.stderr == "stderr1\nSTDERR2"
        assert captured3.log_output == "log_output1\nLOG_OUTPUT2"
        # -- ENSURE: captured1 is not modified.
        assert captured1.stdout == "stdout1"
        assert captured1.stderr == "stderr1"
        assert captured1.log_output == "log_output1"
        # -- ENSURE: captured2 is not modified.
        assert captured2.stdout == "STDOUT2"
        assert captured2.stderr == "STDERR2"
        assert captured2.log_output == "LOG_OUTPUT2"

    def test_operator_iadd(self):
        captured1 = Captured("stdout1", "stderr1", "log_output1")
        captured2 = Captured("STDOUT2", "STDERR2", "LOG_OUTPUT2")

        captured1 += captured2
        assert captured1.stdout == "stdout1\nSTDOUT2"
        assert captured1.stderr == "stderr1\nSTDERR2"
        assert captured1.log_output == "log_output1\nLOG_OUTPUT2"
        # -- ENSURE: captured2 is not modified.
        assert captured2.stdout == "STDOUT2"
        assert captured2.stderr == "STDERR2"
        assert captured2.log_output == "LOG_OUTPUT2"

    def test_make_report__with_all_sections(self):
        captured = Captured(stdout="xxx", stderr="yyy", log_output="zzz")
        expected = """\
Captured stdout:
xxx

Captured stderr:
yyy

Captured logging:
zzz"""
        assert captured.make_report() == expected

    def test_make_report__should_only_contain_nonempty_data_sections(self):
        captured1 = Captured(stdout="xxx")
        expected = "Captured stdout:\nxxx"
        assert captured1.make_report() == expected

        captured2 = Captured(stderr="yyy")
        expected = "Captured stderr:\nyyy"
        assert captured2.make_report() == expected

        captured3 = Captured(log_output="zzz")
        expected = "Captured logging:\nzzz"
        assert captured3.make_report() == expected


class Theory4ActiveCaptureController(object):
    @staticmethod
    def check_invariants(controller):
        if controller.config.capture_stdout:
            assert controller.stdout_capture is not None
            assert sys.stdout is controller.stdout_capture
        else:
            assert controller.stdout_capture is None
            assert sys.stdout is not controller.stdout_capture

        if controller.config.capture_stderr:
            assert controller.stderr_capture is not None
            assert sys.stderr is controller.stderr_capture
        else:
            assert controller.stderr_capture is None
            assert sys.stderr is not controller.stderr_capture

        if controller.config.capture_log:
            assert controller.log_capture is not None
            # assert sys.stderr is controller.stderr_capture
        else:
            assert controller.log_capture is None
            # assert sys.stderr is not controller.stderr_capture


class TestCaptureController(object):

    # @pytest.no_capture
    def test_basics(self):
        capture_controller = create_capture_controller()
        context = Mock()
        context.aborted = False
        context.config = capture_controller.config

        capture_controller.setup_capture(context)
        # XXX AVOID: Due to pytest capture mode
        # Theory4ActiveCaptureController.check_invariants(capture_controller)

        capture_controller.start_capture()
        sys.stdout.write("HELLO\n")
        sys.stderr.write("world\n")
        capture_controller.stop_capture()
        assert capture_controller.captured.output == "HELLO\nworld\n"

        # -- FINALLY:
        capture_controller.teardown_capture()

    def test_capturing__retrieve_captured_several_times(self, capture_controller):
        capture_controller.start_capture()
        sys.stdout.write("HELLO\n")
        sys.stderr.write("Alice\n")
        assert capture_controller.captured.output == "HELLO\nAlice\n"

        print("Sam")
        sys.stderr.write("Bob\n")
        capture_controller.stop_capture()
        assert capture_controller.captured.output == "HELLO\nSam\nAlice\nBob\n"


    def test_capturing__with_several_start_stop_cycles(self, capture_controller):
        capture_controller.start_capture()
        sys.stdout.write("HELLO\n")
        sys.stderr.write("Alice\n")
        capture_controller.stop_capture()
        assert capture_controller.captured.output == "HELLO\nAlice\n"

        sys.stdout.write("__UNCAPTURED:stdout;\n")
        sys.stderr.write("__UNCAPTURED:stderr;\n")

        capture_controller.start_capture()
        sys.stdout.write("Sam\n")
        sys.stderr.write("Bob\n")
        capture_controller.stop_capture()
        assert capture_controller.captured.output == "HELLO\nSam\nAlice\nBob\n"


    def test_make_capture_report(self, capture_controller):
        capture_controller.start_capture()
        print("HELLO")
        sys.stderr.write("Alice\n")
        capture_controller.stop_capture()
        report = capture_controller.make_capture_report()
        expected = """\
Captured stdout:
HELLO

Captured stderr:
Alice"""
        assert report == expected
