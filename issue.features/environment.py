# -*- coding: UTF-8 -*-
# FILE: features/environment.py
# pylint: disable=unused-argument
"""
Functionality:

  * active tags
"""

from __future__ import print_function
import sys
import platform
import os.path
import six
from behave.tag_matcher import ActiveTagMatcher
from behave4cmd0.setup_command_shell import setup_command_shell_processors4behave
# PREPARED:
# from behave.tag_matcher import setup_active_tag_values


def require_tool(tool_name):
    """Check if a tool (an executable program) is provided on this platform.

    :params tool_name:  Name of the tool to check if it is available.
    :return: True, if tool is found.
    :return: False, if tool is not available (or not in search path).
    """
    # print("CHECK-TOOL: %s" % tool_name)
    path = os.environ.get("PATH")
    if not path:
        return False

    for searchdir in path.split(os.pathsep):
        executable1 = os.path.normpath(os.path.join(searchdir, tool_name))
        executables = [executable1]
        if sys.platform.startswith("win"):
            executables.append(executable1 + ".exe")

        for executable in executables:
            # print("TOOL-CHECK: %s" % os.path.abspath(executable))
            if os.path.isfile(executable):
                # print("TOOL-FOUND: %s" % os.path.abspath(executable))
                return True
    # -- OTHERWISE: Tool not found
    # print("TOOL-NOT-FOUND: %s" % tool_name)
    return False

def as_bool_string(value):
    if bool(value):
        return "yes"
    else:
        return "no"

def discover_ci_server():
    # pylint: disable=invalid-name
    ci_server = "none"
    CI = os.environ.get("CI", "false").lower() == "true"
    APPVEYOR = os.environ.get("APPVEYOR", "false").lower() == "true"
    TRAVIS = os.environ.get("TRAVIS", "false").lower() == "true"
    if CI:
        if APPVEYOR:
            ci_server = "appveyor"
        elif TRAVIS:
            ci_server = "travis"
        else:
            ci_server = "unknown"
    return ci_server


# -- MATCHES ANY TAGS: @use.with_{category}={value}
# NOTE: active_tag_value_provider provides category values for active tags.
active_tag_value_provider = {
    "python2": str(six.PY2).lower(),
    "python3": str(six.PY3).lower(),
    # -- python.implementation: cpython, pypy, jython, ironpython
    "python.implementation": platform.python_implementation().lower(),
    "pypy":    str("__pypy__" in sys.modules).lower(),
    "os":      sys.platform,
    "xmllint": as_bool_string(require_tool("xmllint")),
    "ci": discover_ci_server()
}
active_tag_matcher = ActiveTagMatcher(active_tag_value_provider)

def before_all(context):
    # -- SETUP ACTIVE-TAG MATCHER (with userdata):
    # USE: behave -D browser=safari ...
    # NOT-NEEDED: setup_active_tag_values(active_tag_value_provider,
    #                                     context.config.userdata)
    setup_command_shell_processors4behave()

def before_feature(context, feature):
    if active_tag_matcher.should_exclude_with(feature.tags):
        feature.skip(reason=active_tag_matcher.exclude_reason)

def before_scenario(context, scenario):
    if active_tag_matcher.should_exclude_with(scenario.effective_tags):
        scenario.skip(reason=active_tag_matcher.exclude_reason)
