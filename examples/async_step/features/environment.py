# -*- coding: UTF-8 -*-

from behave.tag_matcher import ActiveTagMatcher, setup_active_tag_values
from behave.api.runtime_constraint import require_min_python_version
from behave.active_tag import python_feature

# -----------------------------------------------------------------------------
# REQUIRE: python >= 3.5
# -----------------------------------------------------------------------------
require_min_python_version("3.5")


# -----------------------------------------------------------------------------
# SUPPORT: Active-tags
# -----------------------------------------------------------------------------
# -- MATCHES ANY TAGS: @use.with_{category}={value}
# NOTE: active_tag_value_provider provides category values for active tags.
active_tag_value_provider = {}
active_tag_value_provider.update(python_feature.ACTIVE_TAG_VALUE_PROVIDER)
active_tag_matcher = ActiveTagMatcher(active_tag_value_provider)


# -----------------------------------------------------------------------------
# HOOKS:
# -----------------------------------------------------------------------------
def before_all(ctx):
    # -- SETUP ACTIVE-TAG MATCHER (with userdata):
    setup_active_tag_values(active_tag_value_provider, ctx.config.userdata)


def before_feature(ctx, feature):
    if active_tag_matcher.should_skip(feature):
        feature.skip(reason=active_tag_matcher.skip_reason)

def before_rule(ctx, rule):
    if active_tag_matcher.should_skip(rule):
        rule.skip(reason=active_tag_matcher.skip_reason)

def before_scenario(ctx, scenario):
    if active_tag_matcher.should_skip(scenario):
        scenario.skip(reason=active_tag_matcher.skip_reason)

