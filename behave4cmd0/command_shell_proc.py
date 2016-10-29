#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This module provides pre-/post-processors for the mod:`behave4cmd0.command_shell`.
"""

from __future__ import absolute_import, print_function
import re
import sys

# -----------------------------------------------------------------------------
# UTILITY:
# -----------------------------------------------------------------------------
def posixpath_normpath(filename):
    return filename.replace("\\", "/")

# -----------------------------------------------------------------------------
# FUNCTIONALITY
# -----------------------------------------------------------------------------
class CommandPostProcessor(object): pass
class CommandOutputProcessor(CommandPostProcessor): pass

class TracebackNormalizer(CommandOutputProcessor):
    """Normalize paths in traceback output to use POSIX path style.
    Therefore, it replace backslashes with slashes: '\' => '/'
    in stderr output.
    """
    # XXX cells = [cell.replace("\\|", "|").strip()
    # XXX for cell in re.split(r"(?<!\\)\|", line[1:-1])]
    file_pattern = re.compile(r'\s\s+File "(?P<filename>.*)", line .*')
    marker = "Traceback (most recent call last):\n"
    enabled = sys.platform.startswith("win")
    output_parts = ("stderr", "stdout")

    def __init__(self, enabled=None):
        if enabled is None:
            # -- AUTO-DETECT: Enabled on Windows platform
            enabled = self.__class__.enabled
        self.enabled = enabled

    def matches_output(self, text):
        """Indicates it text contains sections of interest (Traceback sections).
        :param text:    Text to inspect (as string).
        :return: True, if text contains Traceback sections. False, otherwise.
        """
        return self.marker in text

    @classmethod
    def normalize_traceback_paths(cls, text):
        """Normalizes File "..." parts in traceback section to use posix-path
        naming conventions (replace: backslashes with slashes).

        TRACEBACK-OUTPUT EXAMPLE::

            Traceback (most recent call last):
              File "tests/xplore_traceback.py", line 27, in <module>
                sys.exit(main())
              ...
              File "tests/xplore_traceback.py", line 12, in f
                return x/0
            ZeroDivisionError: integer division or modulo by zero

        :param text:    Text to process (as string).
        :return: Tuple (changed : bool, new_text : string)
        """
        marker = cls.marker.strip()
        new_lines = []
        traceback_section = False
        changes = 0
        for line in text.splitlines():
            stripped_line = line.strip()
            if marker == stripped_line:
                assert not traceback_section
                traceback_section = True
                # print("XXX: TRACEBACK-START")
            elif traceback_section:
                matched = cls.file_pattern.match(line)
                if matched:
                    # matched_range = matched.regs[1]
                    filename = matched.groups()[0]
                    new_filename = posixpath_normpath(filename)
                    if new_filename != filename:
                        # print("XXX: %r => %r" % (filename, new_filename))
                        line = line.replace(filename, new_filename)
                        changes += 1
                elif not line.strip() or line[0].isalpha():
                    # -- DETECTED TRCAEBACK-END: exception-description
                    # print("XXX: TRACEBACK-END")
                    traceback_section = False
            new_lines.append(line)

        if changes:
            text = "\n".join(new_lines) + "\n"
        return (bool(changes), text)

    def process_output(self, command_result):
        """Normalizes stderr output of command result.

        EXAMPLE: Traceback output
        .. sourcecode:: python
            Traceback (most recent call last):
              File "tests/xplore_traceback.py", line 27, in <module>
                sys.exit(main())
              ...
              File "tests/xplore_traceback.py", line 12, in f
                return x/0
            ZeroDivisionError: integer division or modulo by zero
        """
        changes = 0
        for output_name in self.output_parts:
            text = getattr(command_result, output_name)
            if text and self.matches_output(text):
                changed, new_text = self.normalize_traceback_paths(text)
                if changed:
                    changes += 1
                    setattr(command_result, output_name, new_text)
        if changes:
            # -- RESET: Composite output
            command_result._output = None
        return command_result

    def __call__(self, command_result):
        if (not self.enabled or not command_result.stderr or
            not self.matches_output(command_result.stderr)):
            return command_result
        return self.process_output(command_result)
