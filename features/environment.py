# -*- coding: UTF-8 -*-
# FILE: features/environemnt.py

from __future__ import absolute_import, print_function
from behave.tag_matcher import \
    ActiveTagMatcher, setup_active_tag_values, print_active_tags
from behave4cmd0.setup_command_shell import setup_command_shell_processors4behave
from behave import python_feature
import platform
import sys


# -- MATCHES ANY TAGS: @use.with_{category}={value}
# NOTE: active_tag_value_provider provides category values for active tags.
active_tag_value_provider = {
    # -- python.implementation: cpython, pypy, jython, ironpython
    "python.implementation": platform.python_implementation().lower(),
    "pypy":    str("__pypy__" in sys.modules).lower(),
}
active_tag_value_provider.update(python_feature.ACTIVE_TAG_VALUE_PROVIDER)
active_tag_matcher = ActiveTagMatcher(active_tag_value_provider)


def print_active_tags_summary():
    print_active_tags(active_tag_value_provider, ["python.version", "os"])


# -----------------------------------------------------------------------------
# HOOKS:
# -----------------------------------------------------------------------------
def before_all(context):
    # -- SETUP ACTIVE-TAG MATCHER (with userdata):
    # USE: behave -D browser=safari ...
    setup_active_tag_values(active_tag_value_provider, context.config.userdata)
    setup_python_path()
    setup_context_with_global_params_test(context)
    setup_command_shell_processors4behave()
    print_active_tags_summary()


def before_feature(context, feature):
    if active_tag_matcher.should_exclude_with(feature.tags):
        feature.skip(reason=active_tag_matcher.exclude_reason)


def before_scenario(context, scenario):
    if active_tag_matcher.should_exclude_with(scenario.effective_tags):
        scenario.skip(reason=active_tag_matcher.exclude_reason)


# -----------------------------------------------------------------------------
# SPECIFIC FUNCTIONALITY:
# -----------------------------------------------------------------------------
def setup_context_with_global_params_test(context):
    context.global_name = "env:Alice"
    context.global_age  = 12

def setup_python_path():
    # -- NEEDED-FOR: formatter.user_defined.feature
    import os
    PYTHONPATH = os.environ.get("PYTHONPATH", "")
    os.environ["PYTHONPATH"] = "."+ os.pathsep + PYTHONPATH
