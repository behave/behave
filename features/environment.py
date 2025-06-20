# -*- coding: UTF-8 -*-
# FILE: features/environment.py

from __future__ import absolute_import, print_function
from behave4cmd0.setup_command_shell import setup_command_shell_processors4behave
from behave import fixture
import behave.active_tag.python
import behave.active_tag.python_feature
from behave.fixture import use_fixture_by_tag
from behave.tag_matcher import \
    ActiveTagMatcher, setup_active_tag_values, print_active_tags

# -----------------------------------------------------------------------------
# ACTIVE TAGS:
# -----------------------------------------------------------------------------
# -- MATCHES ANY TAGS: @use.with_{category}={value}
# NOTE: active_tag_value_provider provides category values for active tags.
active_tag_value_provider = {}
active_tag_value_provider.update(behave.active_tag.python.ACTIVE_TAG_VALUE_PROVIDER)
active_tag_value_provider.update(behave.active_tag.python_feature.ACTIVE_TAG_VALUE_PROVIDER)
active_tag_matcher = ActiveTagMatcher(active_tag_value_provider)


def print_active_tags_summary():
    print_active_tags(active_tag_value_provider, ["python.version", "os"])


# -----------------------------------------------------------------------------
# FIXTURES:
# -----------------------------------------------------------------------------
@fixture(name="fixture.behave.no_background")
def behave_no_background(ctx):
    # -- SETUP-PART-ONLY: Disable background inheritance (for scenarios only).
    current_scenario = ctx.scenario
    if current_scenario:
        print("FIXTURE-HINT: DISABLE-BACKGROUND FOR: %s" % current_scenario.name)
        current_scenario.use_background = False


@fixture(name="fixture.behave.rule.override_background")
def behave_disable_background_inheritance(ctx):
    # -- SETUP-PART-ONLY: Disable background inheritance (for scenarios only).
    current_rule = getattr(ctx, "rule", None)
    if current_rule and current_rule.background:
        # DISABLED: print("DISABLE-BACKGROUND-INHERITANCE FOR RULE: %s" % current_rule.name)
        current_rule.background.use_inheritance = False


fixture_registry = {
    "fixture.behave.no_background": behave_no_background,
    "fixture.behave.override_background": behave_disable_background_inheritance,
}


# -----------------------------------------------------------------------------
# HOOKS:
# -----------------------------------------------------------------------------
def before_all(ctx):
    # -- SETUP ACTIVE-TAG MATCHER (with userdata):
    # USE: behave -D browser=safari ...
    setup_active_tag_values(active_tag_value_provider, ctx.config.userdata)
    setup_python_path()
    setup_context_with_global_params_test(ctx)
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


def before_tag(ctx, tag):
    if tag.startswith("fixture."):
        return use_fixture_by_tag(tag, ctx, fixture_registry)


# -----------------------------------------------------------------------------
# SPECIFIC FUNCTIONALITY:
# -----------------------------------------------------------------------------
def setup_context_with_global_params_test(ctx):
    ctx.global_name = "env:Alice"
    ctx.global_age = 12


def setup_python_path():
    # -- NEEDED-FOR: formatter.user_defined.feature
    import os
    PYTHONPATH = os.environ.get("PYTHONPATH", "")
    os.environ["PYTHONPATH"] = "." + os.pathsep + PYTHONPATH
