#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This module provides pre-/post-processors for the mod:`behave4cmd0.command_shell`.
"""

from __future__ import absolute_import, print_function
import re
import sys
from six import string_types


# -----------------------------------------------------------------------------
# UTILITY:
# -----------------------------------------------------------------------------
def posixpath_normpath(filename):
    if not filename:
        return filename
    return filename.replace("\\", "/").replace("//", "/")


# -----------------------------------------------------------------------------
# LINE PROCESSORS:
# -----------------------------------------------------------------------------
class LineProcessor(object):
    """Function-like object that may perform text-line transformations."""
    def __init__(self, marker=None):
        self.marker = marker

    def reset(self):
        pass

    def __call__(self, text):
        return text


class TracebackLineNormalizer(LineProcessor):
    """Line processor that tries to normalize path lines in a traceback dump."""
    marker = "Traceback (most recent call last):"
    file_pattern = re.compile(r'\s\s+File "(?P<path>.*)", line .*')

    def __init__(self):
        super(TracebackLineNormalizer, self).__init__(self.marker)
        self.traceback_section = False

    def reset(self):
        self.traceback_section = False

    def __call__(self, line):
        """Process a line and optionally transform it.

        :param line: line to process (as text)
        :return: Same line or transformed/normalized line (as text).
        """
        marker = self.marker
        stripped_line = line.strip()
        if marker == stripped_line:
            assert not self.traceback_section
            self.traceback_section = True
            # print("XXX: TRACEBACK-START")
        elif self.traceback_section:
            matched = self.file_pattern.match(line)
            if matched:
                # matched_range = matched.regs[1]
                filename = matched.groups()[0]
                new_filename = posixpath_normpath(filename)
                if new_filename != filename:
                    # print("XXX: %r => %r" % (filename, new_filename))
                    line = line.replace(filename, new_filename)
            elif not stripped_line or line[0].isalpha():
                # -- DETECTED TRCAEBACK-END: exception-description
                # print("XXX: TRACEBACK-END")
                self.traceback_section = False
        return line


class ExceptionWithPathNormalizer(LineProcessor):
    """Normalize filename path in Exception line (for Windows)."""
    # http://myregexp.com/examples.html
    # Windows File Name Regexp
    # (?i) ^ (?! ^ (PRN | AUX | CLOCK\$ | NUL | CON | COM\d | LPT\d |\..* )(\..+)?$)
    # [ ^\\\./:\ * \?\"<>\|][^\\/:\*\?\"<>\|]{0,254}$
    problematic_path_patterns = [
        'ConfigError: No steps directory in "(?P<path>.*)"',
        'ParserError: Failed to parse "(?P<path>.*)"',
        "Error: [Errno 2] No such file or directory: '(?P<path>.*)'",
    ]

    def __init__(self, pattern, marker_text=None):
        super(ExceptionWithPathNormalizer, self).__init__(marker_text)
        self.pattern = re.compile(pattern, re.UNICODE)
        self.marker = marker_text

    def __call__(self, line):
        matched = self.pattern.search(line)
        if matched:
            # -- ONLY: One pattern per line should match.
            filename = matched.groupdict()["path"]
            new_filename = posixpath_normpath(filename)
            if new_filename != filename:
                line = line.replace(filename, new_filename)
        return line


# -----------------------------------------------------------------------------
# COMMAND OUTPUT PROCESSORS:
# -----------------------------------------------------------------------------
class CommandPostProcessor(object):
    """Syntactic sugar to mark a command post-processor."""


class CommandOutputProcessor(CommandPostProcessor):
    """Abstract base class functionality for a CommandPostProcessor that
    post-processes the output of a command.
    """
    enabled = True
    output_parts = ("stderr", "stdout")

    def __init__(self, enabled=None, output_parts=None):
        if enabled is None:
            # -- AUTO-DETECT: Enabled on Windows platform
            enabled = self.__class__.enabled
        if output_parts is None:
            output_parts = self.__class__.output_parts
        self.enabled = enabled
        self.output_parts = output_parts

    def matches_output(self, text):
        """Abstract method that should be overwritten."""
        # pylint: disable=no-self-use, unused-argument
        return False

    def process_output(self, text):   # pylint: disable=no-self-use
        """Abstract method that should be overwritten."""
        changed = False
        return changed, text

    def __call__(self, command_result):
        """Core functionality of command output processor.

        :param command_result:  As value object w/ command execution details.
        :return: Command result
        """
        if not self.enabled:
            return command_result

        changes = 0
        for output_name in self.output_parts:
            output = getattr(command_result, output_name)
            if output and self.matches_output(output):
                changed, new_output = self.process_output(output)
                if changed:
                    changes += 1
                    setattr(command_result, output_name, new_output)

        if changes:
            # -- RESET: Composite output
            # pylint: disable=protected-access
            command_result._output = None
        return command_result


class LineCommandOutputProcessor(CommandOutputProcessor):
    """Provides functionality to process text in line-oriented way by using
    a number of line processors. The line processors perform the actual work
    for transforming/normalizing the text.
    """
    enabled = True
    line_processors = [TracebackLineNormalizer()]

    def __init__(self, line_processors=None):
        if line_processors is None:
            line_processors = self.__class__.line_processors
        super(LineCommandOutputProcessor, self).__init__(self.enabled)
        self.line_processors = line_processors
        self.markers = [p.marker for p in self.line_processors if p.marker]

    def matches_output(self, text):
        """Indicates it text contains sections of interest.
        :param text:    Text to inspect (as string).
        :return: True, if text contains Traceback sections. False, otherwise.
        """
        if self.markers:
            for marker in self.markers:
                if marker in text:
                    return True
        # -- OTHERWISE:
        return False

    def process_output(self, text):
        """Normalizes multi-line text by applying the line processors.

        :param text:    Text to process (as string).
        :return: Tuple (changed : bool, new_text : string)
        """
        new_lines = []
        changed = False
        for line_processor in self.line_processors:
            line_processor.reset()

        for line in text.splitlines():
            # -- LINE PROCESSING PIPELINE:
            original_line = line
            for line_processor in self.line_processors:
                line = line_processor(line)

            if line != original_line:
                changed = True
            new_lines.append(line)

        if changed:
            text = "\n".join(new_lines) + "\n"
        return changed, text

class TextProcessor(CommandOutputProcessor):
    """Provides an adapter that uses an :class:`CommandOutputProcessor`
    as text processor (normalizer).
    """

    def __init__(self, command_output_processor):
        self.command_output_processor = command_output_processor
        self.enabled = self.command_output_processor.enabled
        self.output_parts = self.command_output_processor.output_parts

    def process_output(self, text):
        return self.command_output_processor.process_output(text)

    def __call__(self, command_result):
        if isinstance(command_result, string_types):
            text = command_result
            return self.command_output_processor.process_output(text)[1]
        else:
            return self.command_output_processor(command_result)


class BehaveWinCommandOutputProcessor(LineCommandOutputProcessor):
    """Command output post-processor for :mod:`behave` on Windows platform.
    Mostly, normalizes windows paths in output and exceptions to conform to
    POSIX path conventions.
    """
    enabled = sys.platform.startswith("win") or True
    line_processors = [
        TracebackLineNormalizer(),
        ExceptionWithPathNormalizer(
            "ConfigError: No steps directory in '(?P<path>.*)'",
            "ConfigError: No steps directory in"),
        ExceptionWithPathNormalizer(
            'ParserError: Failed to parse "(?P<path>.*)"',
            "ParserError: Failed to parse"),
        ExceptionWithPathNormalizer(
            "No such file or directory: '(?P<path>.*)'",
            "[Errno 2] No such file or directory:"),  # IOError
        ExceptionWithPathNormalizer(
            '^\s*File "(?P<path>.*)", line \d+, in ',
            'File "'),
    ]
