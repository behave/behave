# -*- coding: UTF-8 -*-
"""
Capture output (like: stdout, stderr, log output).

* :class:`CaptureController`: Coordinates the output capture.
* :class:`Captured`: Stores the captured output (as result).
* :class:`ManyCaptured`: Stored/collects many captured outputs (as result).
* :class:`ICaptureSink`: CaptureSink interface for processing captured data.
"""

from __future__ import absolute_import, print_function
from contextlib import contextmanager
import sys
import warnings

from six import StringIO, PY2

from behave._types import require_type
from behave.constant import (
    CAPTURE_SINK_STORE_CAPTURED_ON_SUCCESS,
    CAPTURE_SINK_SHOW_CAPTURED_ON_SUCCESS,
)
from behave.log_capture import LoggingCapture
from behave.textutil import text as _text


# -----------------------------------------------------------------------------
# UTILITY FUNCTIONS
# -----------------------------------------------------------------------------
def add_text_to(value, more_text, separator="\n"):
    if more_text:
        if value:
            if separator and not value.endswith(separator):
                value += separator
            value += more_text
        else:
            value = more_text
    return value


# -----------------------------------------------------------------------------
# CAPTURED CLASSES as VALUE OBJECTS
# -----------------------------------------------------------------------------
class ICaptured(object):
    """MARKER-CLASS for any Captured class (as value object)."""


class NoCaptured(ICaptured):
    __slots__ = [
        "stdout", "stderr", "log", "name",
        "failed", "status", "output"
    ]
    def __init__(self):
        # -- NON_SETTABLE ATTRIBUTE-PROTOCOL:
        for param in ("stdout", "stderr", "log", "output"):
            super(NoCaptured, self).__setattr__(param, u"")
        super(NoCaptured, self).__setattr__("name", None)
        super(NoCaptured, self).__setattr__("failed", False)
        super(NoCaptured, self).__setattr__("status", "EMPTY")

    def __setattr__(self, name, value):
        raise AttributeError("READ-ONLY: {}".format(name))  # noqa

    def has_output(self):
        return False  # noqa

    def make_output(self, **kwargs):
        return u""  # noqa

    def make_report(self, template=None, separator=None):
       return u""  #noqa

    def make_simple_report(self, separator=None):
        return self.make_report()  # noqa


# -- CONSTANT: For NO_CAPTURED_DATA
NO_CAPTURED_DATA = NoCaptured()



class Captured(ICaptured):
    """Immutable data structure that stores the snapshot of captured output."""
    __slots__ = [
        "stdout", "stderr", "log", "name", "failed", "_output",
    ]
    # -- REPORT-PLACEHOLDERS: this=captured, output
    REPORT_TEMPLATE = u"----\n{output}\n----"
    REPORT_TEMPLATE_SIMPLE = u"{output}"
    LINE_SEPARATOR = u"\n"
    CAPTURED_STDOUT_SCHEMA = u"CAPTURED STDOUT: {}"
    CAPTURED_STDERR_SCHEMA = u"CAPTURED STDERR: {}"
    CAPTURED_LOG_SCHEMA = u"CAPTURED LOG: {}"

    def __init__(self, stdout=None, stderr=None, log=None,
                 name=None, failed=False):
        self.name = name
        self.failed = failed
        self.stdout = stdout or u""
        self.stderr = stderr or u""
        self.log = log or u""
        self._output = None

    def reset(self):
        self.name = None
        self.failed = False
        self.stdout = u""
        self.stderr = u""
        self.log = u""
        self._reset_cached()

    def _reset_cached(self):
        self._output = None

    @property
    def status(self):
        this_status = "OK"
        if self.failed:
            this_status = "FAILED"
        return this_status

    @property
    def output(self):
        """Basic capture report of the captured output."""
        if self._output is None:
            # -- CACHED-PROPERTY: Compute once
            self._output = self.make_output()
        return self._output

    # @property
    # def any_output(self):
    #     """Simple concatenation of all captured output."""
    #     if self._any_output is None:
    #         # -- CACHED-PROPERTY: Compute once
    #         output_text = self.stdout
    #         output_text = add_text_to(output_text, self.stderr)
    #         output_text = add_text_to(output_text, self.log)
    #         self._any_output = output_text
    #     return self._any_output

    def can_merge(self, other):
        return self.name == other.name

    def add_to(self, other):
        if not isinstance(other, Captured):
            raise TypeError("{!r} (expected: Captured)".format(other))
        if self.name != other.name:
            raise ValueError("name mismatch: {} (expected: {})".format(
                       other.name, self.name))

        self.failed = self.failed or other.failed
        self.stdout = add_text_to(self.stdout, other.stdout)
        self.stderr = add_text_to(self.stderr, other.stderr)
        self.log = add_text_to(self.log, other.log)
        self._reset_cached()

    def make_output(self, separator=None):
        if not self.has_output():
            return u""

        # -- NOTE: Trailing whitespace is stripped from each part.
        parts = []
        if self.stdout:
            parts.append(self.stdout.rstrip())
        if self.stderr:
            parts.append(self.stderr.rstrip())
        if self.log:
            parts.append(self.log.rstrip())

        separator = separator or self.LINE_SEPARATOR
        output = separator.join(parts)
        return output

    def make_report(self, template=None):
        """
        Makes a detailed report of the captured output data.

        :returns: Report as string.
        """
        if not self.has_output():
            return u""

        # -- STEP: Collect report parts
        parts = []
        if self.stdout:
            section = self.CAPTURED_STDOUT_SCHEMA.format(self.name or u"")
            parts.extend([section.rstrip(), _text(self.stdout).rstrip(), ""])
        if self.stderr:
            section = self.CAPTURED_STDERR_SCHEMA.format(self.name or u"")
            parts.extend([section.rstrip(), _text(self.stderr).rstrip(), ""])
        if self.log:
            section = self.CAPTURED_LOG_SCHEMA.format(self.name or u"")
            parts.extend([section.rstrip(), _text(self.log).rstrip(), ""])

        # -- STEP: Make report from report parts
        report_output = self.LINE_SEPARATOR.join(parts).rstrip()
        template = template or self.REPORT_TEMPLATE
        return template.format(output=report_output, this=self)

    def make_simple_report(self):
        this_template = self.REPORT_TEMPLATE_SIMPLE
        return self.make_report(this_template)

    # -- SINCE: behave v1.2.7
    def has_output(self):
        return bool(self.stdout or self.stderr or self.log)

    if PY2:
        # -- CONVERSION-TO-BOOL:
        def __nonzero__(self):
            return self.has_output()
    else:
        def __bool__(self):
            return self.has_output()

    def __repr__(self):
        this_output = self.output[:40]
        return '<{classname}: status={status}, output="{output}...">'.format(
            classname=self.__class__.__name__,
            status=self.status, output=this_output,
        )


class ManyCaptured(ICaptured):
    """Composite of many captured outputs."""
    __slots__ = [
        "captures", "_output",
        # XXX_JE_CHECK_IF_NEEDED
        "_stdout", "_stderr", "_log"
    ]
    LINE_SEPARATOR = u"\n"
    PART_SEPARATOR = u"\n----\n"

    def __init__(self, captures=None):
        self.captures = captures or []
        self._output = None
        self._stdout = None
        self._stderr = None
        self._log = None

    def _reset_cached(self):
        self._output = None
        self._stdout = None
        self._stderr = None
        self._log = None

    def _combine_output_for(self, name):
        parts = [getattr(x, name) for x in self.captures]
        return u"\n".join(parts)

    # -- SPECIAL:
    def add_captured(self, other, use_merge=True):
        if not other.has_output():
            return

        if isinstance(other, ManyCaptured):
            # -- EXTEND THIS CAPTURED FROM: other
            for captured_part in other.captures:
                self.add_captured(captured_part, use_merge=False)
            return
        # XXX-DISABLED: Temporarily -- Due to testing w/ Mocks
        # XXX: elif not isinstance(other, Captured):
        # XXX:    raise TypeError("{!r} (expected: Captured)".format(other))

        # -- NORMAL CASE:
        if self.captures:
            # -- MERGE CAPTURE: If possible
            last_captured = self.captures[-1]
            if use_merge and last_captured.can_merge(other):
                last_captured.add_to(other)
            else:
                self.captures.append(other)
        else:
            self.captures.append(other)
        self._reset_cached()

    def select_captures_by_status(self, use_any_status=False):
        return CapturedQuery.select_many_by_status(self.captures, use_any_status)

    def select_by_status(self, use_any_status):
        if use_any_status:
            return self

        selected = self.select_captures_by_status(use_any_status=use_any_status)
        if selected:
            return ManyCaptured(selected)
        return NO_CAPTURED_DATA

    def has_failed(self):
        for captured in self.captures:
            if captured.failed:
                return True
        return False

    def count_failed(self):
        return sum([1 for captured in self.captures if captured.failed])

    # -- CAPTURED API:
    @property
    def failed(self):
        return self.has_failed()

    @property
    def status(self):
        if not self.has_output():
            return "EMPTY"

        this_status = "OK"
        counts = self.count_failed()
        if counts == len(self.captures):
            this_status = "FAILED"
        elif counts > 0:
            this_status = "SOME_FAILED"
        return this_status

    # XXX_JE_CHECK_IF_NEEDED
    @property
    def stdout(self):
        if self._stdout is None:
            self._stdout = self._combine_output_for("stdout")
        return self._stdout

    # XXX_JE_CHECK_IF_NEEDED
    @property
    def stderr(self):
        if self._stderr is None:
            self._stderr = self._combine_output_for("stderr")
        return self._stderr

    # XXX_JE_CHECK_IF_NEEDED
    @property
    def log(self):
        if self._log is None:
            self._log = self._combine_output_for("log")
        return self._log

    @property
    def output(self):
        if self._output is None:
            self._output = self.make_output()
        return self._output

    def reset(self):
        self.captures = []
        self._reset_cached()

    def has_output(self):
        return len(self.captures) > 0

    def make_output(self, separator=None):
        if not self.has_output():
            return u""

        output_parts = [captured.make_output()
                        for captured in self.captures]
        separator = separator or self.PART_SEPARATOR
        return separator.join(output_parts)

    def make_report(self, template=None, separator=None):
        if not self.has_output():
            return u""

        # -- WITH OUTPUT:
        separator = separator or self.PART_SEPARATOR
        template = template or Captured.REPORT_TEMPLATE
        report_parts = [captured_part.make_simple_report()
                        for captured_part in self.captures]
        combined_output = separator.join(report_parts)
        return template.format(output=combined_output, this=self).rstrip()

    def make_simple_report(self, separator=None):
        this_template = Captured.REPORT_TEMPLATE_SIMPLE
        return self.make_report(this_template, separator=separator)

    # -- CONVERSION-TO-BOOL:
    if PY2:
        def __nonzero__(self):
            return self.has_output()
    else:
        def __bool__(self):
            return self.has_output()

    # -- SPECIFIC: ManyCaptured
    def __add__(self, other):
        cls = self.__class__
        if not isinstance(other, (cls, Captured)):
            msg = "{} (expected: Captured, ManyCaptured)".format(type(other))
            raise TypeError(msg)
        if not other.has_output():
            return self

        other_captures = getattr(other, "captures", None)
        if other_captures is None:
            other_captures = [other]
        return cls(self.captures + other_captures)

    def __iadd__(self, other):
        """Supports incremental add to this object."""
        if isinstance(other, Captured):
            self.add_captured(other)
            return self

        if not isinstance(other, ManyCaptured):
            msg = "{} (expected: Captured, ManyCaptured)".format(type(other))
            raise TypeError(msg)

        self.captures.extend(other.captures)
        return self

    def __repr__(self):
        return "<ManyCaptured: size={size}, failed.count={failed_count}>".format(
            size=len(self.captures), failed_count=self.count_failed()
        )


# -----------------------------------------------------------------------------
# CAPTURED HELPER CLASSES
# -----------------------------------------------------------------------------
# XXX_MAYBE: use_any_status=True
class CapturedQuery(object):
    @staticmethod
    def select_by_status(captured, use_any_status=False):
        if captured.failed or use_any_status:
            return captured
        # -- OTHERWISE:
        return None

    @classmethod
    def select_many_by_status(cls, captures, use_any_status=False):
        selected = []
        for captured in captures:
            if cls.select_by_status(captured, use_any_status):
                selected.append(captured)
        return selected



# -----------------------------------------------------------------------------
# CAPTURE SINKS:
# -----------------------------------------------------------------------------
class ICaptureSink(object):
    def process_captured(self, captured):
        raise NotImplementedError()


class CaptureSink2Null(ICaptureSink):
    """Provides the NULL pattern (Blackhole) for a CaptureSink."""
    def process_captured(self, captured):
        pass


class CaptureSinkAsCollector(ICaptureSink):
    """CaptureSink that collects and stores any captured output."""
    STORE_ON_SUCCESS = CAPTURE_SINK_STORE_CAPTURED_ON_SUCCESS

    def __init__(self, collector=None, store_on_success=None):
        if collector is None:
            collector = ManyCaptured()
        if store_on_success is None:
            store_on_success = self.STORE_ON_SUCCESS

        self.collector = collector
        self.store_on_success = store_on_success

    def process_captured(self, captured):
        if captured.failed or self.store_on_success:
            self.collector.add_captured(captured)

    def has_output(self):
        return self.collector.has_output()

    def make_output(self):
        return self.collector.make_output()

    def make_report(self):
        return self.collector.make_report()


class CaptureSink2Print(ICaptureSink):
    """
    Provides a :class:`CaptureSink` that prints captured output.
    """
    SHOW_ON_SUCCESS = CAPTURE_SINK_SHOW_CAPTURED_ON_SUCCESS

    def __init__(self, show_on_success=None):
        if show_on_success is None:
            show_on_success = self.SHOW_ON_SUCCESS
        self.show_on_success = show_on_success

    # -- INTERFACE FOR: ICaptureSink
    def process_captured(self, captured):
        self.print_captured_output(captured)

    # -- SPECIFIC INTERFACE:
    def should_print(self, captured):
        return (captured.has_output()
                and (captured.failed or self.show_on_success))

    def print_captured_output(self, captured):
        if not self.should_print(captured):
            return

        report_text = captured.make_report()
        assert report_text, "REQUIRES NON_EMPTY: %s;" % report_text
        print(report_text)


# -----------------------------------------------------------------------------
# CAPTURE CONTROLLERS:
# -----------------------------------------------------------------------------
class CaptureBookmark(object):
    """Provides a reference point in time what was captured until now."""
    __slots__ = ("offset_stdout", "offset_stderr", "offset_log")

    def __init__(self, offset_stdout=0, offset_stderr=0, offset_log=0):
        self.offset_stdout = offset_stdout
        self.offset_stderr = offset_stderr
        self.offset_log = offset_log

    def make_captured_since(self, captured):
        """
        Make captured data since this bookmark.

        :param captured:  Current captured data.
        :return: Captured data since this bookmark or NO_CAPTURED_DATA.
        """
        captured_stdout = captured.stdout[self.offset_stdout:]
        captured_stderr = captured.stderr[self.offset_stderr:]
        captured_log = captured.log[self.offset_log:]
        has_output = bool(captured_stdout or captured_stderr or captured_log)
        if not has_output:
            return NO_CAPTURED_DATA

        # -- CASE: Some captured output since this bookmark.
        return Captured(captured_stdout, captured_stderr, captured_log,
                        name=captured.name,
                        failed=captured.failed)

    @classmethod
    def from_captured(cls, captured):
        offset_stdout = len(captured.stdout)
        offset_stderr = len(captured.stderr)
        offset_log = len(captured.log)
        return cls(offset_stdout, offset_stderr, offset_log)

    # -- SPECIAL METHODS:
    def __repr__(self):
        return "<CaptureBookmark: stdout={}, stderr={}, log={}>".format(
            self.offset_stdout, self.offset_stderr, self.offset_log
        )

    def __eq__(self, other):
        if not isinstance(other, CaptureBookmark):
            raise TypeError("{!r} (expected: CaptureBookmark)".format(other))

        return (self.offset_stdout == other.offset_stdout
            and self.offset_stderr == other.offset_stderr
            and self.offset_log == other.offset_log
        )

    def __ne__(self, other):
        return not self.__eq__(other)



class CaptureController(object):
    """Simplifies the lifecycle to capture output from various sources."""

    def __init__(self, config, name=None):
        self.config = config
        self.name = name
        self.capture_stdout = None
        self.capture_stderr = None
        self.capture_log = None
        self.delta_bookmark = CaptureBookmark()
        self.old_stdout = None
        self.old_stderr = None

    def should_capture(self):
        return self.config.should_capture()

    def has_output(self):
        # -- MAYBE:
        if self.capture_log is not None:
            if self.capture_log.buffer:
                return True
        if self.capture_stdout is not None:
            if self.capture_stdout.getvalue():
                return True
        if self.capture_stderr is not None:
            if self.capture_stderr.getvalue():
                return True
        # -- OTHERWISE:
        return False

    def make_captured(self, failed=None, name=None):
        stdout = None
        stderr = None
        log = None
        if self.config.capture_stdout and self.capture_stdout:
            stdout = _text(self.capture_stdout.getvalue())
        if self.config.capture_stderr and self.capture_stderr:
            stderr = _text(self.capture_stderr.getvalue())
        if self.config.capture_log and self.capture_log:
            log = _text(self.capture_log.getvalue())

        has_output = bool(stdout or stderr or log)
        if not has_output:
            return NO_CAPTURED_DATA

        if name is None:
            name = self.name
        captured = Captured(stdout=stdout, stderr=stderr, log=log,
                            name=name, failed=failed)
        return captured

    def make_captured_since(self, bookmark, failed=None, name=None):
        # -- NOT-EFFICIENT, but SIMPLE
        captured = self.make_captured(failed=failed, name=name)
        return bookmark.make_captured_since(captured)

    def make_captured_delta(self, failed=None, name=None):
        """
        Provides captured data that was captured since the last call to:

        * :method:`~behave.capture:CaptureController.make_captured()`
        * :method:`~behave.capture:CaptureController.make_captured_delta()`
        """
        # -- NOT-EFFICIENT, but SIMPLE:
        captured = self.make_captured(failed=failed, name=name)
        if captured is NO_CAPTURED_DATA:
            return NO_CAPTURED_DATA

        captured_delta = self.delta_bookmark.make_captured_since(captured)
        if captured_delta is NO_CAPTURED_DATA:
            return NO_CAPTURED_DATA

        self.delta_bookmark = CaptureBookmark.from_captured(captured)
        return captured_delta

    def make_bookmark(self):
        """
        Store the current captured offsets as bookmark.

        A bookmark can be referenced in :meth:`make_captured_since()` or
        can be used in :meth:`CaptureBookmark.make_captured_since()`
        to determine what was captured since this bookmark was created.

        :return: Bookmark object (as :class:`CaptureBookmark`).
        """
        captured = self.make_captured()
        return CaptureBookmark.from_captured(captured)

    def update_delta_bookmark(self):
        self.delta_bookmark = self.make_bookmark()

    @property
    def captured(self):
        """Provides access of the captured output data.

        :return: Object that stores the captured output parts (as Captured).
        """
        return self.make_captured()

    def setup_capture(self, context=None, name=None):
        # -- SINCE: behave v1.2.7 -- IGNORED: context param
        if context is not None:
            warnings.warn("setup_capture: Avoid to use 'context' parameter",
                          DeprecationWarning, stacklevel=3)
        if name is not None:
            self.name = name

        if self.config.capture_stdout:
            # XXX: if self.capture_stdout is not None:
            # XXX:     self.capture_stdout.close()
            self.capture_stdout = StringIO()
        if self.config.capture_stderr:
            # XXX: if self.capture_stderr is not None:
            # XXX:     self.capture_stderr.close()
            self.capture_stderr = StringIO()
        if self.config.capture_log:
            self.capture_log = LoggingCapture(self.config)
            self.capture_log.inveigle()
        self._stdout_offset = 0
        self._stderr_offset = 0
        self._log_offset = 0

    def start_capture(self):
        if self.config.capture_stdout:
            # -- REPLACE ONLY: In non-capturing mode.
            if not self.old_stdout:
                self.old_stdout = sys.stdout
                sys.stdout = self.capture_stdout
            assert sys.stdout is self.capture_stdout

        if self.config.capture_stderr:
            # -- REPLACE ONLY: In non-capturing mode.
            if not self.old_stderr:
                self.old_stderr = sys.stderr
                sys.stderr = self.capture_stderr
            assert sys.stderr is self.capture_stderr

    def stop_capture(self):
        if self.config.capture_stdout:
            # -- RESTORE ONLY: In capturing mode.
            if self.old_stdout:
                sys.stdout = self.old_stdout
                self.old_stdout = None
            assert sys.stdout is not self.capture_stdout

        if self.config.capture_stderr:
            # -- RESTORE ONLY: In capturing mode.
            if self.old_stderr:
                sys.stderr = self.old_stderr
                self.old_stderr = None
            assert sys.stderr is not self.capture_stderr

    def teardown_capture(self):
        # -- DISABLED DUE TO: Support .getvalue() after teardown.
        # if self.capture_stdout is not None:
        #     self.capture_stdout.close()
        #     self.capture_stdout = None
        # if self.capture_stderr is not None:
        #     self.capture_stderr.close()
        #     self.capture_stderr = None
        if self.config.capture_log and self.capture_log is not None:
            self.capture_log.abandon()

    # -- SINCE: behave v1.2.7
    def setup_and_start_capture(self):
        self.setup_capture()
        self.start_capture()

    def stop_and_teardown_capture(self):
        self.stop_capture()
        self.teardown_capture()

    # -- DISABLED:
    # def restart_capture(self):
    #     # XXX_JE_NOTE: Cornercase CHECKS are MISSING -- State handling
    #     # self.stop_capture()
    #     if self.config.capture_stdout and self.capture_stdout:
    #         self.capture_stdout.close()
    #         self.capture_stdout = StringIO()
    #         # sys.stdout = self.capture_stdout
    #     if self.config.capture_stderr and self.capture_stderr:
    #         self.capture_stderr.close()
    #         self.capture_stderr = StringIO()
    #         # sys.stderr = self.capture_stderr
    #     if self.config.capture_log and self.capture_log:
    #         self.capture_log.clear_buffer()
    #     # self.start_capture()

    # -- DEPRECATED CONFIG PARAMETER NAMES:
    # DEPRECATED SINCE: behave v1.2.7
    # REMOVED IN: behave v1.4.0
    @property
    def stdout_capture(self):
        warnings.warn("Use 'capture_stdout' instead", DeprecationWarning)
        return self.capture_stdout

    @stdout_capture.setter
    def stdout_capture(self, value):
        warnings.warn("Use 'capture_stdout = ...' instead", DeprecationWarning)
        self.capture_stdout = value

    @property
    def stderr_capture(self):
        warnings.warn("Use 'capture_stderr' instead", DeprecationWarning)
        return self.capture_stderr

    @stderr_capture.setter
    def stderr_capture(self, value):
        warnings.warn("Use 'capture_stderr = ...' instead", DeprecationWarning)
        self.capture_stderr = value

    @property
    def log_capture(self):
        warnings.warn("Use 'capture_log' instead", DeprecationWarning)
        return self.capture_log

    @log_capture.setter
    def log_capture(self, value):
        warnings.warn("Use 'capture_log = ...' instead", DeprecationWarning)
        self.capture_log = value


class CaptureControllerWithResult(CaptureController):
    def __init__(self, config, name=None):
        super(CaptureControllerWithResult, self).__init__(config, name=name)
        self.result_failed = False




# -----------------------------------------------------------------------------
# UTILITY FUNCTIONS:
# -----------------------------------------------------------------------------
@contextmanager
def capture_output_with_controller(controller, enabled=True):
    """Provides a context manager that starts capturing output

    .. code-block::

        with capture_output(capture_controller):
            ... # Do something
    """
    # -- XXX_JE_CHECK_IF_REALLY_NEEDED
    if enabled:
        try:
            controller.start_capture()
            yield
        finally:
            controller.stop_capture()
    else:
        # -- CAPTURING OUTPUT is disabled.
        # Needed to prevent recursive captures with context.execute_steps()
        yield


class AnyHook:
    # XXX_JE_CLEANUP
    # __slots__ = (
    #     "show_capture_on_success",
    #     "show_cleanup_on_success"
    # )
    show_capture_on_success = False
    show_cleanup_on_success = False

any_hook = AnyHook()




@contextmanager
def capture_output_to_sink(config,
                           capture_sink=None, capture_sink2=None,
                           name=None, show_on_success=False,
                           suppress_error=None):
    """
    Provides a context manager that captures output in a scope
    and delegates any captured output to a capture sink.

    .. code-block::

        with capture_output_to_sink(config):
            ... # Do something
    """
    from .configuration import Configuration
    require_type(config, Configuration)
    if capture_sink is None:
        capture_sink = CaptureSink2Print(show_on_success=show_on_success)

    controller = CaptureControllerWithResult(config, name=name)
    controller.setup_and_start_capture()
    failed = False
    try:
        yield controller
    except (KeyboardInterrupt, SystemExit, Exception) as e:
        failed = True
        if suppress_error is None or not isinstance(e, suppress_error):
            raise
    finally:
        has_failed = failed or controller.result_failed
        controller.stop_and_teardown_capture()
        captured = controller.make_captured(failed=has_failed)
        capture_sink.process_captured(captured)
        if capture_sink2 is not None:
            capture_sink2.process_captured(captured)


def capture_output(*args, **kwargs):
    """
    xxx
    Decorator to wrap an *environment file function* in log file capture.

    It configures the logging capture using the *behave* context,
    the first argument to the function being decorated
    (so don't use this to decorate something that
    doesn't have *context* as the first argument).

    The basic usage is:

    .. code-block: python

        from behave.capture import capture_output
        import logging

        @capture_output(show_on_success=True, level=logging.WARNING)
        def before_all(ctx, scenario):
            pass

        @capture_output
        def some_function(...):
            pass

    XXX_JE_TODO
    The function prints any captured logging
    (at the level determined by the ``log_level`` configuration setting)
    directly to stdout, regardless of error conditions.

    It is mostly useful for debugging in situations where you are seeing a
    message like::

        No handlers could be found for logger "name"

    The decorator takes an optional "level" keyword argument which limits the
    level of logging captured, overriding the level in the run's configuration:

    .. code-block: python

        @capture(level=logging.ERROR)
        def after_scenario(context, scenario):
            ...

    This would limit the logging captured to just ERROR and above,
    and thus only display logged events if they are interesting.

    :param level:   Logging level threshold to use.
    :param show_on_success:  Use true, to always show captured log records.

    .. versionchanged:: 1.2.7

        Log records are now only shown if an error occurs or ``show_on_success`` is true.

        * Use ``capture.show_on_success = True`` to enable the old behavior.
        * Parameter ``show_on_success : bool = CAPTURE_SHOW_ON_SUCCESS`` was added.`
    """
    # XXX_PROBLEM: capture_output decorator should work w/ capture=True, independent of config
    name = kwargs.pop("name", None)
    show_on_success = kwargs.pop("show_on_success", capture_output.show_on_success)
    suppress_error = kwargs.pop("suppress_error", None)
    capture_kwargs = dict(name=name,
                          show_on_success=show_on_success,
                          suppress_error=suppress_error)

    def create_decorator(func, level=None):
        def f(ctx, *args):
            capture_sink = getattr(ctx._runner, "capture_sink", None)
            with capture_output_to_sink(ctx.config,
                                        capture_sink2=capture_sink,
                                        **capture_kwargs):
                func(ctx, *args)
        return f

    if not args:
        # -- CASE: @capture(level=...)
        import functools
        return functools.partial(create_decorator, level=kwargs.get("level"))
    else:
        # -- CASE: @capture
        return create_decorator(args[0])

capture_output.show_on_success = False
