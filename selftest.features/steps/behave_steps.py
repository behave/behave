# -*- coding -*-
"""
Provides step definitions to run behave functionality in feature files.
"""

from __future__ import absolute_import, print_function
from behave import given, when, then
import behave_builder
import command_shell
import command_util
import shutil


# -----------------------------------------------------------------------------
# STEPS
# -----------------------------------------------------------------------------
@given(u'a directory without standard behave project directory structure')
def step_a_directory_without_standard_directory_structure(context):
    # Given /^a directory without standard Cucumber project directory structure$/ do
    # in_current_dir do
    # FileUtils.rm_rf 'features' if File.directory?('features')
    # end
    # end
    command_util.ensure_workdir_exists(context)
    shutil.rmtree(context.workdir, ignore_errors=True)

@given(u'a scenario with a step that looks like this:')
def step_a_scenario_with_a_step_that_looks_like_this(context):
    # Given /^a scenario with a step that looks like this:$/ do |string|
    #                                                   create_feature do
    # create_scenario { string }
    # end
    # end
    command_util.ensure_workdir_exists(context)
    scenario_text = context.text
    filename = behave_builder.create_scenario(scenario_text, cwd=context.workdir)
    command_util.ensure_context_resource_exists(context, "features", [])
    context.features.append(filename)

@given(u'a step definition that looks like this')
def step_a_step_definition_that_looks_like_this(context):
    # Given /^a step definition that looks like this:$/ do |string|
    #                                     create_step_definition { string }
    # end
    command_util.ensure_workdir_exists(context)
    behave_builder.create_step_definition(context.text, cwd=context.workdir)

@when('I run the feature with the "{formatter}" formatter:')
def step_I_run_the_feature_with_the_formatter(context, formatter):
    # When /^I run the feature with the (\w+) formatter$/ do |formatter|
    #                                                features.length.should == 1
    # run_feature features.first, formatter
    # end
    command_util.ensure_workdir_exists(context)
    command_util.ensure_context_resource_exists(context, "features", [])
    command = "behave --format={0} {1}".format(formatter, context.features[0])
    context.command_result = command_shell.run(command, cwd=context.workdir)

