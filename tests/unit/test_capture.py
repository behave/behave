# -*- coding: UTF-8 -*-
"""
Unittests for :mod:`behave.capture` module.
"""

from __future__ import absolute_import, print_function
import sys
import pytest

from behave.capture import (
    Captured, CaptureBookmark, CaptureController, ManyCaptured,
    NO_CAPTURED_DATA
)
from behave.configuration import Configuration
# DISABLED: from behave4cmd0.failing_steps import then_it_should_fail_because


# -----------------------------------------------------------------------------
# TEST SUPPORT:
# -----------------------------------------------------------------------------
def create_capture_controller(config=None):
    if not config:
        config_data = dict(
            capture=True,
            captur_stdoute=True,
            capture_stderr=True,
            capture_log=True,
            capture_hooks=True,
            logging_filter = None,
            logging_level = "INFO",
            logging_format = "LOG_%(levelname)s:%(name)s: %(message)s",
            logging_datefmt = None,
        )
        config = Configuration(load_config=False, **config_data)
    return CaptureController(config)


# -----------------------------------------------------------------------------
# FIXTURES:
# -----------------------------------------------------------------------------
@pytest.fixture
def capture_controller():
    """Provides a capture_controller that is already setup and automatically
    performs a teardown afterwards.
    """
    capture_controller = create_capture_controller()
    capture_controller.setup_capture()
    yield capture_controller
    # -- CLEANUP:
    capture_controller.teardown_capture()

# -- PYTEST MARKERS:
todo = pytest.mark.todo()
not_implemented = pytest.mark.not_implemented()


# -----------------------------------------------------------------------------
# TEST SUITE:
# -----------------------------------------------------------------------------
class TestCaptured(object):

    def test_default_ctor(self):
        captured = Captured()
        assert captured.stdout == u""
        assert captured.stderr == u""
        assert captured.log == u""
        assert not captured

    def test_ctor_with_params(self):
        captured = Captured(u"Alice", u"Bob", u"Charly")
        assert captured.stdout == u"Alice"
        assert captured.stderr == u"Bob"
        assert captured.log == u"Charly"

        captured = Captured(stdout=u"Alice")
        assert captured.stdout == u"Alice"
        assert captured.stderr == u""
        assert captured.log == u""

        captured = Captured(stderr=u"Bob")
        assert captured.stdout == u""
        assert captured.stderr == u"Bob"
        assert captured.log == u""

        captured = Captured(log=u"Charly")
        assert captured.stdout == u""
        assert captured.stderr == u""
        assert captured.log == u"Charly"

    def test_reset(self):
        captured = Captured("STDOUT", "STDERR", "LOG_OUTPUT")
        captured.reset()
        assert captured.stdout == u""
        assert captured.stderr == u""
        assert captured.log == u""
        assert not captured

    def test_bool_conversion__returns_false_without_captured_output(self):
        captured = Captured()
        assert bool(captured) is False
        assert bool(captured.stdout) == captured.has_output()

    @pytest.mark.parametrize("params", [
        dict(stdout="xxx"),
        dict(stderr="yyy"),
        dict(log="zzz"),
        dict(stderr="yyy", log="zzz"),
        dict(stdout="xxx", stderr="yyy", log="zzz"),
    ])
    def test_bool_conversion__returns_true_with_captured_output(self, params):
        captured = Captured(**params)
        actual = bool(captured)
        assert actual
        assert actual == captured.has_output()

    @pytest.mark.parametrize("params, expected", [
        (dict(), ""),
        (dict(stdout="Otto"), "Otto"),
        (dict(stderr="Eric"), "Eric"),
        (dict(log="Ludwig"), "Ludwig"),
        (dict(stdout="Otto", stderr="Eric"),
            "Otto\nEric"),
        (dict(stdout="Otto", log="Ludwig"),
            "Otto\nLudwig"),
        (dict(stdout="Otto", stderr="Eric", log="Ludwig"),
            "Otto\nEric\nLudwig"),
    ])
    def test_output__contains_output_part(self, params, expected):
        captured = Captured(**params)
        assert captured.output == expected

    @pytest.mark.parametrize("params, expected", [
        (dict(), ""),
        (dict(stdout="STDOUT"), "STDOUT"),
        (dict(stderr="STDERR"), "STDERR"),
        (dict(log="LOG_OUTPUT"), "LOG_OUTPUT"),
        (dict(stdout="STDOUT", stderr="STDERR"), "STDOUT\nSTDERR"),
        (dict(stdout="STDOUT", log="LOG_OUTPUT"), "STDOUT\nLOG_OUTPUT"),
        (dict(stdout="STDOUT", stderr="STDERR", log="LOG_OUTPUT"),
         "STDOUT\nSTDERR\nLOG_OUTPUT"),
    ])
    def test_output__contains_concatenated_parts(self, params, expected):
        captured = Captured(**params)
        assert captured.output == expected


    @pytest.mark.parametrize("params, expected", [
        (dict(), ""),
        (dict(stdout="Otto"), "CAPTURED STDOUT:\nOtto"),
        (dict(stderr="Eric"), "CAPTURED STDERR:\nEric"),
        (dict(log="Ludwig"), "CAPTURED LOG:\nLudwig"),
        (dict(stdout="Otto", stderr="Eric"),
            "CAPTURED STDOUT:\nOtto\n\nCAPTURED STDERR:\nEric"),
        (dict(stdout="Otto", log="Ludwig"),
            "CAPTURED STDOUT:\nOtto\n\nCAPTURED LOG:\nLudwig"),
        (dict(stdout="Otto", stderr="Eric", log="Ludwig"),
            "CAPTURED STDOUT:\nOtto\n\nCAPTURED STDERR:\nEric\n\nCAPTURED LOG:\nLudwig"),
    ])
    def test_make_simple_report_contains_basic_captured_report(self, params, expected):
        captured = Captured(**params)
        simple_report = captured.make_simple_report()
        assert simple_report == expected

    @pytest.mark.parametrize("params, expected", [
        (dict(), ""),
        (dict(stdout="Otto"), """
----
CAPTURED STDOUT:
Otto
----
""".strip()),
        (dict(stderr="Eric"), """
----
CAPTURED STDERR:
Eric
----
""".strip()),
        (dict(log="Ludwig"), """
----
CAPTURED LOG:
Ludwig
----
""".strip()),
        (dict(stdout="Otto", stderr="Eric"), """
----
CAPTURED STDOUT:
Otto

CAPTURED STDERR:
Eric
----
""".strip()),
        (dict(stdout="Otto", log="Ludwig"), """
----
CAPTURED STDOUT:
Otto

CAPTURED LOG:
Ludwig
----
""".strip()),
        (dict(stdout="Otto", stderr="Eric", log="Ludwig"), """
----
CAPTURED STDOUT:
Otto

CAPTURED STDERR:
Eric

CAPTURED LOG:
Ludwig
----
""".strip()),
    ])
    def test_make_report__contains_captured_report(self, params, expected):
        captured = Captured(**params)
        report = captured.make_report()
        assert report == expected

    def test_make_report__contains_simple_report(self):
        captured = Captured(stdout="Otto", stderr="Eric", log="Ludwig")
        simple_report = captured.make_simple_report()
        report = captured.make_report()
        assert simple_report in report

        bounded_parts = report.replace(simple_report, "", 1)
        assert bounded_parts == "----\n\n----"

    def test_make_report__with_template(self):
        captured = Captured(stdout="Otto", stderr="Eric", log="Ludwig")
        template = """
__CAPTURED_OUTPUT: {this.status} ________
{output}
__CAPTURED_OUTPUT_END____________________
""".strip()
        expected = """
__CAPTURED_OUTPUT: OK ________
CAPTURED STDOUT:
Otto

CAPTURED STDERR:
Eric

CAPTURED LOG:
Ludwig
__CAPTURED_OUTPUT_END____________________
""".strip()

        report = captured.make_report(template=template)
        assert report == expected

    def test_make_report__with_name(self):
        captured = Captured(name="charly", stdout="Otto", stderr="Eric")
        expected = """
----
CAPTURED STDOUT: charly
Otto

CAPTURED STDERR: charly
Eric
----
    """.strip()
        report = captured.make_report()
        assert report == expected

    def test_add_to__without_this_captured_data(self):
        captured1 = Captured()
        captured2 = Captured("STDOUT", "STDERR", "LOG_OUTPUT")
        captured1.add_to(captured2)
        assert captured1.stdout == "STDOUT"
        assert captured1.stderr == "STDERR"
        assert captured1.log == "LOG_OUTPUT"

    def test_add_to__without_other_captured_data(self):
        captured1 = Captured("STDOUT", "STDERR", "LOG_OUTPUT")
        captured2 = Captured()
        captured1.add_to(captured2)
        assert captured1.stdout == "STDOUT"
        assert captured1.stderr == "STDERR"
        assert captured1.log == "LOG_OUTPUT"

    def test_add_to__with_captured_data(self):
        captured1 = Captured("stdout1", "stderr1", "log_output1")
        captured2 = Captured("STDOUT2", "STDERR2", "LOG_OUTPUT2")

        captured1.add_to(captured2)
        assert captured1.stdout == "stdout1\nSTDOUT2"
        assert captured1.stderr == "stderr1\nSTDERR2"
        assert captured1.log == "log_output1\nLOG_OUTPUT2"

    def test_make_report__with_all_sections(self):
        captured = Captured(stdout="Alice", stderr="Bob", log="Charly")
        expected_text = """\
CAPTURED STDOUT:
Alice

CAPTURED STDERR:
Bob

CAPTURED LOG:
Charly
""".strip()
        expected = Captured.REPORT_TEMPLATE.format(output=expected_text)
        assert captured.make_report() == expected

    def test_make_report__should_only_contain_nonempty_data_sections(self):
        captured1 = Captured(stdout="Alice")
        expected_text = "CAPTURED STDOUT:\nAlice"
        expected = Captured.REPORT_TEMPLATE.format(output=expected_text)
        assert captured1.make_report() == expected

        captured2 = Captured(stderr="Bob")
        expected_text = "CAPTURED STDERR:\nBob"
        expected = Captured.REPORT_TEMPLATE.format(output=expected_text)
        assert captured2.make_report() == expected

        captured3 = Captured(log="Charly")
        expected_text = "CAPTURED LOG:\nCharly"
        expected = Captured.REPORT_TEMPLATE.format(output=expected_text)
        assert captured3.make_report() == expected


class TestManyCapture(object):
    def test_add_captured__with_empty_captured_data(self):
        captured = Captured()
        collector = ManyCaptured()
        collector.add_captured(captured)
        assert collector.has_output() is False
        assert len(collector.captures) == 0
        assert collector.output == ""

    def test_add_captured__with_some_captured_data(self):
        captured = Captured(stdout="Alice", stderr="Bob", log="Charly")
        collector = ManyCaptured()
        collector.add_captured(captured)
        assert collector.has_output() is True
        assert len(collector.captures) == 1
        assert collector.output == "Alice\nBob\nCharly"

    def test_add_captured__two_with_same_name_are_merged(self):
        captured1 = Captured(stdout="Alice", stderr="Bob", log="Charly")
        captured2 = Captured(stdout="Doro", stderr="Emily", log="Fred")
        collector = ManyCaptured()
        collector.add_captured(captured1)
        collector.add_captured(captured2)
        assert collector.has_output() is True
        assert len(collector.captures) == 1
        assert collector.output == "Alice\nDoro\nBob\nEmily\nCharly\nFred"
        assert collector.stdout == "Alice\nDoro"
        assert collector.stderr == "Bob\nEmily"
        assert collector.log == "Charly\nFred"

    def test_add_captured__two_with_other_names_are_added(self):
        captured1 = Captured(name="C1", stdout="Alice", stderr="Bob", log="Charly")
        captured2 = Captured(name="C2", stdout="Doro", stderr="Emily", log="Fred")
        collector = ManyCaptured()
        collector.add_captured(captured1)
        collector.add_captured(captured2)
        assert collector.has_output() is True
        assert len(collector.captures) == 2
        assert collector.output == "Alice\nBob\nCharly\n----\nDoro\nEmily\nFred"
        assert collector.stdout == "Alice\nDoro"
        assert collector.stderr == "Bob\nEmily"
        assert collector.log == "Charly\nFred"

    def test_make_report__with_empty_captured_data(self):
        captured = Captured()
        collector = ManyCaptured()
        collector.add_captured(captured)
        report = collector.make_report()
        assert report == u""

    def test_make_report__with_some_captured_data(self):
        captured = Captured(stdout="Alice", stderr="Bob", log="Charly")
        collector = ManyCaptured()
        collector.add_captured(captured)
        report = collector.make_report()
        expected = u"""
----
CAPTURED STDOUT:
Alice

CAPTURED STDERR:
Bob

CAPTURED LOG:
Charly
----
""".strip()
        assert report == expected

    def test_make_report__two_with_same_name_are_merged(self):
        captured1 = Captured(stdout="Alice", stderr="Bob", log="Charly")
        captured2 = Captured(stdout="Doro", stderr="Emily", log="Fred")
        collector = ManyCaptured()
        collector.add_captured(captured1)
        collector.add_captured(captured2)
        report = collector.make_report()
        expected = u"""
----
CAPTURED STDOUT:
Alice
Doro

CAPTURED STDERR:
Bob
Emily

CAPTURED LOG:
Charly
Fred
----
""".strip()
        assert report == expected

    def test_make_report__two_with_other_names_are_added(self):
        captured1 = Captured(name="C1", stdout="Alice", stderr="Bob", log="Charly")
        captured2 = Captured(name="C2", stdout="Doro", stderr="Emily", log="Fred")
        collector = ManyCaptured()
        collector.add_captured(captured1)
        collector.add_captured(captured2)
        report = collector.make_report()
        expected = u"""
----
CAPTURED STDOUT: C1
Alice

CAPTURED STDERR: C1
Bob

CAPTURED LOG: C1
Charly
----
CAPTURED STDOUT: C2
Doro

CAPTURED STDERR: C2
Emily

CAPTURED LOG: C2
Fred
----
""".strip()
        assert report == expected


class Theory4ActiveCaptureController(object):
    @staticmethod
    def check_invariants(controller):
        if controller.config.capture_stdout:
            assert controller.capture_stdout is not None
            assert sys.stdout is controller.capture_stdout
        else:
            assert controller.capture_stdout is None
            assert sys.stdout is not controller.capture_stdout

        if controller.config.capture_stderr:
            assert controller.capture_stderr is not None
            assert sys.stderr is controller.capture_stderr
        else:
            assert controller.capture_stderr is None
            assert sys.stderr is not controller.capture_stderr

        if controller.config.capture_log:
            assert controller.capture_log is not None
        else:
            assert controller.capture_log is None

class TestCaptureBookmark(object):
    def test_ctor__with_default_values(self):
        bookmark = CaptureBookmark()
        assert bookmark.offset_stdout == 0
        assert bookmark.offset_stderr == 0
        assert bookmark.offset_log == 0

    def test_ctor__with_values(self):
        bookmark = CaptureBookmark(1, 2, 3)
        assert bookmark.offset_stdout == 1
        assert bookmark.offset_stderr == 2
        assert bookmark.offset_log == 3

    def test_ctor__with_named_values(self):
        # -- OTHER PARAM-ORDERING:
        bookmark = CaptureBookmark(offset_log=1, offset_stdout=2, offset_stderr=3)
        assert bookmark.offset_stdout == 2
        assert bookmark.offset_stderr == 3
        assert bookmark.offset_log == 1

    def test_from_captured__with_no_captured_data(self):
        captured = Captured()
        bookmark = CaptureBookmark.from_captured(captured)
        assert bookmark == CaptureBookmark(0, 0, 0)

    def test_from_captured__with_some_captured_data(self):
        captured = Captured(stdout="Alice", stderr="Bob", log="Charly")
        bookmark = CaptureBookmark.from_captured(captured)
        assert bookmark == CaptureBookmark(5, 3, 6)

    def test_make_captured_since__with_empty_captured(self):
        captured1 = Captured()
        captured2 = Captured()

        # -- WHEN: I make bookmark.make_captured_since(...)
        bookmark = CaptureBookmark.from_captured(captured1)
        captured_delta = bookmark.make_captured_since(captured2)

        # -- THEN: I check the captured output
        assert not captured_delta.has_output()
        assert captured_delta is NO_CAPTURED_DATA

    def test_make_captured_since__with_unchanged_captured(self):
        captured1 = Captured(stdout="Alice", stderr="Bob", log="Charly")
        captured2 = Captured(stdout="Alice", stderr="Bob", log="Charly")

        # -- WHEN: I make bookmark.make_captured_since(...)
        bookmark = CaptureBookmark.from_captured(captured1)
        captured_delta = bookmark.make_captured_since(captured2)

        # -- THEN: I check the captured output
        assert not captured_delta.has_output()
        assert captured_delta is NO_CAPTURED_DATA

    def test_make_captured_since__with_changed_captured(self):
        captured1 = Captured(stdout="Alice", stderr="Bob\n", log="Charly")
        captured2 = Captured(stdout="AliceDoro", stderr="Bob\nEmily", log="CharlyFred")

        # -- WHEN: I make bookmark.make_captured_since(...)
        bookmark = CaptureBookmark.from_captured(captured1)
        captured_delta = bookmark.make_captured_since(captured2)

        # -- THEN: I check the captured output
        part_separator = "\n____\n"
        captured_output = captured_delta.make_output(separator=part_separator)
        expected = Captured(stdout="Doro", stderr="Emily", log="Fred")
        expected_output = expected.make_output(separator=part_separator)
        assert captured_output == expected_output

    def test_make_captured_since__with_unrelated_bookmark(self):
        captured = Captured(stdout="Alice", stderr="Bob\n", log="Charly")

        # -- WHEN: the bookmark refers to other captured w/ more data
        bad_bookmark = CaptureBookmark(11, 12, 13)
        captured_delta = bad_bookmark.make_captured_since(captured)

        # -- THEN: I check the captured output
        assert not captured_delta.has_output()
        assert captured_delta is NO_CAPTURED_DATA


class TestCaptureController(object):

    # @pytest.no_capture
    def test_basics_using_stdfd(self):
        # XXX AVOID: Due to pytest capture mode
        # Theory4ActiveCaptureController.check_invariants(capture_controller)
        capture_controller = create_capture_controller()
        capture_controller.setup_capture()
        capture_controller.start_capture()
        sys.stdout.write("HELLO\n")
        sys.stderr.write("world\n")
        capture_controller.stop_capture()
        assert capture_controller.captured.output == "HELLO\nworld"
        assert capture_controller.captured.stdout == "HELLO\n"
        assert capture_controller.captured.stderr == "world\n"

        # -- FINALLY:
        capture_controller.teardown_capture()

    def test_basics_using_print(self):
        capture_controller = create_capture_controller()
        capture_controller.setup_capture()
        capture_controller.start_capture()
        print("HELLO")
        print("world", file=sys.stderr)
        capture_controller.stop_capture()
        capture_controller.teardown_capture()  # -- EARLY
        assert capture_controller.captured.output == "HELLO\nworld"
        assert capture_controller.captured.stdout == "HELLO\n"
        assert capture_controller.captured.stderr == "world\n"

    def test_use_captured_before_stop(self):
        capture_controller = create_capture_controller()
        capture_controller.setup_capture()
        capture_controller.start_capture()
        print("HELLO")
        print("world", file=sys.stderr)

        this_captured = capture_controller.captured
        assert this_captured.output == "HELLO\nworld"
        assert this_captured.stdout == "HELLO\n"
        assert this_captured.stderr == "world\n"
        # -- FINALLY:
        capture_controller.stop_capture()
        capture_controller.teardown_capture()

    def test_use_captured_after_stop(self):
        capture_controller = create_capture_controller()
        capture_controller.setup_capture()
        capture_controller.start_capture()
        print("HELLO")
        print("world", file=sys.stderr)

        capture_controller.stop_capture()
        this_captured = capture_controller.captured
        assert this_captured.output == "HELLO\nworld"
        assert this_captured.stdout == "HELLO\n"
        assert this_captured.stderr == "world\n"
        # -- FINALLY:
        capture_controller.teardown_capture()

    def test_use_captured_after_teardown(self):
        capture_controller = create_capture_controller()
        capture_controller.setup_capture()
        capture_controller.start_capture()
        print("HELLO")
        print("world", file=sys.stderr)

        capture_controller.stop_capture()
        capture_controller.teardown_capture()
        this_captured = capture_controller.captured
        assert this_captured.output == "HELLO\nworld"
        assert this_captured.stdout == "HELLO\n"
        assert this_captured.stderr == "world\n"


    def test_captured__is_accumulating(self, capture_controller):
        capture_controller.start_capture()
        print("HELLO")
        print("Alice", file=sys.stderr)
        this_captured1 = capture_controller.captured
        assert this_captured1.output == "HELLO\nAlice"
        assert this_captured1.stdout == "HELLO\n"
        assert this_captured1.stderr == "Alice\n"

        print("MORE_1")
        print("MORE_2", file=sys.stderr)
        this_captured2 = capture_controller.captured
        assert this_captured2.output == "HELLO\nMORE_1\nAlice\nMORE_2"
        assert not this_captured2.output.startswith(this_captured1.output)
        assert this_captured2.stdout.startswith(this_captured1.stdout)
        assert this_captured2.stderr.startswith(this_captured1.stderr)
        capture_controller.stop_capture()

    def test_captured__with_several_start_stop_cycles(self, capture_controller):
        capture_controller.start_capture()
        print("HELLO")
        print("Alice", file=sys.stderr)
        capture_controller.stop_capture()
        assert capture_controller.captured.output == "HELLO\nAlice"

        print("__UNCAPTURED:stdout;")
        print("__UNCAPTURED:stderr;", file=sys.stderr)

        capture_controller.start_capture()
        print("Sam")
        print("Bob", file=sys.stderr)
        capture_controller.stop_capture()
        this_captured = capture_controller.captured
        assert this_captured.output == "HELLO\nSam\nAlice\nBob"
        assert "__UNCAPTURED" not in this_captured.output

    def test_make_captured_delta__is_not_accumulating(self, capture_controller):
        capture_controller.start_capture()
        print("HELLO")
        print("Alice", file=sys.stderr)
        this_captured1 = capture_controller.make_captured_delta()
        assert this_captured1.output == "HELLO\nAlice"
        assert this_captured1.stdout == "HELLO\n"
        assert this_captured1.stderr == "Alice\n"

        print("MORE_1")
        print("MORE_2", file=sys.stderr)
        this_captured2 = capture_controller.make_captured_delta()
        assert this_captured2.output == "MORE_1\nMORE_2"
        assert not this_captured2.output.startswith(this_captured1.output)
        assert not this_captured2.stdout.startswith(this_captured1.stdout)
        assert not this_captured2.stderr.startswith(this_captured1.stderr)
        capture_controller.stop_capture()

    def test_make_captured_delta__without_output(self, capture_controller):
        capture_controller.start_capture()
        this_captured = capture_controller.make_captured_delta()
        assert this_captured.output == u""
        assert not this_captured.has_output()
        assert this_captured is NO_CAPTURED_DATA

    def test_make_captured_delta__with_unchanged_output(self, capture_controller):
        capture_controller.start_capture()
        print("HELLO Alice")
        this_captured1 = capture_controller.make_captured_delta()
        assert this_captured1.has_output()
        assert this_captured1.output == u"HELLO Alice"

        # -- WHEN: I create another captured_delta
        this_captured2 = capture_controller.make_captured_delta()

        # -- THEN: this captured_delta contains NO_OUTPUT and is NO_CAPTURED_OUTPUT
        assert not this_captured2.has_output()
        assert this_captured2 is NO_CAPTURED_DATA
        assert this_captured2.output == u""

    def test_make_captured_delta__with_changed_output(self, capture_controller):
        capture_controller.start_capture()
        print("Hello Alice")
        this_captured1 = capture_controller.make_captured_delta()
        assert this_captured1.has_output()
        assert this_captured1.output == u"Hello Alice"

        # -- WHEN: I create another captured_delta after other output was captured
        print("Ciao Bob")
        this_captured2 = capture_controller.make_captured_delta(name="C2",
                                                                failed=True)

        # -- THEN: this captured_delta contains NO_OUTPUT and is NO_CAPTURED_OUTPUT
        assert this_captured2.output == u"Ciao Bob"
        assert this_captured2.name == "C2"
        assert this_captured2.failed is True
        assert this_captured2.has_output()
        assert this_captured2 is not NO_CAPTURED_DATA

    def test_make_bookmark__without_output(self, capture_controller):
        capture_controller.start_capture()
        bookmark = capture_controller.make_bookmark()
        assert bookmark == CaptureBookmark(0, 0, 0)

    def test_make_bookmark__without_changed_output(self, capture_controller):
        capture_controller.start_capture()
        print("Hello ALice")
        bookmark1 = capture_controller.make_bookmark()
        assert bookmark1 != CaptureBookmark()

        bookmark2 = capture_controller.make_bookmark()
        assert bookmark2 == bookmark1

    def test_make_bookmark__with_changed_output(self, capture_controller):
        capture_controller.start_capture()
        print("Hello ALice")
        bookmark1 = capture_controller.make_bookmark()

        # -- WHEN: the captured output changes and I make another bookmark
        print("Hello ALice")
        bookmark2 = capture_controller.make_bookmark()

        # -- THEN: The bookmark differs from the first bookmark
        assert bookmark2 != bookmark1

    def test_make_captured_since__without_output(self, capture_controller):
        capture_controller.start_capture()
        bookmark = capture_controller.make_bookmark()
        captured = capture_controller.make_captured_since(bookmark)
        assert not captured.has_output()
        assert captured is NO_CAPTURED_DATA

    def test_make_captured_since__without_changed_output(self, capture_controller):
        capture_controller.start_capture()
        print("Hello ALice")

        bookmark = capture_controller.make_bookmark()
        captured = capture_controller.make_captured_since(bookmark)
        assert not captured.has_output()
        assert captured is NO_CAPTURED_DATA

    def test_make_captured_since__with_changed_output(self, capture_controller):
        capture_controller.start_capture()
        print("Hello ALice")
        bookmark = capture_controller.make_bookmark()

        # -- WHEN: more output is captured and I make captured since the bookmark.
        print("Ciao Bob")
        captured = capture_controller.make_captured_since(bookmark,
                                                          name="C2",
                                                          failed=True)

        # -- THEN: The captured contains the new output
        assert captured.has_output()
        assert captured.output == u"Ciao Bob"
        assert captured.name == "C2"
        assert captured.failed is True
        assert captured is not NO_CAPTURED_DATA

@todo
@not_implemented
class TestCaptureSinkAsCollector(object):
    pass

@todo
@not_implemented
class TestCaptureSink2Print(object):
    pass

@todo
@not_implemented
class TestCaptureOutputToSink(object):
    pass

@todo
@not_implemented
class TestCaptureOutputDecorator(object):
    pass
