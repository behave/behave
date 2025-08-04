# -*- coding: UTF-8 -*-
# FILE: issue.features/environment.py
# pylint: disable=unused-argument
"""
Functionality:

  * active tags
"""


from __future__ import absolute_import, print_function
import sys
import os.path
from behave.active_tag.python import \
    ACTIVE_TAG_VALUE_PROVIDER as ACTIVE_TAG_VALUE_PROVIDER4PYTHON
from behave.tag_matcher import ActiveTagMatcher, print_active_tags
from behave4cmd0.setup_command_shell import setup_command_shell_processors4behave


# ---------------------------------------------------------------------------
# TEST SUPPORT: For Active Tags
# ---------------------------------------------------------------------------
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
    GITHUB_ACTIONS = os.environ.get("GITHUB_ACTIONS", "false").lower() == "true"
    APPVEYOR = os.environ.get("APPVEYOR", "false").lower() == "true"
    if CI:
        if GITHUB_ACTIONS:
            ci_server = "github-actions"
        elif APPVEYOR:
            ci_server = "appveyor"
        else:
            ci_server = "unknown"
    return ci_server


# ---------------------------------------------------------------------------
# BEHAVE SUPPORT: Active Tags
# ---------------------------------------------------------------------------
# -- MATCHES ANY TAGS: @use.with_{category}={value}
# NOTE: active_tag_value_provider provides category values for active tags.
python_version = "%s.%s" % sys.version_info[:2]
active_tag_value_provider = {
    "xmllint": as_bool_string(require_tool("xmllint")),
    "ci": discover_ci_server()
}
active_tag_value_provider.update(ACTIVE_TAG_VALUE_PROVIDER4PYTHON)
active_tag_matcher = ActiveTagMatcher(active_tag_value_provider)


def print_active_tags_summary():
    print_active_tags(active_tag_value_provider, [
        "python.version", "python.implementation", "os"
    ])


# ---------------------------------------------------------------------------
# BEHAVE HOOKS:
# ---------------------------------------------------------------------------
def before_all(ctx):
    # -- SETUP ACTIVE-TAG MATCHER (with userdata):
    # USE: behave -D browser=safari ...
    # NOT-NEEDED:
    # setup_active_tag_values(active_tag_value_provider, ctx.config.userdata)
    setup_command_shell_processors4behave()
    print_active_tags_summary()


def before_feature(ctx, feature):
    if active_tag_matcher.should_skip(feature):
        feature.skip(reason=active_tag_matcher.skip_reason)

def before_rule(ctx, rule):
    if active_tag_matcher.should_skip(rule):
        rule.skip(reason=active_tag_matcher.skip_reason)

def before_scenario(ctx, scenario):
    if active_tag_matcher.should_skip(scenario):
        scenario.skip(reason=active_tag_matcher.skip_reason)
