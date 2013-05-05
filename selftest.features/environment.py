# -*- coding: UTF-8 -*-
"""
before_step(context, step), after_step(context, step)
    These run before and after every step.
    The step passed in is an instance of Step.

before_scenario(context, scenario), after_scenario(context, scenario)
    These run before and after each scenario is run.
    The scenario passed in is an instance of Scenario.

before_feature(context, feature), after_feature(context, feature)
    These run before and after each feature file is exercised.
    The feature passed in is an instance of Feature.

before_tag(context, tag), after_tag(context, tag)

"""

import logging
import os.path
import shutil

def before_all(context):
    if not context.config.log_capture:
        logging.basicConfig(level=logging.DEBUG)

def after_all(context):
    # TEMPORARILY-DISABLED: print "SUMMARY:"
    pass

#def before_feature(context, feature):
#    context.workdir = None
#
#def after_feature(context, feature):
#    # destroy_workdir(context.workdir)
#    context.workdir = None
#
#def destroy_workdir(workdir):
#    if workdir and os.path.exists(workdir):
#        shutil.rmtree(workdir, ignore_errors=True)

