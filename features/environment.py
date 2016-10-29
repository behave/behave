# -*- coding: UTF-8 -*-

from behave.tag_matcher import ActiveTagMatcher, setup_active_tag_values
from behave4cmd0.setup_command_shell import setup_command_shell_processors4behave
import platform
import sys
import six

# -- MATCHES ANY TAGS: @use.with_{category}={value}
# NOTE: active_tag_value_provider provides category values for active tags.
python_version = "%s.%s" % sys.version_info[:2]
active_tag_value_provider = {
    "python2": str(six.PY2).lower(),
    "python3": str(six.PY3).lower(),
    "python.version": python_version,
    # -- python.implementation: cpython, pypy, jython, ironpython
    "python.implementation": platform.python_implementation().lower(),
    "pypy":    str("__pypy__" in sys.modules).lower(),
    "os":      sys.platform,
}
active_tag_matcher = ActiveTagMatcher(active_tag_value_provider)

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
