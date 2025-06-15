# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function
from logging.handlers import BufferingHandler
import logging
import functools
import re

from behave.log_config import (
    LoggingConfigurator as _LoggingConfigurator
)


# -----------------------------------------------------------------------------
# CLASSES
# -----------------------------------------------------------------------------
class RecordFilter(object):
    """Implement logging record filtering as per the configuration
    --logging-filter option.
    """
    def __init__(self, names):
        self.include = set()
        self.exclude = set()
        for name in names.split(','):
            if name[0] == '-':
                self.exclude.add(name[1:])
            else:
                self.include.add(name)

    def filter(self, record):
        if self.exclude:
            return record.name not in self.exclude
        return record.name in self.include


# originally from nostetsts logcapture plugin
class LoggingCapture(BufferingHandler):
    """Capture logging events in a memory buffer for later display or query.

    Captured logging events are stored on the attribute
    :attr:`~LoggingCapture.buffer`:

    .. attribute:: buffer

       This is a list of captured logging events as `logging.LogRecords`_.

    .. _`logging.LogRecords`:
       https://docs.python.org/3/library/logging.html#logrecord-objects

    By default the format of the messages will be::

        '%(levelname)s:%(name)s:%(message)s'

    This may be overridden using standard logging formatter names in the
    configuration variable ``logging_format``.

    The level of logging captured is set to ``logging.NOTSET`` by default. You
    may override this using the configuration setting ``logging_level`` (which
    is set to a level name.)

    Finally there may be `filtering of logging events`__ specified by the
    configuration variable ``logging_filter``.

    .. __: behave.html#command-line-arguments
    """
    DEFAULT_FORMAT = "LOG.%(levelname)s:%(name)s:%(message)s"

    def __init__(self, config, level=None):
        BufferingHandler.__init__(self, 1000)
        self.config = config
        self.old_handlers = []
        self.old_level = None

        # -- STEP: Create log-formatter
        log_format = self.DEFAULT_FORMAT
        if config.logging_format:
            log_format = config.logging_format
        log_datefmt = None
        if config.logging_datefmt:
            log_datefmt = config.logging_datefmt

        configurator = _LoggingConfigurator(config)
        formatter = configurator.make_formatter(log_format, log_datefmt)
        self.setFormatter(formatter)

        # figure the level we're logging at
        if level is not None:
            self.level = level
        elif config.logging_level:
            self.level = config.logging_level
        else:
            self.level = logging.NOTSET

        # construct my filter
        if config.logging_filter:
            self.addFilter(RecordFilter(config.logging_filter))

    def clear_buffer(self):
        # -- SINCE: behave v1.2.7
        self.buffer = []

    def __bool__(self):
        return bool(self.buffer)

    def flush(self):
        pass  # do nothing

    def truncate(self):
        self.buffer = []

    def getvalue(self):
        return '\n'.join(self.formatter.format(r) for r in self.buffer)

    def find_event(self, pattern):
        """Search through the buffer for a message that matches the given
        regular expression.

        Returns boolean indicating whether a match was found.
        """
        pattern = re.compile(pattern)
        for record in self.buffer:
            if pattern.search(record.getMessage()) is not None:
                return True
        return False

    def any_errors(self):
        """Search through the buffer for any ERROR or CRITICAL events.

        Returns boolean indicating whether a match was found.
        """
        return any(record for record in self.buffer
                   if record.levelname in ('ERROR', 'CRITICAL'))

    def inveigle(self):
        """Turn on logging capture by replacing all existing handlers
        configured in the logging module.

        If the config var logging_clear_handlers is set then we also remove
        all existing handlers.

        We also set the level of the root logger.

        The opposite of this is :meth:`~LoggingCapture.abandon`.
        """
        root_logger = logging.getLogger()
        if self.config.logging_clear_handlers:
            # kill off all the other log handlers
            for logger in logging.Logger.manager.loggerDict.values():
                if hasattr(logger, "handlers"):
                    for handler in logger.handlers:
                        self.old_handlers.append((logger, handler))
                        logger.removeHandler(handler)

        # sanity check: remove any existing LoggingCapture
        for handler in root_logger.handlers[:]:
            if isinstance(handler, LoggingCapture):
                root_logger.handlers.remove(handler)
            elif self.config.logging_clear_handlers:
                self.old_handlers.append((root_logger, handler))
                root_logger.removeHandler(handler)

        # right, we're it now
        root_logger.addHandler(self)

        # capture the level we're interested in
        self.old_level = root_logger.level
        root_logger.setLevel(self.level)

    def abandon(self):
        """Turn off logging capture.

        If other handlers were removed by :meth:`~LoggingCapture.inveigle` then
        they are reinstated.
        """
        root_logger = logging.getLogger()
        for handler in root_logger.handlers[:]:
            if handler is self:
                root_logger.handlers.remove(handler)

        if self.config.logging_clear_handlers:
            for logger, handler in self.old_handlers:
                logger.addHandler(handler)

        if self.old_level is not None:
            # -- RESTORE: Old log.level before inveigle() was used.
            root_logger.setLevel(self.old_level)
            self.old_level = None


def capture(*args, **kw):
    """
    Decorator to wrap an *environment file function* in log file capture.

    It configures the logging capture using the *behave* context,
    the first argument to the function being decorated
    (so don't use this to decorate something that
    doesn't have *context* as the first argument).

    The basic usage is:

    .. code-block: python

        @capture
        def before_scenario(context, scenario):
            ...

        @capture(show_on_success=True)
        def after_scenario(context, scenario):
            ...

    .. tip:: Use :func:`behave.capture.capture_output` decorator instead.

        Supports capturing of any-output.

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
    show_on_success = kw.pop("show_on_success", capture.show_on_success)
    def create_decorator(func, level=None):
        def f(context, *args):
            h = LoggingCapture(context.config, level=level)
            h.inveigle()
            failed = False
            try:
                func(context, *args)
            except Exception as e:
                failed = True
                logger = logging.getLogger("behave.run")
                logger.exception(e)
                raise
            finally:
                h.abandon()
                captured_output = h.getvalue()
                should_show = failed or show_on_success
                if should_show and captured_output:
                    print("CAPTURED LOG:")
                    print(captured_output)
        return f

    if not args:
        # -- CASE: @capture(level=...)
        return functools.partial(create_decorator, level=kw.get("level"))
    else:
        # -- CASE: @capture
        return create_decorator(args[0])

capture.show_on_success = False
