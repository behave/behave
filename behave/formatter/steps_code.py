# -*- coding: UTF-8 -*-
"""
Provides a formatter, like the "plain" formatter, that:

* Shows the step (and its result)
* Shows the step implementation (as code section)
"""

from __future__ import absolute_import, print_function
import inspect
import sys

from behave.model_describe import ModelPrinter
from behave.model_type import Status
from behave.textutil import indent, make_indentation
from behave.step_registry import registry as the_step_registry
from .plain import PlainFormatter


class StepModelPrinter(ModelPrinter):
    INDENT_SIZE = 2
    SHOW_ALIGNED_KEYWORDS = False
    SHOW_MULTILINE = True
    SHOW_SKIPPED_CODE = False

    def __init__(self, stream=None, indent_size=None, step_indent_level=0,
                 show_aligned_keywords=None, show_multiline=None,
                 step_registry=None):
        if stream is None:
            stream = sys.stdout
        if indent_size is None:
            indent_size = self.INDENT_SIZE
        super(StepModelPrinter, self).__init__(stream)
        self.indent_size = indent_size
        self.step_indent_level = step_indent_level
        self.show_aligned_keywords = show_aligned_keywords or self.SHOW_ALIGNED_KEYWORDS
        self.show_multiline = show_multiline or self.SHOW_MULTILINE
        self.step_registry = step_registry or the_step_registry

    def _print_step_with_schema(self, step, schema, in_rule=False):
        step_indent_level = self.step_indent_level
        if in_rule:
            step_indent_level += 1

        prefix = make_indentation(self.indent_size * step_indent_level)
        text = schema.format(prefix=prefix, step=step)
        print(text, file=self.stream)
        has_multiline = bool(step.text or step.table)
        if self.show_multiline and has_multiline:
            prefix += " " * self.indent_size
            if step.table:
                self.print_table(step.table, indentation=prefix)
            elif step.text:
                self.print_docstring(step.text, indentation=prefix)

    def print_step(self, step, in_rule=False):
        schema = u"{prefix}{step.keyword} {step.name}"
        if self.show_aligned_keywords:
            schema = u"{prefix}{step.keyword:6s} {step.name}"
        self._print_step_with_schema(step, schema, in_rule=in_rule)

    def print_step_with_result(self, step, in_rule=False):
        schema = u"{prefix}{step.keyword} {step.name}  ...  {step.status.name}"
        if self.show_aligned_keywords:
            schema = u"{prefix}{step.keyword:6s} {step.name}  ...  {step.status.name}"
        self._print_step_with_schema(step, schema, in_rule=in_rule)

    @classmethod
    def get_code_without_docstring(cls, func):
        func_code = inspect.getsource(func)
        show_skipped_code = cls.SHOW_SKIPPED_CODE
        if func.__doc__:
            # -- STRIP: function-docstring
            selected = []
            docstring_markers = ['"""',  "'''"]
            docstring_marker = None
            inside_docstring = False
            docstring_done = False
            for line in func_code.splitlines():
                text = line.strip()
                if not docstring_done:
                    if inside_docstring:
                        if text.startswith(docstring_marker):
                            inside_docstring = False
                            docstring_done = True
                        if show_skipped_code:
                            print("SKIP-CODE-LINE: {}".format(line))
                        continue

                    for this_marker in docstring_markers:
                        if text.startswith(this_marker):
                            docstring_marker = this_marker
                            inside_docstring = True
                            break

                    if inside_docstring:
                        if text.endswith(docstring_marker) and text != docstring_marker:
                            # -- CASE: One line docstring, like: """One line."""
                            inside_docstring = False
                            docstring_done = True
                        if show_skipped_code:
                            print("SKIP-CODE-LINE: {}".format(line))
                        continue
                selected.append(line)
            func_code = "\n".join(selected)
        return func_code

    def print_step_code(self, step, in_rule=False):
        step_match = self.step_registry.find_match(step)
        if not step_match:
            return

        step_indent_level = self.step_indent_level
        if in_rule:
            step_indent_level += 1

        code_indent_level = step_indent_level + 1
        prefix = make_indentation(self.indent_size * code_indent_level)
        # DISABLED: step_code = inspect.getsource(step_match.func)
        step_code = self.get_code_without_docstring(step_match.func)
        print("{prefix}# -- CODE: {step_match.location}".format(
            step_match=step_match, prefix=prefix),
            file=self.stream)

        code_text = indent(step_code, prefix=prefix)
        print(code_text, file=self.stream)


class StepWithCodeFormatter(PlainFormatter):
    """
    Provides a formatter, like the "plain" formatter, that:

    * Shows the step (and its result)
    * Shows the step implementation (as code section)
    """
    name = "steps.code"
    description = "Shows executed steps combined with their code."

    def __init__(self, stream_opener, config, **kwargs):
        super(StepWithCodeFormatter, self).__init__(stream_opener, config, **kwargs)
        self.printer = StepModelPrinter(self.stream, step_indent_level=2)
        # PREPARED: self.suppress_duplicated_code = False

    # -- IMPLEMENT-INTERFACE FOR: Formatter
    def result(self, step):
        self.print_step(step)

    # -- INTERNALS:
    def print_step(self, step):
        contained_in_rule = bool(self.current_rule)
        print_step = self.printer.print_step_with_result
        if step.status is Status.untested:
            print_step = self.printer.print_step
        print_step(step, in_rule=contained_in_rule)
        self.printer.print_step_code(step, in_rule=contained_in_rule)


