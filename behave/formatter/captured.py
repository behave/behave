"""
Experimental formatter to inspect captured output.
"""

from __future__ import absolute_import, print_function
from .base2 import BaseFormatter2

# -- PREPARED:
# import sys
# _PYTHON_VERSION = sys.version_info[:2]
# if _PYTHON_VERSION < (3, 6):
#    # -- REQUIRED-BY: f-strings
#    raise ImportError("REQUIRES: Python >= 3.6")


# -----------------------------------------------------------------------------
# FORMATTER CLASSES:
# -----------------------------------------------------------------------------
class CapturedFormatter(BaseFormatter2):
    """Inspect captured output in Features/Rules/Scenarios/Steps."""
    name = "captured"
    description = "Inspect captured output."

    SHOW_CAPTURED_ON_SUCCESS = True
    SHOW_STEPS_ALWAYS = False

    def __init__(self, stream_opener, config):
        super(CapturedFormatter, self).__init__(stream_opener, config)
        self.show_on_success = self.SHOW_CAPTURED_ON_SUCCESS
        self.prefix = ""
        self.indent_level = 0

    def reset_indent_level(self):
        self.indent_level = 0
        self.prefix = ""

    def increment_indent_level(self):
        self.indent_level += 1
        self.prefix = "  " * self.indent_level

    def decrement_indent_level(self):
        if self.indent_level > 0:
            self.indent_level -= 1
            self.prefix = "  " * self.indent_level

    # -- INTERFACE FOR: IFormatter2
    def on_file_end(self, path):
        self.reset_indent_level()

    def on_feature_start(self, this_feature):
        self.print_statement(this_feature, "ON_START")
        self.print_captured(this_feature.captured, this_feature, "ON_START")
        self.increment_indent_level()

    def on_feature_end(self, this_feature):
        self.decrement_indent_level()
        self.print_statement(this_feature, "ON_END")
        self.print_captured(this_feature.captured, this_feature, "ON_END")

    def on_rule_start(self, this_rule):
        self.print_statement(this_rule, "ON_START")
        self.print_captured(this_rule.captured, this_rule, "ON_START.2")
        self.increment_indent_level()

    def on_rule_end(self, this_rule):
        self.decrement_indent_level()
        self.print_statement(this_rule, "ON_END")
        self.print_captured(this_rule.captured, this_rule, "ON_END.2")

    def on_scenario_start(self, this_scenario):
        # AVOID: self.on_step_end(self.current_step)
        self.print_statement(this_scenario, "ON_START")
        self.print_captured(this_scenario.captured, this_scenario, "ON_START.2")
        self.increment_indent_level()

    def on_scenario_end(self, this_scenario):
        # AVOID: self.on_step_end(self.current_step)
        self.decrement_indent_level()
        self.print_statement(this_scenario, "ON_END")
        self.print_captured(this_scenario.captured, this_scenario, "ON_END.2")

    def on_step_start(self, this_step):
        if this_step.captured.has_output() or self.SHOW_STEPS_ALWAYS:
            self.print_statement(this_step, "ON_START")
        self.print_captured(this_step.captured, this_step, "ON_START")

    def on_step_end(self, this_step):
        if this_step.captured.has_output() or self.SHOW_STEPS_ALWAYS:
            self.print_statement(this_step, "ON_END")
        self.print_captured(this_step.captured, this_step, "ON_END")


    # -- SPECIFIC PARTS:
    def print_statement(self, statement, position=None, show_status=False):
        if statement is None:
            return

        this_type = statement.__class__.__name__
        location = statement.location
        statement_name = statement.name
        if this_type == "Step":
            # PREPARED; statement_name = f"{statement.step_type.title()} {statement.name}"
            statement_name = "{statement.step_type.title()} {statement.name}".format(
                statement=statement
            )
        annotation = ""
        if position:
            # PREPARED: annotation = " -- {position}: {statement.status.name}"
            annotation = " -- {position}: {statement.status.name}".format(
                position=position, statement=statement
            )
        elif show_status:
            # PREPARED: annotation = f" -- status={statement.status.name}"
            annotation = " -- status={statement.status.name}".format(
                statement=statement
            )

        prefix = self.prefix
        # -- PREPARED:
        # print(f"{prefix}{this_type}: {statement_name} {annotation}", file=self.stream)
        # print(f"{prefix}Location: {location}", file=self.stream)
        print("{prefix}{this_type}: {statement_name} {annotation}".format(
              prefix=prefix, this_type=this_type,
              statement_name=statement_name, annotation=annotation),
              file=self.stream)
        print("{prefix}Location: {location}".format(
              prefix=prefix, location=location),
              file=self.stream)
        print("", file=self.stream)

    def make_capture_report(self, captured, show_on_success=None):
        if show_on_success is None:
            show_on_success = self.show_on_success

        template = """
____CAPTURED: {this.status} _______________________
{output}
____CAPTURED_END________________________________
""".strip()
        part_template = "{output}"
        captured_view = captured.select_by_status(show_on_success)
        report = captured_view.make_report(template=template, part_template=part_template)
        return report

    def print_captured(self, captured, statement=None, position=None):
        if not captured.has_output():
            return

        report = self.make_capture_report(captured, show_on_success=self.show_on_success)
        if report:
            # DISABLED: self.print_statement(statement, position)
            print(report, file=self.stream)
            print("", file=self.stream)

    def print_captured_if(self, captured, statement=None, position=None):
        if captured.has_output():
            self.print_captured(captured, statement, position)
