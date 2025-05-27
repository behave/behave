"""
Thin adapter around the :mod:`logging` module.

Tries to overcome some of the setup/init problems of the logging subsystem:

* :func:`logging.basicConfig()` works only on first call
* :func:`logging.basicConfig(filename)` requires that no root.handlers exist
  which is not the case in :mod:`behave` (log-capture is used).
"""

from __future__ import absolute_import, print_function
import logging
import logging.config
import sys
from behave.textutil import text_encoding

# -----------------------------------------------------------------------------
# CONSTANTS
# -----------------------------------------------------------------------------
_PYTHON_VERSION = sys.version_info[:2]


# -----------------------------------------------------------------------------
# CLASSES
# -----------------------------------------------------------------------------
class LoggingConfigurator(object):
    DEFAULT_LEVEL = logging.INFO
    DEFAULT_FORMAT_STYLE = '%'

    def __init__(self, config):
        self.config = config

    # -- PUBLIC API:
    def configure_by_file(self, configfile, level=None, **kwargs):
        """Configure the logging subsystem by using a config-file."""
        logging.config.fileConfig(configfile, **kwargs)
        self.configure_level(level)

    def configure_file_sink(self, filename, level=None, format=None,
                            datefmt=None, **kwargs):
        # -- BASED-ON: logging.basicConfig()
        mode = kwargs.pop("filemode", "a")
        encoding = kwargs.pop("encoding", None)
        errors = kwargs.pop("errors", None)
        if "b" in mode:
            errors = None
        else:
            encoding = text_encoding(encoding)

        if errors and _PYTHON_VERSION >= (3, 9):
            # -- SINCE: PYTHON 3.9 -- logging.FileHandler(..., errors)
            kwargs["errors"] = errors
        handler = logging.FileHandler(filename, mode, encoding=encoding, **kwargs)

        format_ = format or self.config.logging_format
        datefmt = datefmt or self.config.logging_datefmt
        formatter = self.make_formatter(format_, datefmt)
        handler.setFormatter(formatter)
        root_logger = logging.getLogger()
        root_logger.addHandler(handler)
        self.configure_level(level)

    def configure_console_sink(self, level=None, format=None,
                            datefmt=None, **kwargs):
        if "filename" in kwargs:
            raise ValueError("filename (not allowed)")

        root_logger = logging.getLogger()
        already_configured = bool(len(root_logger.handlers) > 0)

        level = level or self.config.logging_level or self.DEFAULT_LEVEL
        format_ = format or self.config.logging_format
        datefmt_ = datefmt or self.config.logging_datefmt
        logging.basicConfig(level=level, format=format_, datefmt=datefmt_, **kwargs)
        self.configure_level(level)

        if already_configured and (format or datefmt):
            # -- ENSURE: Format params are applied.
            from behave.log_capture import LoggingCapture
            formatter = self.make_formatter(format, datefmt)
            for handler in root_logger.handlers:
                if isinstance(handler, (logging.StreamHandler, LoggingCapture)):
                    handler.setFormatter(formatter)

    def configure_level(self, level=None):
        # -- ENSURE: Default log level is set (even if logging is already configured).
        # Ressign to self.logging_level
        # NEEDED FOR: behave.log_capture.LoggingCapture
        level = level or self.config.logging_level or self.DEFAULT_LEVEL
        level = logging._checkLevel(level)
        logging.getLogger().setLevel(level)
        self.config.logging_level = level  # pylint: disable=W0201

    def make_formatter(self, format=None, datefmt=None):
        format_ = format or self.config.logging_format
        datefmt = datefmt or self.config.logging_datefmt
        if format_ and _PYTHON_VERSION >= (3, 2):
            # -- SINCE: Python 3.2 -- logging.Formatter(..., style)
            style = self.select_format_style(format_)
            return logging.Formatter(format_, datefmt, style)
        # -- OTHERWISE:
        return logging.Formatter(format_, datefmt)

    @classmethod
    def select_format_style(cls, format):
        """
        Discover log-format style by using the format.
        """
        # SEE: logging._STYLES
        if not format:
            return cls.DEFAULT_FORMAT_STYLE

        if "${message" in format:
            # -- SHELL PLACEHOLDER FORMAT STYLE = "${message}"
            return '$'
        elif "{message" in format:
            # -- F-STRING FORMAT STYLE = "{message}"
            return '{'

        # -- PERCENT FORMAT STYLE = "%(message)s"
        return cls.DEFAULT_FORMAT_STYLE
