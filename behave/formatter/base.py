# -*- coding: UTF-8 -*-
from __future__ import absolute_import, print_function
import codecs
import os.path
from behave.formatter.api import IFormatter
from behave.textutil import (
    select_best_encoding,
    ensure_stream_with_encoder as _ensure_stream_with_encoder
)


# -----------------------------------------------------------------------------
# FORMATTER HELPER CLASSES
# -----------------------------------------------------------------------------
class StreamOpener(object):
    """Provides a transport vehicle to open the formatter output stream
    when the formatter needs it.
    In addition, it provides the formatter with more control:

      * when a stream is opened
      * if a stream is opened at all
      * the name (filename/dirname) of the output stream
      * let it decide if directory mode is used instead of file mode
    """
    # FORMER: default_encoding = "UTF-8"
    default_encoding = select_best_encoding()

    def __init__(self, filename=None, stream=None, encoding=None):
        if not encoding:
            encoding = self.default_encoding
        if stream:
            stream = self.ensure_stream_with_encoder(stream, encoding)
        self.name = filename
        self.stream = stream
        self.encoding = encoding
        self.should_close_stream = not stream   # Only for not pre-opened ones.

    @staticmethod
    def ensure_dir_exists(directory):
        if directory and not os.path.isdir(directory):
            os.makedirs(directory)

    @classmethod
    def ensure_stream_with_encoder(cls, stream, encoding=None):
        return _ensure_stream_with_encoder(stream, encoding)

    def open(self):
        if not self.stream or self.stream.closed:
            self.ensure_dir_exists(os.path.dirname(self.name))
            # -- DISABLED:
            #   stream = open(self.name, "w")
            stream = codecs.open(self.name, "w", encoding=self.encoding)
            stream = self.ensure_stream_with_encoder(stream, self.encoding)
            self.stream = stream  # -- Keep stream for house-keeping.
            self.should_close_stream = True
            assert self.should_close_stream
        return self.stream

    def close(self):
        """
        Close the stream, if it was opened by this stream_opener.
        Skip closing for sys.stdout and pre-opened streams.
        :return: True, if stream was closed.
        """
        closed = False
        if self.stream and self.should_close_stream:
            closed = getattr(self.stream, "closed", False)
            if not closed:
                self.stream.close()
                closed = True
            self.stream = None
        return closed


# -----------------------------------------------------------------------------
# FORMATTER BASE CLASSES
# -----------------------------------------------------------------------------
class Formatter(IFormatter):
    """
    Base class for formatters  that use the :class:`IFormatter` interface.

    A formatter is an extension point (variation point) for the runner logic.
    A formatter is called while processing model elements.

    .. seealso:: :class:`IFormatter`
    """
    name = None
    description = None

    def __init__(self, stream_opener, config):
        super(Formatter, self).__init__()
        self.stream_opener = stream_opener
        self.stream = stream_opener.stream
        self.config = config

    # -- SPECIFIC PARTS:
    @property
    def stdout_mode(self):
        return not self.stream_opener.name

    def open(self):
        """
        Ensure that the output stream is open.
        Triggers the stream opener protocol (if necessary).

        :return: Output stream to use (just opened or already open).
        """
        if not self.stream:
            self.stream = self.stream_opener.open()
        return self.stream

    def close_stream(self):
        """Close the stream, but only if this is needed.
        This step is skipped if the stream is sys.stdout.
        """
        if self.stream:
            # -- DELEGATE STREAM-CLOSING: To stream_opener
            assert self.stream is self.stream_opener.stream
            self.stream_opener.close()
        self.stream = None      # -- MARK CLOSED.

    # -- INTERFACE FOR: behave.formatter.api.IFormatter
    def close(self):
        """
        Called before the formatter is no longer used
        (as stream/io compatibility).
        """
        self.close_stream()

