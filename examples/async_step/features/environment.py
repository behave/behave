# -*- coding: UTF-8 -*-

from behave.tag_matcher import ActiveTagMatcher, setup_active_tag_values
from behave.api.runtime_constraint import require_min_python_version
from behave import python_feature


# -----------------------------------------------------------------------------
# REQUIRE: python >= 3.4
# -----------------------------------------------------------------------------
require_min_python_version("3.4")


# -----------------------------------------------------------------------------
# SUPPORT: Active-tags
# -----------------------------------------------------------------------------
# -- MATCHES ANY TAGS: @use.with_{category}={value}
# NOTE: active_tag_value_provider provides category values for active tags.
active_tag_value_provider = python_feature.ACTIVE_TAG_VALUE_PROVIDER.copy()
active_tag_matcher = ActiveTagMatcher(active_tag_value_provider)


# -----------------------------------------------------------------------------
# HOOKS:
# -----------------------------------------------------------------------------
def before_all(ctx):
    # -- SETUP ACTIVE-TAG MATCHER (with userdata):
    setup_active_tag_values(active_tag_value_provider, ctx.config.userdata)


def before_feature(ctx, feature):
    if active_tag_matcher.should_exclude_with(feature.tags):
        feature.skip(reason=active_tag_matcher.exclude_reason)


def before_scenario(ctx, scenario):
    if active_tag_matcher.should_exclude_with(scenario.effective_tags):
        scenario.skip(reason=active_tag_matcher.exclude_reason)

