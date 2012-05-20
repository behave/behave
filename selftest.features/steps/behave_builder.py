# -*- coding: utf-8 -*-
"""
Provide a behave shell to simplify creation of feature files
and running features, etc.

    context.command_result = behave_shell.behave(cmdline, cwd=context.workdir)
    behave_shell.create_scenario(scenario_text, cwd=context.workdir)
    behave_shell.create_step_definition(context.text, cwd=context.workdir)
    context.command_result = behave_shell.run_feature_with_formatter(
            context.features[0], formatter=formatter, cwd=context.workdir)

STATUS: PREPARED, untested.
"""

import command_util
import os.path

scenario_index = 0
step_definition_index = 0

def create_scenario(text, cwd="."):
    """
    Creates a feature file with a scenario.
    """
    global scenario_index
    template = """Feature: Something

        {0}
    """
    contents = template.format(text)
    scenario_index += 1
    feature_name = "scenario_{0}.feature".format(scenario_index)
    filename = os.path.abspath(os.path.join(cwd, feature_name))
    command_util.create_textfile_with_contents(filename, contents)
    return filename

def create_step_definition(text, cwd="."):
    """
    Create a step definition file from its text.
    """
    global step_definition_index
    template = """
    from behave import given, when, then

    {0}
    """
    contents = template.format(text)

    step_definition_index += 1
    dirname = os.path.normpath(os.path.join(cwd, "features", "steps"))
    step_filename = "step_{0}.py".format(step_definition_index)
    filename = os.path.abspath(os.path.join(dirname, step_filename))
    command_util.create_textfile_with_contents(filename, contents)
    return filename

