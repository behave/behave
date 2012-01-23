import logging
from logging.handlers import BufferingHandler
import re

from behave.configuration import ConfigError


class RecordFilter(object):
    '''Implement logging record filtering as per the configuration
    --logging-filter option.
    '''
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
class MemoryHandler(BufferingHandler):
    def __init__(self, config):
        BufferingHandler.__init__(self, 1000)

        self.config = config

        self.old_handlers = []

        # set my formatter
        fmt = datefmt = None
        if config.logging_format:
            fmt = config.logging_format
        else:
            fmt = '%(levelname)s:%(name)s:%(message)s'
        if config.logging_datefmt:
            datefmt = config.logging_datefmt
        fmt = logging.Formatter(fmt, datefmt)
        self.setFormatter(fmt)

        # figure the level we're logging at
        if config.logging_level:
            self.level = getattr(logging, config.logging_level.upper(),
                None)
            if self.level is None:
                raise ConfigError('Invalid log level: "%s"' %
                    config.logging_level)
        else:
            self.level = logging.NOTSET

        # construct my filter
        if config.logging_filter:
            self.addFilter(RecordFilter(config.logging_filter))

    def __nonzero__(self):
        return bool(self.buffer)

    def flush(self):
        pass  # do nothing

    def truncate(self):
        self.buffer = []

    def getvalue(self):
        return '\n'.join(self.formatter.format(r) for r in self.buffer)

    def findEvent(self, pattern):
        pattern = re.compile(pattern)
        for record in self.buffer:
            if pattern.search(record.getMessage()) is not None:
                return True
        return False

    def any_errors(self):
        return any(record for record in self.buffer
            if record.levelname in ('ERROR', 'CRITICAL'))

    def inveigle(self):
        root_logger = logging.getLogger()

        if self.config.logging_clear_handlers:
            # kill off all the other log handlers
            for logger in logging.Logger.manager.loggerDict.values():
                if hasattr(logger, "handlers"):
                    for handler in logger.handlers:
                        self.old_handlers.append((logger, handler))
                        logger.removeHandler(handler)

        # sanity check: remove any existing MemoryHandler
        for handler in root_logger.handlers[:]:
            if isinstance(handler, MemoryHandler):
                root_logger.handlers.remove(handler)
            elif self.config.logging_clear_handlers:
                self.old_handlers.append((root_logger, handler))
                root_logger.removeHandler(handler)

        # right, we're it now
        root_logger.addHandler(self)

        # capture the level we're interested in
        root_logger.setLevel(self.level)

    def abandon(self):
        root_logger = logging.getLogger()
        for handler in root_logger.handlers[:]:
            if handler is self:
                root_logger.handlers.remove(handler)

        if self.config.logging_clear_handlers:
            for logger, handler in self.old_handlers:
                logger.addHandler(handler)


def capture(func):
    '''Decorator to wrap an *environment file function* in log file capture.

    It configures the logging capture using the *behave* context - the first
    argument to the function being decorated (so don't use this to decorate
    something that doesn't have *context* as the first argument.)

    The function prints any captured logging directly to stdout, regardless of
    error conditions. It is mostly useful for debugging in situations where
    you are seeing a message like::

        No handlers could be found for logger "name"

    '''
    def f(context, *args):
        h = MemoryHandler(context.config)
        h.inveigle()
        try:
            func(context, *args)
        finally:
            h.abandon()
        v = h.getvalue()
        if v:
            print 'Captured Logging:'
            print v
    return f
