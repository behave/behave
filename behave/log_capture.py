
import logging
from logging.handlers import BufferingHandler

# from nostetsts logcapture plugin
# filter for specific log destinations by adding to .filters
class MemoryHandler(BufferingHandler):
    def __init__(self):
        BufferingHandler.__init__(self, 1000)
        fmt = logging.Formatter()
        self.setFormatter(fmt)
        self.filters = []
        self.old_handlers = []

    def __nonzero__(self):
        return bool(self.buffer)

    def flush(self):
        pass # do nothing

    def truncate(self):
        self.buffer = []

    def filter(self, record):
        """Our custom record filtering logic.

        Built-in filtering logic (via logging.Filter) is too limiting.
        """
        if not self.filters:
            return True
        matched = False
        rname = record.name # shortcut
        for name in self.filters:
            if rname == name or rname.startswith(name+'.'):
                matched = True
        return matched

    def getvalue(self):
        return '\n'.join('%s %s %s' % (record.name, record.levelname, record.getMessage())
            for record in self.buffer)

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
        # kill off all the other log handlers
        for logger in logging.Logger.manager.loggerDict.values():
            if hasattr(logger, "handlers"):
                for handler in logger.handlers:
                    self.old_handlers.append((logger, handler))
                    logger.removeHandler(handler)

        root_logger = logging.getLogger()

        # sanity check: remove any existing MemoryHandler
        for handler in root_logger.handlers[:]:
            root_logger.handlers.remove(handler)
            if not isinstance(handler, MemoryHandler):
                self.old_handlers.append((root_logger, handler))

        # right, we're it now
        root_logger.addHandler(self)

        # to make sure everything gets captured
        root_logger.setLevel(logging.NOTSET)

    def abandon(self):
        for logger, handler in self.old_handlers:
            logger.addHandler(handler)

